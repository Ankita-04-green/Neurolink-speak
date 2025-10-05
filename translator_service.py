import streamlit as st
from transformers import MarianMTModel, MarianTokenizer
from config import config
from typing import Dict, Optional
import torch

class TranslatorService:
    """Service for handling multilingual translation using Hugging Face MarianMT models"""
    
    def __init__(self):
        self.models: Dict[str, MarianMTModel] = {}
        self.tokenizers: Dict[str, MarianTokenizer] = {}
        
    @st.cache_resource
    def load_model_and_tokenizer(_self, model_name: str) -> tuple:
        """
        Load and cache a translation model and tokenizer
        
        Args:
            model_name: Name of the Hugging Face model to load
            
        Returns:
            Tuple of (model, tokenizer)
        """
        try:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            return model, tokenizer
        except Exception as e:
            st.error(f"Error loading translation model {model_name}: {e}")
            return None, None
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate text from source language to target language
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if translation fails
        """
        # Create model key
        model_key = f"{source_lang}-{target_lang}"
        
        # Check if we support this language pair
        if model_key not in config.TRANSLATION_MODELS:
            st.warning(f"Translation from {source_lang} to {target_lang} not supported")
            return None
            
        model_name = config.TRANSLATION_MODELS[model_key]
        
        # Load model and tokenizer (cached)
        model, tokenizer = self.load_model_and_tokenizer(model_name)
        
        if model is None or tokenizer is None:
            st.error("Failed to load translation model")
            return None
            
        try:
            # Tokenize the text
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            
            # Generate translation
            with torch.no_grad():
                outputs = model.generate(**inputs)
                
            # Decode the translated text
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return translated_text
        except Exception as e:
            st.error(f"Error during translation: {e}")
            return None

# Global translator service instance
translator_service = TranslatorService()

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text using the global translator service
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    if not text:
        return ""
        
    # If target language is 'no' or 'none', return original text without translation
    if target_lang == "no" or target_lang == "none":
        return text
        
    translated = translator_service.translate_text(text, source_lang, target_lang)
    return translated if translated else text
