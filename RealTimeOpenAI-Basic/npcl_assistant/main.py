#!/usr/bin/env python3
"""
NPCL Voice Assistant Main Application
"""

import asyncio
import logging
import sys
import signal
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NPCLMainApplication:
    """Main application that coordinates Asterisk ARI and Voice Assistant"""
    
    def __init__(self):
        self.running = False
        
    async def start(self):
        """Start the main application"""
        logger.info("Starting NPCL Voice Assistant Application...")
        self.running = True
        
        while self.running:
            await asyncio.sleep(1)

async def main():
    """Main entry point"""
    app = NPCLMainApplication()
    await app.start()

if __name__ == "__main__":
    print("🏢 NPCL Voice Assistant")
    asyncio.run(main())