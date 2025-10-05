import streamlit as st
import plotly.graph_objects as go
from auth import login_form, signup_form, get_current_user, logout
from signal_decoder import signal_decoder, get_mock_decoded_text
from translator_service import translate_text
from tts_service import generate_speech
from asr_service import transcribe_speech
from conversation_mode import conversation_mode
from config import config
import numpy as np
import random

# Task progress tracking
task_progress = [
    "- [x] Set up project structure and dependencies",
    "- [x] Create configuration and database setup",
    "- [x] Implement user authentication system",
    "- [x] Create signal decoding simulation",
    "- [x] Implement translation service",
    "- [x] Implement text-to-speech service",
    "- [x] Implement automatic speech recognition service",
    "- [x] Create conversation mode interface",
    "- [x] Build main Streamlit UI with all components",
    "- [x] Add accessibility features and settings",
    "- [x] Test the complete application"
]

# Set page config
st.set_page_config(
    page_title="NeuroLink Speak",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "font_size" not in st.session_state:
    st.session_state.font_size = 16
if "contrast" not in st.session_state:
    st.session_state.contrast = 5

# Apply theme and accessibility settings
contrast_factor = st.session_state.contrast / 5.0  # Normalize contrast to 0-2 range
font_size = st.session_state.font_size

if st.session_state.theme == "dark":
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: #0e1117;
            color: #fafafa;
        }}
        .stMarkdown, .stText {{
            color: #fafafa;
            font-size: {font_size}px;
        }}
        .stButton>button {{
            background-color: #262730;
            color: #fafafa;
            font-size: {font_size}px;
        }}
        .stHeader {{
            color: #fafafa;
            font-size: {font_size + 4}px;
        }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <style>
        .stMarkdown, .stText {{
            font-size: {font_size}px;
        }}
        .stButton>button {{
            font-size: {font_size}px;
        }}
        .stHeader {{
            font-size: {font_size + 4}px;
        }}
    </style>
    """, unsafe_allow_html=True)

def dashboard():
    """Display the dashboard with signal graphs, model status, and connection info"""
    st.title("NeuroLink Speak - Dashboard")
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to see personalized dashboard")
        return
    
    # Display user info
    st.subheader("User Information")
    st.write(f"Username: {user.username}")
    st.write(f"Native Language: {user.native_language}")
    st.write(f"Target Language: {user.target_language}")
    st.write(f"Voice Type: {user.voice_type}")
    
    # Connection status
    st.subheader("Connection Status")
    st.success("EEG/EMG devices connected successfully")
    st.info("Translation service active")
    st.info("Text-to-speech service active")
    st.info("Speech recognition service active")
    
    # Model status
    st.subheader("Model Status")
    st.write("EEG Decoder: Active")
    st.write("EMG Decoder: Active")
    st.write("Translation Models: Cached")
    st.write("TTS Models: Cached")
    st.write("ASR Models: Cached")
    
    # Signal visualization
    st.subheader("Signal Visualization")
    col1, col2 = st.columns(2)
    
    with col1:
        # Generate and display EEG signal
        t_eeg, signal_eeg = signal_decoder.generate_mock_signal("eeg", 5)
        fig_eeg = signal_decoder.visualize_signal(t_eeg, signal_eeg, "eeg")
        st.plotly_chart(fig_eeg, use_container_width=True)
    
    with col2:
        # Generate and display EMG signal
        t_emg, signal_emg = signal_decoder.generate_mock_signal("emg", 5)
        fig_emg = signal_decoder.visualize_signal(t_emg, signal_emg, "emg")
        st.plotly_chart(fig_emg, use_container_width=True)

def thought_to_speech():
    """Display the thought-to-speech interface"""
    st.title("NeuroLink Speak - Thought to Speech")
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to use this feature")
        return
    
    # Select signal type and duration
    signal_type = st.radio("Select Signal Type", ["EEG", "EMG"], horizontal=True)
    duration = st.slider("Signal Duration (seconds)", 1, 30, 10)
    
    if st.button("Decode Signal"):
        with st.spinner(f"Decoding {signal_type} signals..."):
            # Step 1: Get mock decoded text (base English or internal language)
            original_text, confidence, t, signal = get_mock_decoded_text(
                signal_type.lower(), duration
            )

            # Step 2: Translate decoded text to user's native language
            decoded_in_native = translate_text(
                original_text,
                source_lang="en",  # assuming original mock text is English
                target_lang=user.native_language
            )

            # Step 3: Translate decoded text to user's target language
            translated_text = translate_text(
                original_text,
                source_lang=user.native_language,
                target_lang=user.target_language
            )

            # Step 4: Generate speech for translated text (target language)
            audio_bytes = generate_speech(translated_text, user.voice_type)
        
        # === UI Output Section ===
        st.subheader("🧠 Decoded Thought (in Native Language)")
        st.write(f"**{decoded_in_native}**")
        st.caption(f"Confidence: {confidence:.2f}")
        
        st.subheader("📶 Signal Visualization")
        fig = signal_decoder.visualize_signal(t, signal, signal_type.lower())
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🌍 Translation (Target Language)")
        st.write(f"**{translated_text}**")
        
        if audio_bytes:
            st.subheader("🔊 Audio Output (Translated Speech)")
            st.audio(audio_bytes, format="audio/wav")
            st.download_button(
                label="Download Translated Audio",
                data=audio_bytes,
                file_name=f"neurolink_speak_{signal_type.lower()}_{user.target_language}.wav",
                mime="audio/wav"
            )

def incoming_speech():
    """Display the incoming speech interface"""
    st.title("NeuroLink Speak - Incoming Speech")
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to use this feature")
        return
    
    # Options for input
    input_method = st.radio("Input Method", ["Upload Audio File", "Record Audio (Simulated)"], horizontal=True)
    
    if input_method == "Upload Audio File":
        uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])
        if uploaded_file is not None:
            # In a real implementation, we would process the uploaded file
            # For simulation, we'll just use mock data
            st.info("File uploaded successfully (using mock processing)")
            
            if st.button("Process Audio"):
                with st.spinner("Transcribing and translating audio..."):
                    # Generate mock audio bytes
                    sample_rate = 22050
                    duration = random.uniform(1.0, 3.0)
                    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
                    audio_signal = np.int16(np.random.normal(0, 0.1, len(t)) * 32767)
                    audio_bytes = audio_signal.tobytes()
                    
                    # Transcribe audio
                    transcribed_text = transcribe_speech(audio_bytes)
                    
                    # Translate text
                    translated_text = translate_text(
                        transcribed_text, 
                        user.target_language, 
                        user.native_language
                    )
                    
                    # Generate speech
                    response_audio_bytes = generate_speech(translated_text, user.voice_type)
                
                st.subheader("Transcription")
                st.write(f"**Original Text:** {transcribed_text}")
                
                st.subheader("Translation")
                st.write(f"**Translated Text:** {translated_text}")
                
                if response_audio_bytes:
                    st.subheader("Audio Output")
                    st.write(f"**Subtitles:** {translated_text}")
                    st.audio(response_audio_bytes, format="audio/wav")
                    
                    # Download button
                    st.download_button(
                        label="Download Translated Audio",
                        data=response_audio_bytes,
                        file_name="translated_speech.wav",
                        mime="audio/wav"
                    )
    else:  # Record Audio (Simulated)
        st.info("In this simulation, we'll generate mock audio data")
        
        if st.button("Simulate Recording and Process"):
            with st.spinner("Simulating recording and processing..."):
                # Generate mock audio bytes
                sample_rate = 22050
                duration = random.uniform(1.0, 3.0)
                t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
                audio_signal = np.int16(np.random.normal(0, 0.1, len(t)) * 32767)
                audio_bytes = audio_signal.tobytes()
                
                # Transcribe audio
                transcribed_text = transcribe_speech(audio_bytes)
                
                # Translate text
                translated_text = translate_text(
                    transcribed_text, 
                    user.target_language, 
                    user.native_language
                )
                
                # Generate speech
                response_audio_bytes = generate_speech(translated_text, user.voice_type)
            
            st.subheader("Transcription")
            st.write(f"**Original Text:** {transcribed_text}")
            
            st.subheader("Translation")
            st.write(f"**Translated Text:** {translated_text}")
            
            if response_audio_bytes:
                st.subheader("Audio Output")
                st.audio(response_audio_bytes, format="audio/wav")
                
                # Download button
                st.download_button(
                    label="Download Translated Audio",
                    data=response_audio_bytes,
                    file_name="translated_speech.wav",
                    mime="audio/wav"
                )

def settings():
    """Display the settings interface"""
    st.title("NeuroLink Speak - Settings")
    
    user = get_current_user()
    if not user:
        st.warning("Please log in to access settings")
        return
    
    # Theme toggle
    st.subheader("Appearance")
    theme = st.radio("Theme", ["Light", "Dark"], horizontal=True)
    if theme.lower() != st.session_state.theme:
        st.session_state.theme = theme.lower()
        st.rerun()
    
    # Language settings
    st.subheader("Language Preferences")
    native_language = st.selectbox(
        "Native Language", 
        config.SUPPORTED_LANGUAGES, 
        index=config.SUPPORTED_LANGUAGES.index(user.native_language)
    )

    # 🔄 Show Target Language only if translation is enabled
    if st.session_state.get("translation_enabled", True):
        target_language = st.selectbox(
            "Target Language", 
            config.SUPPORTED_LANGUAGES, 
            index=config.SUPPORTED_LANGUAGES.index(user.target_language)
        )
    else:
        target_language = user.native_language  # fallback to native if disabled
        st.info("Translation is disabled — using native language only.")
    
    voice_type = st.selectbox(
        "Voice Type", 
        ["default", "male", "female"], 
        index=["default", "male", "female"].index(user.voice_type)
    )
    
    # Accessibility settings
    st.subheader("Accessibility")
    font_size = st.slider("Font Size", 12, 24, st.session_state.font_size)
    contrast = st.slider("Contrast", 1, 10, st.session_state.contrast)
    
    # Privacy settings
    st.subheader("Privacy")
    st.info("Use the toggle in Conversation Mode to enable/disable active decoding")

    # Unified Update Preferences button
    if st.button("💾 Update Preferences"):
        from database import get_db
        db_generator = get_db()
        db = next(db_generator)
        
        try:
            # Update all user preferences
            user.native_language = native_language
            user.target_language = target_language
            user.voice_type = voice_type
            st.session_state.font_size = font_size
            st.session_state.contrast = contrast
            
            db.commit()
            st.success("All preferences updated successfully!")
            st.rerun()
        except Exception as e:
            db.rollback()
            st.error(f"Error updating preferences: {e}")
        finally:
            try:
                next(db_generator)
            except StopIteration:
                pass


def main():
    """Main application function"""
    # Sidebar navigation
    st.sidebar.title("NeuroLink Speak")
    
    user = get_current_user()
    
    if user:
        st.sidebar.write(f"Welcome, {user.username}!")
        if st.sidebar.button("Logout"):
            logout()
    else:
        auth_option = st.sidebar.radio("Authentication", ["Login", "Sign Up"])
        if auth_option == "Login":
            login_form()
        else:
            signup_form()
    
    #translation toggle
    st.sidebar.divider()
    translation_enabled = st.sidebar.toggle("🌍 Enable Translation", value=True)
    st.session_state.translation_enabled = translation_enabled
    
    # Navigation
    st.sidebar.divider()
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Thought to Speech", "Incoming Speech", "Conversation Mode", "Settings"]
    )
    
    # Update session state
    st.session_state.page = page.lower().replace(" ", "_")
    
    # Display selected page
    if st.session_state.page == "dashboard":
        dashboard()
    elif st.session_state.page == "thought_to_speech":
        thought_to_speech()
    elif st.session_state.page == "incoming_speech":
        incoming_speech()
    elif st.session_state.page == "conversation_mode":
        conversation_mode()
    elif st.session_state.page == "settings":
        settings()

if __name__ == "__main__":
    main()
