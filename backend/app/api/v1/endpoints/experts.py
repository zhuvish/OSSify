"""API endpoints for expert discovery, contributor profile, and contributor-grounded RAG.

All retrieval uses LOCAL PostgreSQL contributor IDs (not GitHub IDs).
Qdrant metadata filtering ensures contributor-scoped isolation.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from backend.app.services.expert_retrieval_service import (
    find_experts,
    get_contributor_profile,
    answer_for_contributor,
)

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
        experts = find_experts(query=query, top_k=top_k)
        return ExpertSearchResponse(query=query, experts=experts, count=len(experts))
    except Exception as exc:
        logger.exception("Expert search failed for query=%s", query)
        raise HTTPException(status_code=500, detail=f"Expert search error: {exc}")


# ──────────────────────────────────────────────
#  2. Contributor Profile API
# ──────────────────────────────────────────────


@router.get("/contributors/{contributor_id}/profile", response_model=ContributorProfileResponse)
def contributor_profile(contributor_id: int):
    """Get a detailed contributor profile with expertise, repositories, files, activity, and semantic summary.

    Data sources:
      - **PostgreSQL**: contributor info, expertise areas, commits/PRs/issues counts, repositories, files
      - **Qdrant**: semantic expertise summary (thematic keywords extracted from vector search)
    """
    logger.info("Contributor profile requested: contributor_id=%d", contributor_id)
    try:
        profile = get_contributor_profile(contributor_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Contributor {contributor_id} not found")
        return ContributorProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Profile fetch failed for contributor_id=%d", contributor_id)
        raise HTTPException(status_code=500, detail=f"Profile error: {exc}")


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