"""TTS service using ElevenLabs REST API (no SDK).

Provides generate_speech(text: str) -> bytes which calls the ElevenLabs
text-to-speech endpoint and returns raw MP3 bytes.
"""
import io
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

ELEVENLABS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


class TTSException(Exception):
    pass


def generate_speech(text: str, timeout: int = 30) -> bytes:
    """Generate MP3 bytes for the given text via ElevenLabs REST API.

    Args:
        text: Non-empty text to synthesize
        timeout: HTTP timeout in seconds

    Returns:
        bytes: MP3 audio bytes

    Raises:
        ValueError: missing API key, missing voice id, or empty text
        TTSException: on HTTP/API failures
    """
    if not text or not text.strip():
        raise ValueError("Text to synthesize is empty")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
    if not voice_id:
        raise ValueError("ELEVENLABS_VOICE_ID environment variable is not set")

    url = ELEVENLABS_URL_TEMPLATE.format(voice_id=voice_id)
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}

    try:
        logger.info("Calling ElevenLabs TTS API, voice_id=%s, text_length=%d", voice_id, len(text))
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        logger.exception("HTTP request to ElevenLabs failed")
        raise TTSException(f"HTTP error calling ElevenLabs: {e}") from e

    if resp.status_code != 200:
        logger.error(
            "ElevenLabs API returned non-200 status: %s, body=%s",
            resp.status_code,
            resp.text,
        )
        raise TTSException(f"ElevenLabs API error: {resp.status_code} - {resp.text}")

    audio_bytes = resp.content
    if not audio_bytes:
        logger.error("ElevenLabs returned empty audio payload")
        raise TTSException("ElevenLabs returned empty audio payload")

    return audio_bytes
