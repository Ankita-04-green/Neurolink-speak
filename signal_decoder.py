import streamlit as st
import numpy as np
import plotly.graph_objects as go
from typing import Tuple, Dict
import random

class SignalDecoder:
    """Simulates EEG/EMG signal decoding to text conversion"""
    
    def __init__(self):
        # Common phrases for non-verbal communication
        self.phrases = [
            "I need help",
            "I am hungry",
            "I am thirsty",
            "I am in pain",
            "I need to use the restroom",
            "Yes",
            "No",
            "Please",
            "Thank you",
            "Hello",
            "Goodbye",
            "I love you",
            "I am tired",
            "I am happy",
            "I am sad",
            "I am uncomfortable",
            "I am cold",
            "I am hot",
            "I am scared",
            "I am confused"
        ]
        
        # Confidence levels for each phrase
        self.confidence_levels = {
            phrase: random.uniform(0.7, 0.95) for phrase in self.phrases
        }
    
    def generate_mock_signal(self, signal_type: str = "eeg", duration: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate mock EEG or EMG signals
        
        Args:
            signal_type: Either "eeg" or "emg"
            duration: Duration of signal in seconds
            
        Returns:
            Tuple of time array and signal array
        """
        # Sampling rate (samples per second)
        fs = 256 if signal_type == "eeg" else 1000
        
        # Time array
        t = np.linspace(0, duration, fs * duration)
        
        # Generate mock signal based on type
        if signal_type == "eeg":
            # EEG-like signal with multiple frequency components
            signal = (np.sin(2 * np.pi * 8 * t) +  # Alpha waves (8 Hz)
                     0.5 * np.sin(2 * np.pi * 15 * t) +  # Beta waves (15 Hz)
                     0.3 * np.sin(2 * np.pi * 4 * t) +   # Theta waves (4 Hz)
                     0.1 * np.random.normal(0, 1, len(t)))  # Noise
        else:  # EMG
            # EMG-like signal with burst activity
            signal = np.random.normal(0, 0.5, len(t))
            # Add some muscle activation bursts
            for _ in range(5):
                start = random.randint(0, len(t) - 50)
                signal[start:start+50] += np.sin(np.linspace(0, 2*np.pi, 50)) * random.uniform(1, 3)
        
        return t, signal
    
    def decode_signal(self, signal: np.ndarray, signal_type: str = "eeg") -> Tuple[str, float]:
        """
        Map signals to text phrases (simulated decoding)
        
        Args:
            signal: Signal array to decode
            signal_type: Either "eeg" or "emg"
            
        Returns:
            Tuple of decoded phrase and confidence score
        """
        # In a real implementation, this would use ML models
        # For simulation, we'll randomly select a phrase with a confidence score
        
        # Calculate some features from the signal
        signal_energy = np.sum(signal**2) / len(signal)
        signal_mean = np.mean(signal)
        signal_std = np.std(signal)
        
        # Use these features to deterministically select a phrase
        # (in a real system, this would be a trained ML model)
        feature_sum = signal_energy + signal_mean + signal_std
        phrase_index = int(feature_sum * 1000) % len(self.phrases)
        
        phrase = self.phrases[phrase_index]
        confidence = self.confidence_levels[phrase]
        
        # Add some randomness to confidence
        confidence = max(0.1, min(0.99, confidence + random.uniform(-0.1, 0.1)))
        
        return phrase, confidence
    
    def visualize_signal(self, t: np.ndarray, signal: np.ndarray, signal_type: str = "eeg") -> go.Figure:
        """
        Create a Plotly visualization of the signal
        
        Args:
            t: Time array
            signal: Signal array
            signal_type: Either "eeg" or "emg"
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=t,
            y=signal,
            mode='lines',
            name=f'{signal_type.upper()} Signal',
            line=dict(color='blue' if signal_type == "eeg" else 'red')
        ))
        
        fig.update_layout(
            title=f"Mock {signal_type.upper()} Signal",
            xaxis_title="Time (seconds)",
            yaxis_title="Amplitude (microvolts)" if signal_type == "eeg" else "Amplitude (millivolts)",
            height=300,
            showlegend=True
        )
        
        return fig

# Global signal decoder instance
signal_decoder = SignalDecoder()

def get_mock_decoded_text(signal_type: str = "eeg", duration: int = 10) -> Tuple[str, float, np.ndarray, np.ndarray]:
    """
    Generate mock decoded text from simulated signals
    
    Args:
        signal_type: Either "eeg" or "emg"
        duration: Duration of signal in seconds (default: 10)
        
    Returns:
        Tuple of (decoded_text, confidence_score, time_array, signal_array)
    """
    t, signal = signal_decoder.generate_mock_signal(signal_type, duration)
    text, confidence = signal_decoder.decode_signal(signal, signal_type)
    return text, confidence, t, signal
