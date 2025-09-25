#!/usr/bin/env python3
"""
NPCL Voice Assistant Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration (keeping your existing setup)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

# Google Gemini Configuration (for future use)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_REALTIME_URL = "wss://api.openai.com/v1/realtime"

# Asterisk ARI Configuration
ASTERISK_ARI_URL = os.getenv('ASTERISK_ARI_URL', 'http://localhost:8088')
ASTERISK_ARI_USERNAME = os.getenv('ASTERISK_ARI_USERNAME', 'asterisk')
ASTERISK_ARI_PASSWORD = os.getenv('ASTERISK_ARI_PASSWORD', 'asterisk')
ASTERISK_APP_NAME = os.getenv('ASTERISK_APP_NAME', 'npcl_assistant')

# Audio Configuration
AUDIO_SAMPLE_RATE = 16000  # Asterisk standard
AUDIO_CHUNK_SIZE = 320     # 20ms at 16kHz
AUDIO_CHANNELS = 1
AUDIO_FORMAT = 'pcm16'

# Performance Settings
ENABLE_PERFORMANCE_LOGGING = os.getenv('ENABLE_PERFORMANCE_LOGGING', 'false').lower() == 'true'
TARGET_RMS = 1000  # Audio normalization target

# NPCL Specific Configuration
NPCL_COMPLAINT_PREFIX = "000"
NPCL_CUSTOMER_NAMES = ["dheeraj", "nidhi", "nikunj"]
NPCL_DEFAULT_COMPLAINT = "0000054321"

# Zoiper/SIP Configuration
SIP_DOMAIN = os.getenv('SIP_DOMAIN', 'localhost')
SIP_PORT = int(os.getenv('SIP_PORT', '5060'))

print(f"Configuration loaded - Asterisk: {ASTERISK_ARI_URL}, App: {ASTERISK_APP_NAME}")