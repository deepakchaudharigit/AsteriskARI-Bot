#!/usr/bin/env python3
"""
RTP-based Real-time ARI Server for NPCL Voice Assistant.

This server uses the corrected RTP-based ARI handler that properly implements
Asterisk external media using RTP/UDP instead of WebSocket.

Usage:
    python src/run_rtp_server.py

The server will start on http://localhost:8000 and handle ARI events from Asterisk.
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from voice_assistant.telephony.rtp_ari_handler import create_rtp_ari_app
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_signal_handlers(app_task):
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        app_task.cancel()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point"""
    try:
        # Load settings
        settings = get_settings()
        
        logger.info("🚀 Starting RTP-based NPCL Voice Assistant ARI Server")
        logger.info(f"📡 ARI Base URL: {settings.ari_base_url}")
        logger.info(f"🎯 External Media Host: {settings.external_media_host}")
        logger.info(f"🎵 Audio Format: {settings.audio_format}")
        logger.info(f"🤖 OpenAI Model: {settings.openai_model}")
        
        # Create FastAPI app
        app = create_rtp_ari_app()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True,
            reload=False  # Disable reload in production
        )
        
        # Create and run server
        server = uvicorn.Server(config)
        
        # Set up signal handlers
        app_task = asyncio.create_task(server.serve())
        setup_signal_handlers(app_task)
        
        logger.info("✅ RTP-based ARI Server started successfully")
        logger.info("🌐 Server running at: http://0.0.0.0:8000")
        logger.info("📊 Health check: http://0.0.0.0:8000/health")
        logger.info("📚 API docs: http://0.0.0.0:8000/docs")
        logger.info("🔧 System status: http://0.0.0.0:8000/status")
        
        # Wait for the server task
        await app_task
        
    except asyncio.CancelledError:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("👋 RTP-based ARI Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)