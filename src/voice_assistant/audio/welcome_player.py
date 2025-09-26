"""
Welcome message player for voice assistant.
Plays welcome.wav file when calls are initiated.
"""

import asyncio
import logging
import wave
import struct
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WelcomePlayer:
    """Plays welcome message audio file"""
    
    def __init__(self, welcome_file_path: str = None):
        """
        Initialize welcome player
        
        Args:
            welcome_file_path: Path to welcome.wav file
        """
        # Default to welcome.wav in project root
        if welcome_file_path is None:
            project_root = Path(__file__).parent.parent.parent.parent
            welcome_file_path = project_root / "welcome.wav"
        
        self.welcome_file_path = Path(welcome_file_path)
        self.audio_data: Optional[bytes] = None
        self.sample_rate: int = 16000
        self.channels: int = 1
        self.sample_width: int = 2  # 16-bit
        
        # Load welcome audio on initialization
        self._load_welcome_audio()
    
    def _load_welcome_audio(self) -> bool:
        """Load welcome audio file into memory"""
        try:
            if not self.welcome_file_path.exists():
                logger.error(f"Welcome file not found: {self.welcome_file_path}")
                return False
            
            with wave.open(str(self.welcome_file_path), 'rb') as wav_file:
                # Get audio parameters
                self.channels = wav_file.getnchannels()
                self.sample_width = wav_file.getsampwidth()
                self.sample_rate = wav_file.getframerate()
                frames = wav_file.getnframes()
                
                # Read all audio data
                self.audio_data = wav_file.readframes(frames)
                
                logger.info(f"Loaded welcome audio: {frames} frames, "
                           f"{self.sample_rate}Hz, {self.channels} channels, "
                           f"{self.sample_width * 8}-bit")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to load welcome audio: {e}")
            return False
    
    def get_welcome_audio_chunks(self, chunk_size: int = 320) -> list:
        """
        Get welcome audio as chunks for streaming
        
        Args:
            chunk_size: Size of each audio chunk in samples (default 320 = 20ms at 16kHz)
            
        Returns:
            List of audio chunks as bytes
        """
        if not self.audio_data:
            logger.warning("No welcome audio data loaded")
            return []
        
        chunks = []
        bytes_per_chunk = chunk_size * self.sample_width * self.channels
        
        for i in range(0, len(self.audio_data), bytes_per_chunk):
            chunk = self.audio_data[i:i + bytes_per_chunk]
            
            # Pad last chunk if necessary
            if len(chunk) < bytes_per_chunk:
                padding = bytes_per_chunk - len(chunk)
                chunk += b'\\x00' * padding
            
            chunks.append(chunk)
        
        logger.debug(f"Created {len(chunks)} audio chunks of {bytes_per_chunk} bytes each")
        return chunks
    
    async def stream_welcome_audio(self, audio_sender, chunk_delay: float = 0.02) -> bool:
        """
        Stream welcome audio through provided sender function
        
        Args:
            audio_sender: Async function to send audio chunks
            chunk_delay: Delay between chunks in seconds (default 20ms)
            
        Returns:
            True if streaming completed successfully
        """
        try:
            if not self.audio_data:
                logger.warning("No welcome audio to stream")
                return False
            
            chunks = self.get_welcome_audio_chunks()
            
            logger.info(f"Streaming welcome message ({len(chunks)} chunks)")
            
            for i, chunk in enumerate(chunks):
                # Send audio chunk
                success = await audio_sender(chunk)
                if not success:
                    logger.warning(f"Failed to send audio chunk {i}")
                    return False
                
                # Wait before sending next chunk (maintain real-time playback)
                if i < len(chunks) - 1:  # Don't wait after last chunk
                    await asyncio.sleep(chunk_delay)
            
            logger.info("Welcome message streaming completed")
            return True
            
        except Exception as e:
            logger.error(f"Error streaming welcome audio: {e}")
            return False
    
    def get_audio_info(self) -> Dict[str, Any]:
        """Get information about loaded audio"""
        if not self.audio_data:
            return {"loaded": False}
        
        duration = len(self.audio_data) / (self.sample_rate * self.channels * self.sample_width)
        
        return {
            "loaded": True,
            "file_path": str(self.welcome_file_path),
            "duration_seconds": duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "sample_width": self.sample_width,
            "total_bytes": len(self.audio_data),
            "total_samples": len(self.audio_data) // (self.sample_width * self.channels)
        }
    
    def is_loaded(self) -> bool:
        """Check if welcome audio is loaded"""
        return self.audio_data is not None
    
    def reload_audio(self) -> bool:
        """Reload welcome audio file"""
        self.audio_data = None
        return self._load_welcome_audio()


# Global welcome player instance
_welcome_player: Optional[WelcomePlayer] = None


def get_welcome_player() -> WelcomePlayer:
    """Get global welcome player instance"""
    global _welcome_player
    if _welcome_player is None:
        _welcome_player = WelcomePlayer()
    return _welcome_player


async def play_welcome_message(audio_sender) -> bool:
    """
    Convenience function to play welcome message
    
    Args:
        audio_sender: Async function to send audio chunks
        
    Returns:
        True if welcome message played successfully
    """
    player = get_welcome_player()
    if not player.is_loaded():
        logger.warning("Welcome audio not loaded, skipping welcome message")
        return False
    
    return await player.stream_welcome_audio(audio_sender)