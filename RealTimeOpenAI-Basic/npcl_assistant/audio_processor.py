#!/usr/bin/env python3
"""
Audio Processing for NPCL Voice Assistant
Handles audio conversion between different formats and sample rates
"""

import numpy as np
import audioop
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Audio processing utilities for voice assistant"""
    
    def __init__(self):
        self.target_rms = 1000
        
    def resample_pcm_24khz_to_16khz(self, pcm_24khz: bytes) -> bytes:
        """Resample PCM audio from 24kHz to 16kHz for Asterisk"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(pcm_24khz, dtype=np.int16)
            
            # Simple decimation (take every 3rd sample: 24000/16000 = 1.5, so we approximate)
            # For better quality, we could use scipy.signal.resample
            resampled = audio_array[::3]  # Take every 3rd sample
            
            # Convert back to bytes
            return resampled.astype(np.int16).tobytes()
            
        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return pcm_24khz  # Return original if resampling fails
    
    def resample_pcm_16khz_to_24khz(self, pcm_16khz: bytes) -> bytes:
        """Resample PCM audio from 16kHz to 24kHz for OpenAI"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(pcm_16khz, dtype=np.int16)
            
            # Simple upsampling by repeating samples
            # For better quality, we could use scipy.signal.resample
            upsampled = np.repeat(audio_array, 3)[:len(audio_array) * 3 // 2]
            
            # Convert back to bytes
            return upsampled.astype(np.int16).tobytes()
            
        except Exception as e:
            logger.error(f"Error upsampling audio: {e}")
            return pcm_16khz  # Return original if upsampling fails
    
    def normalize_audio(self, pcm_buffer: bytes, target_rms: int = None) -> Tuple[bytes, float]:
        """Normalize audio to target RMS level"""
        if target_rms is None:
            target_rms = self.target_rms
            
        try:
            # Calculate current RMS
            current_rms = audioop.rms(pcm_buffer, 2)
            
            if current_rms == 0:
                return pcm_buffer, 0.0
            
            # Calculate scaling factor
            scale_factor = target_rms / current_rms
            
            # Apply scaling (but limit to prevent clipping)
            scale_factor = min(scale_factor, 4.0)  # Max 4x amplification
            
            # Apply the scaling
            normalized = audioop.mul(pcm_buffer, 2, scale_factor)
            
            return normalized, current_rms
            
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return pcm_buffer, 0.0
    
    def is_silence(self, pcm_buffer: bytes, threshold: int = 100) -> bool:
        """Quick silence detection"""
        try:
            rms = audioop.rms(pcm_buffer, 2)
            return rms < threshold
        except:
            return False
    
    def convert_to_asterisk_format(self, pcm_buffer: bytes, source_rate: int = 24000) -> bytes:
        """Convert audio to Asterisk-compatible format"""
        if source_rate == 24000:
            # Resample from 24kHz to 16kHz
            return self.resample_pcm_24khz_to_16khz(pcm_buffer)
        elif source_rate == 16000:
            # Already correct format
            return pcm_buffer
        else:
            logger.warning(f"Unsupported source rate: {source_rate}")
            return pcm_buffer
    
    def convert_from_asterisk_format(self, pcm_buffer: bytes, target_rate: int = 24000) -> bytes:
        """Convert audio from Asterisk format to target format"""
        if target_rate == 24000:
            # Resample from 16kHz to 24kHz
            return self.resample_pcm_16khz_to_24khz(pcm_buffer)
        elif target_rate == 16000:
            # Already correct format
            return pcm_buffer
        else:
            logger.warning(f"Unsupported target rate: {target_rate}")
            return pcm_buffer

# Global audio processor instance
audio_processor = AudioProcessor()