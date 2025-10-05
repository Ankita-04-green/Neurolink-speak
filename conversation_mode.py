import streamlit as st
import numpy as np
from database import ConversationLog, get_db
from signal_decoder import get_mock_decoded_text
from translator_service import translate_text
from tts_service import generate_speech
from asr_service import transcribe_speech
from auth import get_current_user
import random
from typing import List, Tuple

class ConversationManager:
    """Manages the conversation mode interface and functionality"""
    
    def __init__(self):
        self.user = get_current_user()
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        if "active_decoding" not in st.session_state:
            st.session_state.active_decoding = True
    
    def save_conversation_log(self, direction: str, original_text: str, translated_text: str, audio_bytes: bytes = None) -> bool:
        """
        Save conversation log to database
        
        Args:
            direction: "outgoing" or "incoming"
            original_text: Original text before translation
            translated_text: Translated text
            audio_bytes: Audio data (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.user:
            return False
            
        db_generator = get_db()
        db = next(db_generator)
        
        try:
            # Save audio to file if provided
            audio_file_path = None
            if audio_bytes:
                audio_file_path = f"audio_logs/{self.user.id}_{direction}_{len(st.session_state.conversation_history)}.wav"
                # In a real implementation, we would save the audio file
                # For simulation, we'll just note that audio would be saved
            
            # Create conversation log entry
            log_entry = ConversationLog(
                user_id=self.user.id,
                direction=direction,
                original_text=original_text,
                translated_text=translated_text,
                audio_file_path=audio_file_path
            )
            
            db.add(log_entry)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            st.error(f"Error saving conversation log: {e}")
            return False
        finally:
            # Close the database connection
            try:
                next(db_generator)
            except StopIteration:
                pass
    
    def simulate_outgoing_message(self) -> Tuple[str, str, bytes]:
        """
        Simulate an outgoing message from EEG/EMG signals
        
        Returns:
            Tuple of (original_text, translated_text, audio_bytes)
        """
        # Get mock decoded text from EEG/EMG signals
        original_text, confidence, t, signal = get_mock_decoded_text()
        
        # Translate text to user's target language
        translated_text = translate_text(
            original_text, 
            self.user.native_language, 
            self.user.target_language
        )
        
        # Generate speech audio
        audio_bytes = generate_speech(translated_text, self.user.voice_type)
        
        # Save to conversation history
        message_entry = {
            "sender": "You",
            "original": original_text,
            "translated": translated_text,
            "confidence": confidence,
            "audio": audio_bytes,
            "timestamp": st.session_state.get("message_counter", 0)
        }
        
        st.session_state.conversation_history.append(message_entry)
        st.session_state.message_counter = st.session_state.get("message_counter", 0) + 1
        
        # Save to database
        self.save_conversation_log("outgoing", original_text, translated_text, audio_bytes)
        
        return original_text, translated_text, audio_bytes
    
    def simulate_incoming_message(self) -> Tuple[str, str, bytes]:
        """
        Simulate an incoming message from speech
        
        Returns:
            Tuple of (original_text, translated_text, audio_bytes)
        """
        # Generate mock audio bytes
        sample_rate = 22050
        duration = random.uniform(1.0, 3.0)
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_signal = np.int16(np.random.normal(0, 0.1, len(t)) * 32767)
        audio_bytes = audio_signal.tobytes()
        
        # Transcribe audio to text
        original_text = transcribe_speech(audio_bytes)
        
        if not original_text:
            original_text = "Sorry, I couldn't understand that."
        
        # Translate text to user's native language
        translated_text = translate_text(
            original_text, 
            self.user.target_language, 
            self.user.native_language
        )
        
        # Generate speech audio for translated text
        response_audio_bytes = generate_speech(translated_text, self.user.voice_type)
        
        # Save to conversation history
        message_entry = {
            "sender": "Partner",
            "original": original_text,
            "translated": translated_text,
            "audio": response_audio_bytes,
            "timestamp": st.session_state.get("message_counter", 0)
        }
        
        st.session_state.conversation_history.append(message_entry)
        st.session_state.message_counter = st.session_state.get("message_counter", 0) + 1
        
        # Save to database
        self.save_conversation_log("incoming", original_text, translated_text, response_audio_bytes)
        
        return original_text, translated_text, response_audio_bytes
    
    def display_conversation_history(self):
        """Display the conversation history in a two-pane interface"""
        # Create two columns for the conversation interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Messages (EEG/EMG → Text → Speech)")
            for entry in st.session_state.conversation_history:
                if entry["sender"] == "You":
                    with st.container(border=True):
                        st.write(f"**Decoded Text:** {entry['original']}")
                        st.write(f"**Translated Text:** {entry['translated']}")
                        st.write(f"**Confidence:** {entry['confidence']:.2f}")
                        if entry["audio"]:
                            st.write("**Audio:**")
                            st.audio(entry["audio"], format="audio/wav")
        
        with col2:
            st.subheader("Partner Messages (Speech → Text → Translation)")
            for entry in st.session_state.conversation_history:
                if entry["sender"] == "Partner":
                    with st.container(border=True):
                        st.write(f"**Original Speech:** {entry['original']}")
                        st.write(f"**Translation:** {entry['translated']}")
                        st.write(f"**Subtitles:** {entry['translated']}")
                        if entry["audio"]:
                            st.audio(entry["audio"], format="audio/wav")
    
    def conversation_interface(self):
        """Main conversation mode interface"""
        st.title("NeuroLink Speak - Conversation Mode")
        
        if not self.user:
            st.warning("Please log in to use conversation mode")
            return
        
        # Privacy toggle
        st.session_state.active_decoding = st.toggle(
            "Active Decoding", 
            value=st.session_state.active_decoding,
            help="Toggle to enable/disable EEG/EMG signal decoding"
        )
        
        # Display conversation history
        self.display_conversation_history()
        
        # Controls for simulating messages
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Simulate Your Message (EEG/EMG)", use_container_width=True):
                if st.session_state.active_decoding:
                    with st.spinner("Decoding EEG/EMG signals..."):
                        original, translated, audio = self.simulate_outgoing_message()
                    
                    st.success("Message sent successfully!")
                    st.rerun()
                else:
                    st.warning("Active decoding is disabled. Enable it to send messages.")
        
        with col2:
            if st.button("Simulate Partner Message (Speech)", use_container_width=True):
                with st.spinner("Processing incoming speech..."):
                    original, translated, audio = self.simulate_incoming_message()
                
                st.success("Partner message received!")
                st.rerun()
        
        # Manual input option
        st.divider()
        st.subheader("Manual Input")
        manual_text = st.text_input("Enter your message manually")
        native_translated_text = translate_text(
                manual_text, 
                "en", 
                self.user.native_language
            )
        if st.button("Send Manual Message") and manual_text:
            # Translate and generate audio
            translated_text = translate_text(
                native_translated_text, 
                self.user.native_language, 
                self.user.target_language
            )
            
            audio_bytes = generate_speech(translated_text, self.user.voice_type)
            
            # Save to conversation history
            message_entry = {
                "sender": "You",
                "original": native_translated_text,
                "translated": translated_text,
                "confidence": 1.0,
                "audio": audio_bytes,
                "timestamp": st.session_state.get("message_counter", 0)
            }
            
            st.session_state.conversation_history.append(message_entry)
            st.session_state.message_counter = st.session_state.get("message_counter", 0) + 1
            
            # Save to database
            self.save_conversation_log("outgoing", manual_text, translated_text, audio_bytes)
            
            st.success("Manual message sent!")
            st.rerun() 


# Global conversation manager instance
conversation_manager = ConversationManager()

def conversation_mode():
    """Display the conversation mode interface"""
    user = get_current_user()
    if not user:
        st.warning("Please log in to use conversation mode")
        return
    # Create a new conversation manager instance for each call
    manager = ConversationManager()
    manager.conversation_interface()

