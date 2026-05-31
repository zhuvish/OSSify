"""Voice-enabled Digital Twin service using Groq Whisper transcription.

This service handles audio file transcription and delegates to the existing
answer_for_contributor() function for RAG-based responses.

No new retrieval or RAG logic is introduced — all retrieval logic is reused
from expert_retrieval_service.
"""
import logging
import os
from typing import Any, Dict, BinaryIO

from backend.app.services.expert_retrieval_service import answer_for_contributor

logger = logging.getLogger(__name__)


def transcribe_audio_with_groq(audio_file: BinaryIO, filename: str) -> str:
    """Transcribe an audio file using Groq Whisper API.

    Args:
        audio_file: File-like object containing audio data
        filename: Original filename (used for determining file type)

    Returns:
        Transcribed text from the audio

    Raises:
        ValueError: If GROQ_API_KEY is not set
        Exception: If Groq transcription fails
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        logger.info("Transcribing audio file: %s", filename)

        # Use Groq's Whisper transcription
        transcript = client.audio.transcriptions.create(
            file=(filename, audio_file, "audio/mpeg"),  # Groq auto-detects format
            model="whisper-large-v3",
        )

        text = transcript.text if hasattr(transcript, "text") else str(transcript)
        logger.info("Audio transcribed successfully, length: %d chars", len(text))

        return text

    except ImportError:
        raise ImportError(
            "groq package is required for voice chat. Install with: pip install groq"
        )
    except Exception as e:
        logger.exception("Groq transcription failed")
        raise


def voice_chat_with_contributor(
    contributor_id: int,
    audio_file: BinaryIO,
    filename: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Process voice input and return a Digital Twin response.

    Pipeline:
      1. Transcribe audio using Groq Whisper
      2. Extract transcript text
      3. Reuse answer_for_contributor() with transcript
      4. Return enriched response with transcript included

    Args:
        contributor_id: PostgreSQL contributor ID
        audio_file: File-like object containing audio data
        filename: Original filename
        top_k: Number of evidence documents to retrieve (default 5, max 15)

    Returns:
        Dict with keys:
          - contributor_id
          - username
          - transcript (the transcribed text)
          - answer (LLM-generated response)
          - evidence (list of matched documents)
          - grounding_status
          - document_count

    Raises:
        ValueError: If validation fails (empty transcript, invalid contributor)
        Exception: If transcription or RAG fails
    """
    logger.info(
        "Starting voice chat for contributor_id=%d, file=%s", contributor_id, filename
    )

    # Step 1: Transcribe audio
    try:
        transcript = transcribe_audio_with_groq(audio_file, filename)
    except ValueError as e:
        logger.error("Transcription validation error: %s", e)
        raise
    except Exception as e:
        logger.error("Transcription failed: %s", e)
        raise

    # Validate transcript is not empty
    if not transcript.strip():
        raise ValueError("Audio transcription resulted in empty text")

    logger.info("Transcript (first 100 chars): %s", transcript[:100])

    # Step 2: Use existing answer_for_contributor() with transcript
    try:
        result = answer_for_contributor(
            contributor_id=contributor_id,
            question=transcript,
            top_k=top_k,
        )
    except Exception as e:
        logger.error("RAG pipeline failed: %s", e)
        raise

    # Check for contributor not found error
    if "error" in result:
        raise ValueError(result["error"])

    # Step 3: Enrich response with transcript
    result["transcript"] = transcript

    return result
