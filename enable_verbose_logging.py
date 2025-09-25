#!/usr/bin/env python3
"""
Enable verbose logging for NPCL Voice Assistant to see complete call flow
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_verbose_logging():
    """Setup verbose logging configuration"""
    
    # Set environment variables for detailed logging
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['ENABLE_CALL_LOGGING'] = 'true'
    os.environ['ENABLE_AUDIO_LOGGING'] = 'true'
    os.environ['ENABLE_AI_LOGGING'] = 'true'
    
    # Import and configure logging
    import logging
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers to DEBUG
    loggers_to_debug = [
        'src.voice_assistant.telephony.realtime_ari_handler',
        'src.voice_assistant.ai.openai_realtime_client_enhanced',
        'src.voice_assistant.telephony.external_media_handler',
        'src.voice_assistant.core.session_manager',
        'src.voice_assistant.audio.realtime_audio_processor',
        'uvicorn.access',
        'fastapi'
    ]
    
    for logger_name in loggers_to_debug:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    print("🔍 VERBOSE LOGGING ENABLED")
    print("=" * 60)
    print("📋 You will now see detailed logs for:")
    print("   • 📞 Call start/end events")
    print("   • 🎤 Voice activity detection")
    print("   • 🧠 AI processing steps")
    print("   • 🔊 Audio streaming events")
    print("   • 🌐 External media connections")
    print("   • 📊 Session management")
    print("=" * 60)

if __name__ == "__main__":
    setup_verbose_logging()
    
    # Import and run the main application
    from src.main import main
    sys.exit(main())