"""Text-to-Speech using ElevenLabs.

Provides a simple, isolated service to convert text to MP3 audio bytes using the
ElevenLabs API. Reads ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID from environment.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def text_to_speech(text: str, voice_id: Optional[str] = None) -> bytes:
    """Generate MP3 audio bytes for the provided text using ElevenLabs.

    Args:
        text: Text to synthesize (must be non-empty)
        voice_id: Optional voice identifier; if not provided, ELEVENLABS_VOICE_ID env var is used.

    Returns:
        Bytes of MP3 audio

    Raises:
        ValueError: On missing API key, missing text, or empty TTS output
        Exception: On ElevenLabs SDK or API failures
    """
    if not text or not text.strip():
        raise ValueError("Text to synthesize is empty")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    env_voice = os.getenv("ELEVENLABS_VOICE_ID")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY environment variable is not set")

    if not voice_id:
        voice_id = env_voice

    if not voice_id:
        raise ValueError("No voice id provided. Set ELEVENLABS_VOICE_ID or pass voice_id")

    try:
        # Prefer the official elevenlabs SDK when available
        try:
            from elevenlabs import set_api_key, generate

            set_api_key(api_key)
            logger.info("Generating speech using ElevenLabs SDK, voice=%s", voice_id)
            audio = generate(text=text, voice=voice_id, model="eleven_multilingual_v1")
            if not audio:
                raise ValueError("ElevenLabs returned empty audio")
            # many SDKs return bytes-like; ensure bytes
            return bytes(audio)
        except ImportError:
            # Fallback to direct HTTP request if SDK not installed
            import requests

            logger.info("ElevenLabs SDK not installed, falling back to HTTP API")
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json",
            }
            payload = {"text": text, "model": "eleven_multilingual_v1"}
            resp = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
            if resp.status_code != 200:
                logger.error("ElevenLabs API error: %s %s", resp.status_code, resp.text)
                raise Exception(f"ElevenLabs API error: {resp.status_code} - {resp.text}")
            audio_bytes = resp.content
            if not audio_bytes:
                raise ValueError("ElevenLabs returned empty audio")
            return audio_bytes
    except Exception:
        logger.exception("Text-to-speech generation failed")
        raise
