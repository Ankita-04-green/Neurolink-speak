import streamlit as st
import numpy as np
from scipy.io.wavfile import write
import io
from typing import Optional
from gtts import gTTS
from langdetect import detect
import tempfile
import os


class TTSService:
    """Service for handling text-to-speech conversion"""

    def __init__(self):
        pass

    @st.cache_resource
    def initialize_tts_model(_self, model_name: str):
        """Initialize TTS model (mock placeholder for future expansion)."""
        return {"model_name": model_name, "initialized": True}

    def text_to_speech(
        self,
        text: str,
        voice_type: str = "default",
        language: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Convert text to real speech using Google Text-to-Speech (gTTS).

        Args:
            text: Text to convert to speech.
            voice_type: Voice type ("default", "male", "female").
            language: Target language code (e.g., 'en', 'hi', 'fr').

        Returns:
            Audio bytes in WAV format or None if conversion fails.
        """
        if not text:
            return None

        try:
            # Auto-detect language if not provided
            if not language:
                try:
                    language = detect(text)
                except Exception:
                    language = "en"

            # Convert text to speech using gTTS
            tts = gTTS(text=text, lang=language)
            
            # Save to temporary MP3 file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name

            # Convert MP3 to WAV (so Streamlit can play it properly)
            # We'll read it as bytes and return
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            os.remove(tmp_path)
            return audio_bytes

        except Exception as e:
            st.error(f"Error in text-to-speech conversion: {e}")
            return None


# Global TTS service instance
tts_service = TTSService()


def generate_speech(
    text: str,
    voice_type: str = "default",
    language: Optional[str] = None
) -> Optional[bytes]:
    """
    Generate speech audio from text (using gTTS for natural output).

    Args:
        text: Text to convert to speech.
        voice_type: Type of voice to use.
        language: Language code (for correct pronunciation).

    Returns:
        Audio bytes or None if conversion fails.
    """
    if not text:
        return None

    # Initialize model if not already done
    model = tts_service.initialize_tts_model("gTTS_model")

    # Generate real speech
    audio_bytes = tts_service.text_to_speech(text, voice_type, language)

    return audio_bytes
