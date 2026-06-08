"""API endpoints for expert discovery, contributor profile, and contributor-grounded RAG.

All retrieval uses LOCAL PostgreSQL contributor IDs (not GitHub IDs).
Qdrant metadata filtering ensures contributor-scoped isolation.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body, UploadFile, File
from fastapi.responses import StreamingResponse
import io
from pydantic import BaseModel, Field

from backend.app.services.expert_retrieval_service import (
    find_experts,
    get_contributor_profile,
    answer_for_contributor,
)
from backend.app.services.voice_chat_service import voice_chat_with_contributor
from backend.app.services.tts_service import generate_speech, TTSException
from backend.app.services.ask_experts_service import ask_experts

logger = logging.getLogger(__name__)
router = APIRouter()

# ──────────────────────────────────────────────
#  Pydantic Schemas
# ──────────────────────────────────────────────


class ExpertiseArea(BaseModel):
    domain: str
    score: float
    evidence_count: Optional[int] = None
    confidence: Optional[float] = None


class ExpertResult(BaseModel):
    contributor_id: int
    username: str
    score: float = Field(..., description="Aggregated relevance score")
    expertise: Optional[str] = Field(None, description="Top expertise domain")
    expertise_areas: List[ExpertiseArea] = Field(default_factory=list)
    matched_documents: int = Field(..., description="Number of semantically matched documents")
    matched_files: List[str] = Field(default_factory=list, description="File paths that matched query tokens")
    confidence: float = Field(..., ge=0.0, le=1.0)


class ExpertSearchResponse(BaseModel):
    query: str
    experts: List[ExpertResult]
    count: int


class AskExpertsRequest(BaseModel):
    question: str = Field(..., description="Natural language question about expert contributors", min_length=1)


class AskExpertsResponse(BaseModel):
    summary: str
    relevant_information: List[str]
    answer: str


class RecentActivity(BaseModel):
    type: str  # "commit" | "pr" | "issue"
    description: str
    date: Optional[str] = None
    sha: Optional[str] = None
    pr_number: Optional[int] = None
    issue_number: Optional[int] = None
    repo_id: Optional[int] = None


class SemanticTerm(BaseModel):
    term: str
    relevance: float


class TopRepository(BaseModel):
    name: str
    stars: int


class ContributorProfileResponse(BaseModel):
    contributor_id: int
    username: str
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    followers: Optional[int] = None
    contributions_count: Optional[int] = None
    expertise_areas: List[ExpertiseArea] = Field(default_factory=list)
    top_repositories: List[TopRepository] = Field(default_factory=list)
    top_files: List[str] = Field(default_factory=list)
    commit_count: int = 0
    pr_count: int = 0
    issue_count: int = 0
    recent_activity: List[RecentActivity] = Field(default_factory=list)
    semantic_expertise_summary: List[SemanticTerm] = Field(default_factory=list)


class EvidenceDocument(BaseModel):
    document_type: str
    content_snippet: str
    score: float
    commit_sha: Optional[str] = None
    pr_number: Optional[int] = None
    issue_number: Optional[int] = None


class ContributorChatRequest(BaseModel):
    message: str = Field(..., description="User question about the contributor's work", min_length=1)


class ContributorChatResponse(BaseModel):
    contributor_id: int
    username: str
    question: str
    answer: str
    evidence: List[EvidenceDocument]
    grounding_status: str
    document_count: int


class ContributorVoiceChatResponse(BaseModel):
    contributor_id: int
    username: str
    transcript: str = Field(..., description="Transcribed text from audio input")
    answer: str
    evidence: List[EvidenceDocument]
    grounding_status: str
    document_count: int


# ──────────────────────────────────────────────
#  1. Expertise API
# ──────────────────────────────────────────────


@router.get("/experts/search", response_model=ExpertSearchResponse)
def search_experts(
    query: str = Query(
        ...,
        min_length=1,
        description="Search query to find experts (e.g., 'authentication', 'routing', 'Flask session bugs')",
    ),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of top experts to return",
    ),
    repo_id: Optional[int] = Query(
        default=None,
        description="Filter experts by repository ID",
    ),
):
    """Search for contributors who are experts in a given topic.

    Uses semantic retrieval from Qdrant with document-type weighting
    (commits > PRs > issues) plus file-path token matching.

    **Example queries:**
    - `"Who is expert in authentication?"`
    - `"Who works most on routing?"`
    - `"Who should review Flask session bugs?"`
    """
    logger.info("Expert search: query=%s top_k=%d", query, top_k)
    try:
        experts = find_experts(query=query, top_k=top_k, repo_id=repo_id)
        return ExpertSearchResponse(query=query, experts=experts, count=len(experts))
    except Exception as exc:
        logger.exception("Expert search failed for query=%s", query)
        raise HTTPException(status_code=500, detail=f"Expert search error: {exc}")



# ──────────────────────────────────────────────
#  3. Contributor Chat API (Digital Twin)
# ──────────────────────────────────────────────


@router.post("/contributors/{contributor_id}/chat", response_model=ContributorChatResponse)
def chat_with_contributor(
    contributor_id: int,
    body: ContributorChatRequest,
    top_k: int = Query(
        default=5,
        ge=1,
        le=15,
        description="Number of evidence documents to retrieve for context",
    ),
):
    """Chat with a contributor's **digital twin**.

    The answer is generated using **ONLY** documents belonging to the specified contributor
    (commits, PRs, issues).  No global retrieval is used, and no other contributor's
    documents are mixed in.

    **Request body:**\n
    ```json
    {"message": "What has this contributor worked on?"}
    ```

    **Guarantees:**
    - Contributor-scoped retrieval (Qdrant filter on `contributor_id`)
    - Evidence always includes the matched document snippets
    - Never returns documents from other contributors
    """
    logger.info("Contributor chat: contributor_id=%d message='%s'", contributor_id, body.message[:80])
    try:
        result = answer_for_contributor(
            contributor_id=contributor_id,
            question=body.message,
            top_k=top_k,
        )

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return ContributorChatResponse(
            contributor_id=result["contributor_id"],
            username=result["username"],
            question=result["question"],
            answer=result["answer"],
            evidence=[EvidenceDocument(**ev) for ev in result["evidence"]],
            grounding_status=result["grounding_status"],
            document_count=result["document_count"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat failed for contributor_id=%d", contributor_id)
        raise HTTPException(status_code=500, detail=f"Chat error: {exc}")


# ──────────────────────────────────────────────
#  4. Contributor Voice Chat API (Voice Digital Twin)
# ──────────────────────────────────────────────


@router.post("/contributors/{contributor_id}/voice-chat", response_model=ContributorVoiceChatResponse)
def voice_chat_with_contributor_endpoint(
    contributor_id: int,
    audio_file: UploadFile = File(..., description="Audio file (MP3, WAV, OGG, FLAC, or M4A)"),
    top_k: int = Query(
        default=5,
        ge=1,
        le=15,
        description="Number of evidence documents to retrieve for context",
    ),
):
    """Chat with a contributor's **digital twin** using voice input.

    This endpoint accepts an audio file, transcribes it using Groq Whisper,
    and then uses the same contributor-scoped RAG pipeline as the text chat endpoint.

    **Multipart Form Data:**
    - `audio_file`: Audio file (required). Supported formats: MP3, WAV, OGG, FLAC, M4A
    - `top_k`: Number of evidence documents (optional, default=5, max=15)

    **Response:**
    - `transcript`: The text transcribed from the audio input
    - `answer`: LLM-generated response based on contributor's documents
    - `evidence`: Matched documents grounding the answer
    - `grounding_status`: "contributor_scoped" or "no_matches"
    - `document_count`: Number of retrieved documents

    **Guarantees:**
    - Contributor-scoped retrieval (Qdrant filter on `contributor_id`)
    - Audio transcription uses Groq Whisper (whisper-large-v3 model)
    - Evidence always includes matched document snippets
    - Never returns documents from other contributors

    **Example curl:**
    ```bash
    curl -X POST "http://localhost:8000/contributors/1/voice-chat" \\
      -F "audio_file=@sample_audio.mp3" \\
      -F "top_k=5"
    ```
    """
    logger.info(
        "Voice chat requested: contributor_id=%d, file=%s, size=%d",
        contributor_id,
        audio_file.filename,
        audio_file.size or 0,
    )

    # Validate file upload
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="Missing audio_file in request")

    if audio_file.size and audio_file.size > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(status_code=413, detail="Audio file too large (max 25 MB)")

    try:
        result = voice_chat_with_contributor(
            contributor_id=contributor_id,
            audio_file=audio_file.file,
            filename=audio_file.filename,
            top_k=top_k,
        )

        return ContributorVoiceChatResponse(
            contributor_id=result["contributor_id"],
            username=result["username"],
            transcript=result["transcript"],
            answer=result["answer"],
            evidence=[EvidenceDocument(**ev) for ev in result["evidence"]],
            grounding_status=result["grounding_status"],
            document_count=result["document_count"],
        )
    except ValueError as e:
        logger.error("Voice chat validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        logger.exception("Voice chat failed for contributor_id=%d", contributor_id)
        raise HTTPException(status_code=500, detail=f"Voice chat error: {exc}")


# ──────────────────────────────────────────────
#  5. Contributor Voice Chat Audio API (TTS Output)
# ──────────────────────────────────────────────


@router.post(
    "/contributors/{contributor_id}/voice-chat-audio",
    responses={
        200: {
            "content": {
                "audio/mpeg": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        }
    },
)
def voice_chat_audio_with_contributor_endpoint(
    contributor_id: int,
    audio_file: UploadFile = File(..., description="Audio file (MP3, WAV, OGG, FLAC, or M4A)"),
    top_k: int = Query(
        default=5,
        ge=1,
        le=15,
        description="Number of evidence documents to retrieve for context",
    ),
):
    """Chat with a contributor's digital twin using voice input and return spoken MP3 audio.

    Pipeline:
    - Accept multipart/form-data audio upload
    - Transcribe using existing Groq Whisper flow
    - Use existing contributor-scoped RAG (answer_for_contributor)
    - Synthesize the LLM answer using ElevenLabs TTS

    Returns raw MP3 audio (Content-Type: audio/mpeg).
    """
    logger.info(
        "Voice chat (audio output) requested: contributor_id=%d, file=%s, size=%d",
        contributor_id,
        audio_file.filename,
        audio_file.size or 0,
    )

    # Validate file upload
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="Missing audio_file in request")

    if audio_file.size and audio_file.size > 25 * 1024 * 1024:  # 25 MB limit
        raise HTTPException(status_code=413, detail="Audio file too large (max 25 MB)")

    try:
        # Reuse existing transcription + RAG logic
        result = voice_chat_with_contributor(
            contributor_id=contributor_id,
            audio_file=audio_file.file,
            filename=audio_file.filename,
            top_k=top_k,
        )

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        answer_text = result.get("answer", "")
        if not answer_text or not answer_text.strip():
            raise HTTPException(status_code=500, detail="LLM returned empty answer text")

        # Synthesize speech using ElevenLabs REST API
        try:
            # If voice_chat_with_contributor already synthesized audio and attached it, prefer that
            audio_bytes = result.get("audio_mp3")
            if not audio_bytes:
                audio_bytes = generate_speech(answer_text)
        except ValueError as e:
            logger.error("TTS validation error: %s", e)
            raise HTTPException(status_code=400, detail=str(e))
        except TTSException as e:
            logger.error("TTS provider error: %s", e)
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            logger.exception("TTS generation failed")
            raise HTTPException(status_code=502, detail=f"Text-to-speech error: {e}")

        if not audio_bytes:
            raise HTTPException(status_code=502, detail="Received empty audio from TTS provider")

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=response.mp3"},
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Voice chat audio validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        logger.exception("Voice chat audio failed for contributor_id=%d", contributor_id)
        raise HTTPException(status_code=500, detail=f"Voice chat audio error: {exc}")


# ──────────────────────────────────────────────
#  6. Expert Q&A API (Ask Question)
# ──────────────────────────────────────────────


@router.post("/experts/ask", response_model=AskExpertsResponse)
def ask_experts_question(
    body: AskExpertsRequest,
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of top experts to consider for the answer",
    ),
):
    """Answer a natural language question about expert contributors.

    This endpoint uses the existing expert retrieval pipeline (find_experts)
    combined with the existing Groq LLM to produce a structured, grounded answer.

    **Request body:**\n
    ```json
    {"question": "Who should review backend API changes?"}
    ```

    **Response:**
    - `summary`: Brief overview of findings
    - `relevant_information`: Specific facts about matched experts
    - `answer`: Final grounded answer

    **Guarantees:**
    - Answer is grounded in retrieved expert data
    - No hallucinated contributors
    - Uses existing find_experts() + Groq LLM infrastructure
    """
    logger.info("Expert Q&A: question='%s' top_k=%d", body.question[:80], top_k)
    try:
        result = ask_experts(question=body.question, top_k=top_k)
        return AskExpertsResponse(
            summary=result["summary"],
            relevant_information=result["relevant_information"],
            answer=result["answer"],
        )
    except Exception as exc:
        logger.exception("Expert Q&A failed for question='%s'", body.question[:80])
        raise HTTPException(status_code=500, detail=f"Expert Q&A error: {exc}")
