import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AppConfig:
    # Database configuration
    DATABASE_URL: str = "sqlite:///neurolink.db"
    
    # Translation models (MarianMT)
    TRANSLATION_MODELS: Dict[str, str] = None
    
    # TTS models
    TTS_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    
    # ASR models (Whisper)
    ASR_MODEL: str = "openai/whisper-base"
    
    # Supported languages
    SUPPORTED_LANGUAGES: List[str] = None
    
    # Default settings
    DEFAULT_SOURCE_LANGUAGE: str = "en"
    DEFAULT_TARGET_LANGUAGE: str = "es"
    
    def __post_init__(self):
        if self.TRANSLATION_MODELS is None:
            self.TRANSLATION_MODELS = {
                "en-es": "Helsinki-NLP/opus-mt-en-es",
                "es-en": "Helsinki-NLP/opus-mt-es-en",
                "en-fr": "Helsinki-NLP/opus-mt-en-fr",
                "fr-en": "Helsinki-NLP/opus-mt-fr-en",
                "en-de": "Helsinki-NLP/opus-mt-en-de",
                "de-en": "Helsinki-NLP/opus-mt-de-en",
                "en-it": "Helsinki-NLP/opus-mt-en-it",
                "it-en": "Helsinki-NLP/opus-mt-it-en",
                "en-pt": "Helsinki-NLP/opus-mt-en-pt",
                "pt-en": "Helsinki-NLP/opus-mt-pt-en",
                "en-ru": "Helsinki-NLP/opus-mt-en-ru",
                "ru-en": "Helsinki-NLP/opus-mt-ru-en",
                "en-ar": "Helsinki-NLP/opus-mt-en-ar",
                "ar-en": "Helsinki-NLP/opus-mt-ar-en",
                "en-hi": "Helsinki-NLP/opus-mt-en-hi",
                "hi-en": "Helsinki-NLP/opus-mt-hi-en",
                "en-zh": "Helsinki-NLP/opus-mt-en-zh",
                "zh-en": "Helsinki-NLP/opus-mt-zh-en"
            }
            
        if self.SUPPORTED_LANGUAGES is None:
            self.SUPPORTED_LANGUAGES = [
                "en", "es", "fr", "de", "it", 
                "pt", "ru", "ar", "hi", "zh"
            ]

# Global configuration instance
config = AppConfig()
