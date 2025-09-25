"""
FastAPI server for handling Asterisk ARI events with OpenAI Real-time API integration. Provides HTTP endpoints for ARI events and WebSocket support for external media.

FastAPI server for handling Asterisk ARI events with OpenAI Real-time API integration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import get_settings, get_logging_settings
from src.voice_assistant.utils.logger import setup_logger
from src.voice_assistant.telephony.realtime_ari_handler import create_realtime_ari_app
from src.voice_assistant.ai.ai_client_factory import (
    get_current_provider, get_provider_info, AIClientFactory, switch_provider
)


def create_app() -> FastAPI:
    """Create the main FastAPI application"""
    
    # Setup logging
    logging_settings = get_logging_settings()
    setup_logger(__name__)
    
    logger = logging.getLogger(__name__)
    settings = get_settings()
    
    # Get current AI provider
    current_provider = get_current_provider()
    provider_info = get_provider_info(current_provider)
    
    # Create the main app
    app = FastAPI(
        title=f"NPCL Voice Assistant - Real-time ARI Server ({current_provider.upper()})",
        description=f"Real-time conversational AI with Asterisk ARI and {provider_info['name']}",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create and mount the ARI handler app
    ari_app = create_realtime_ari_app()
    app.mount("/ari", ari_app)
    
    # Also add the events endpoint directly to main app for better accessibility
    from src.voice_assistant.telephony.realtime_ari_handler import RealTimeARIHandler
    
    # Create a shared ARI handler instance
    shared_ari_handler = RealTimeARIHandler()
    
    @app.on_event("startup")
    async def startup_shared_handler():
        """Start the shared ARI handler"""
        await shared_ari_handler.start()
    
    @app.on_event("shutdown")
    async def shutdown_shared_handler():
        """Stop the shared ARI handler"""
        await shared_ari_handler.stop()
    
    @app.post("/ari/events")
    async def handle_ari_events_direct(request: Request):
        """Handle incoming ARI events - direct endpoint"""
        event_data = await request.json()
        result = await shared_ari_handler.handle_ari_event(event_data)
        logger.info(f"Processed ARI event: {event_data.get('type', 'unknown')}")
        return result
    
    @app.get("/ari/calls")
    async def get_calls_direct():
        """Get active calls - direct endpoint"""
        return {
            "active_calls": list(shared_ari_handler.active_calls.keys()),
            "call_count": len(shared_ari_handler.active_calls)
        }
    
    @app.get("/ari/status")
    async def get_status_direct():
        """Get system status - direct endpoint"""
        return shared_ari_handler.get_system_status()
    
    @app.get("/ari/health")
    async def get_health_direct():
        """Health check - direct endpoint"""
        return {
            "status": "healthy",
            "service": "realtime-openai-voice-assistant-ari",
            "is_running": shared_ari_handler.is_running,
            "active_calls": len(shared_ari_handler.active_calls),
            "features": {
                "call_transfer": True,
                "customer_data": True,
                "queue_management": True,
                "conversation_tracking": True
            }
        }
    
    @app.get("/")
    async def root():
        """Root endpoint with system information"""
        return {
            "service": f"NPCL Voice Assistant - Real-time ARI Server ({current_provider.upper()})",
            "version": "2.0.0",
            "status": "running",
            "ai_provider": current_provider,
            "features": provider_info.get('features', []) + [
                "Bidirectional audio streaming with externalMedia",
                "Voice Activity Detection",
                "Session management",
                "slin16 audio format support"
            ],
            "endpoints": {
                "ari_events": "/ari/events",
                "status": "/ari/status",
                "calls": "/ari/calls",
                "health": "/ari/health",
                "docs": "/docs"
            },
            "configuration": {
                "assistant_name": settings.assistant_name,
                "ai_provider": current_provider,
                "ai_model": provider_info.get('model', 'unknown'),
                "ai_voice": provider_info.get('voice', 'unknown'),
                "audio_format": settings.audio_format,
                "sample_rate": settings.audio_sample_rate,
                "external_media_port": settings.external_media_port,
                "stasis_app": settings.stasis_app,
                "voice_interruption": settings.enable_voice_interruption,
                "noise_cancellation": settings.enable_noise_cancellation
            }
        }
    
    @app.get("/info")
    async def system_info():
        """Detailed system information"""
        return {
            "system": {
                "name": "OpenAI Voice Assistant",
                "version": "2.0.0",
                "type": "Real-time ARI Integration"
            },
            "ai": {
                "provider": provider_info['name'],
                "provider_key": current_provider,
                "model": provider_info.get('model', 'unknown'),
                "voice": provider_info.get('voice', 'unknown'),
                "features": provider_info.get('features', []),
                "configured": provider_info.get('configured', False)
            },
            "telephony": {
                "platform": "Asterisk",
                "interface": "ARI (Asterisk REST Interface)",
                "audio_streaming": "externalMedia WebSocket",
                "format": settings.audio_format,
                "sample_rate": f"{settings.audio_sample_rate} Hz",
                "channels": settings.audio_channels
            },
            "capabilities": {
                "real_time_conversation": True,
                "voice_activity_detection": True,
                "interruption_handling": settings.enable_interruption_handling,
                "voice_interruption": settings.enable_voice_interruption,
                "noise_cancellation": settings.enable_noise_cancellation,
                "session_management": True,
                "call_recording": settings.enable_call_recording,
                "auto_answer": settings.auto_answer_calls
            }
        }
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )
    
    # AI Provider management endpoints
    @app.get("/ai/providers")
    async def list_providers():
        """List all supported AI providers"""
        providers = AIClientFactory.get_supported_providers()
        return {
            "providers": providers,
            "current": current_provider,
            "details": {provider: get_provider_info(provider) for provider in providers}
        }
    
    @app.get("/ai/provider/current")
    async def get_current_ai_provider():
        """Get current AI provider information"""
        return {
            "provider": current_provider,
            "info": provider_info
        }
    
    @app.get("/ai/provider/{provider_name}/info")
    async def get_provider_details(provider_name: str):
        """Get detailed information about a specific provider"""
        if provider_name not in AIClientFactory.get_supported_providers():
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return {
            "provider": provider_name,
            "info": get_provider_info(provider_name),
            "is_current": provider_name == current_provider
        }
    
    @app.post("/ai/provider/switch/{provider_name}")
    async def switch_ai_provider(provider_name: str):
        """Switch to a different AI provider"""
        if provider_name not in AIClientFactory.get_supported_providers():
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Validate provider configuration
        if not AIClientFactory.validate_provider_config(provider_name):
            raise HTTPException(
                status_code=400, 
                detail=f"Provider {provider_name} is not properly configured"
            )
        
        # Switch provider
        success = switch_provider(provider_name)
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to switch to provider {provider_name}"
            )
        
        return {
            "status": "success",
            "previous_provider": current_provider,
            "new_provider": provider_name,
            "message": f"Switched to {provider_name}. Restart the service for changes to take effect."
        }
    
    logger.info("FastAPI application created successfully")
    return app


def main():
    """Main entry point for the server"""
    settings = get_settings()
    current_provider = get_current_provider()
    provider_info = get_provider_info(current_provider)
    
    print("\\n" + "="*80)
    print(f"🚀 STARTING NPCL VOICE ASSISTANT - REAL-TIME ARI SERVER ({current_provider.upper()})")
    print("="*80)
    print(f"🔍 Server Status: http://localhost:8000/status")
    print(f"📞 Call Status: http://localhost:8000/ari/calls")
    print(f"🌡️ Health Check: http://localhost:8000/ari/health")
    print("="*80)
    print(f"🤖 Assistant: {settings.assistant_name}")
    print(f"🧠 AI Provider: {provider_info['name']}")
    print(f"🎯 AI Model: {provider_info.get('model', 'unknown')}")
    print(f"🎤 Voice: {provider_info.get('voice', 'unknown')}")
    print(f"🔊 Audio: {settings.audio_format} @ {settings.audio_sample_rate}Hz")
    print(f"📞 Stasis App: {settings.stasis_app}")
    print(f"🌐 External Media: {settings.external_media_host}:{settings.external_media_port}")
    
    # Show advanced features if using OpenAI
    if current_provider == 'openai':
        print(f"🎙️ Voice Interruption: {'✅ Enabled' if settings.enable_voice_interruption else '❌ Disabled'}")
        print(f"🔇 Noise Cancellation: {'✅ Enabled' if settings.enable_noise_cancellation else '❌ Disabled'}")
    
    print("="*80)
    
    # Run the server
    uvicorn.run(
        "src.run_realtime_server:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower() if hasattr(settings, 'log_level') else "info",
        reload=False,  # Set to True for development
        access_log=True
    )


if __name__ == "__main__":
    main()