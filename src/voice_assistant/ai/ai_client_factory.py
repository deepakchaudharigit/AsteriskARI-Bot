"""
AI Client Factory for OpenAI Real-time API.
Provides a unified interface for AI providers.
"""

import logging
from typing import Union, Optional, Dict, Any
from config.settings import get_settings
from .openai_realtime_client_enhanced import OpenAIRealtimeClientEnhanced, OpenAIRealtimeConfig

logger = logging.getLogger(__name__)


class AIClientFactory:
    """Factory for creating AI clients based on configuration"""
    
    @staticmethod
    def create_client(provider: Optional[str] = None) -> OpenAIRealtimeClientEnhanced:
        """
        Create an AI client based on the provider setting
        
        Args:
            provider: AI provider ('openai'). If None, uses settings.
            
        Returns:
            Configured AI client instance
            
        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        settings = get_settings()
        
        # Always use OpenAI provider
        ai_provider = "openai"
        
        logger.info(f"Creating AI client for provider: {ai_provider}")
        
        return AIClientFactory._create_openai_client()
    
    @staticmethod
    def _create_openai_client() -> OpenAIRealtimeClientEnhanced:
        """Create and configure OpenAI Real-time client"""
        settings = get_settings()
        
        # Validate OpenAI API key
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI Real-time API")
        
        # Create OpenAI configuration with enhanced settings
        config = OpenAIRealtimeConfig(
            model=settings.openai_realtime_model,
            voice=settings.voice_model,  # Use voice_model from settings
            input_audio_format="pcm16",
            output_audio_format="pcm16",
            sample_rate=settings.sample_rate,  # 24kHz for OpenAI
            chunk_size=settings.chunk_size,    # 1024 from RealTimeOpenAI-Basic
            channels=settings.channels,        # 1 channel
            enable_interruption=settings.enable_voice_interruption,
            interruption_threshold=settings.interruption_threshold,  # 0.8 from RealTimeOpenAI-Basic
            vad_threshold=settings.vad_threshold,                    # 0.8
            prefix_padding_ms=settings.prefix_padding_ms,            # 200ms
            silence_duration_ms=settings.silence_duration_ms,        # 4000ms
            response_delay_seconds=settings.response_delay_seconds,  # 10 seconds
            target_rms=1000,  # From RealTimeOpenAI-Basic
            enable_audio_normalization=True
        )
        
        logger.info(f"Creating OpenAI Real-time client with model: {config.model}, voice: {config.voice}")
        logger.info(f"Features: interruption={config.enable_interruption}, audio_normalization={config.enable_audio_normalization}")
        logger.info(f"VAD settings: threshold={config.vad_threshold}, response_delay={config.response_delay_seconds}s")
        
        return OpenAIRealtimeClientEnhanced(
            api_key=settings.openai_api_key,
            config=config
        )
    

    
    @staticmethod
    def get_supported_providers() -> list:
        """Get list of supported AI providers"""
        return ["openai"]
    
    @staticmethod
    def validate_provider_config(provider: str) -> bool:
        """
        Validate that the provider configuration is complete
        
        Args:
            provider: AI provider to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        settings = get_settings()
        
        try:
            if provider.lower() == "openai":
                return bool(settings.openai_api_key and settings.openai_api_key.strip())
            else:
                return False
        except Exception:
            return False
    
    @staticmethod
    def get_provider_info(provider: str) -> dict:
        """
        Get information about a specific provider
        
        Args:
            provider: AI provider name
            
        Returns:
            Dictionary with provider information
        """
        settings = get_settings()
        
        if provider.lower() == "openai":
            return {
                "name": "OpenAI Real-time API",
                "model": settings.openai_realtime_model,
                "voice": settings.openai_voice,
                "features": [
                    "Real-time voice conversation",
                    "Voice interruption",
                    "Noise cancellation",
                    "Function calling",
                    "Low latency"
                ],
                "audio_format": "PCM16, 24kHz",
                "configured": AIClientFactory.validate_provider_config("openai")
            }
        else:
            return {
                "name": "Unknown Provider",
                "configured": False
            }


# Convenience functions for backward compatibility
def create_ai_client(provider: Optional[str] = None) -> OpenAIRealtimeClientEnhanced:
    """Create an AI client using the factory"""
    return AIClientFactory.create_client(provider)


def get_current_provider() -> str:
    """Get the current AI provider from settings"""
    return "openai"


def get_provider_info(provider: str) -> Dict[str, Any]:
    """Get information about a specific AI provider"""
    settings = get_settings()
    
    if provider == "openai":
        return {
            "name": "OpenAI Real-time API",
            "model": getattr(settings, 'openai_realtime_model', 'gpt-4o-realtime-preview-2024-10-01'),
            "voice": getattr(settings, 'voice_model', 'alloy'),
            "configured": bool(getattr(settings, 'openai_api_key', None)),
            "features": [
                "Real-time voice interruption",
                "Advanced audio processing",
                "24kHz audio support",
                "Voice Activity Detection",
                "Natural conversation flow",
                "Professional customer service"
            ],
            "sample_rate": getattr(settings, 'sample_rate', 24000),
            "chunk_size": getattr(settings, 'chunk_size', 1024),
            "interruption_enabled": getattr(settings, 'enable_voice_interruption', True),
            "response_delay": getattr(settings, 'response_delay_seconds', 10)
        }

    else:
        return {
            "name": "Unknown Provider",
            "model": "unknown",
            "voice": "unknown",
            "configured": False,
            "features": [],
            "sample_rate": 16000,
            "chunk_size": 320,
            "interruption_enabled": False,
            "response_delay": 5
        }


def switch_provider(provider: str) -> bool:
    """Switch to a different AI provider (runtime switching)"""
    if provider not in AIClientFactory.get_supported_providers():
        logger.error(f"Unsupported provider: {provider}")
        return False
    
    # Validate provider configuration
    if not AIClientFactory.validate_provider_config(provider):
        logger.error(f"Provider {provider} is not properly configured")
        return False
    
    # Note: This is a runtime switch - for persistent changes,
    # update the .env file or configuration
    logger.info(f"Switching to AI provider: {provider}")
    
    # In a real implementation, you might want to:
    # 1. Update environment variable
    # 2. Reload configuration
    # 3. Recreate client instances
    
    return True