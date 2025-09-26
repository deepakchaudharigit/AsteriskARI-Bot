
# Add this to the start() method in EnhancedRealTimeARIHandler

async def start(self) -> bool:
    """Start the enhanced ARI handler with WebSocket subscription"""
    try:
        logger.info("Starting Enhanced Real-time ARI Handler...")
        
        await self.session_manager.start_cleanup_task()
        
        if not await self.ai_client.connect():
            raise RuntimeError(f"Failed to connect to {self.ai_provider} API")
        
        if not await self.external_media_handler.start_server(
            self.config.external_media_host,
            self.config.external_media_port
        ):
            raise RuntimeError("Failed to start external media server")
        
        # NEW: Start ARI WebSocket connection to register Stasis app
        if not await self._start_ari_websocket():
            raise RuntimeError("Failed to connect to ARI WebSocket")
        
        self.is_running = True
        logger.info("Enhanced Real-time ARI Handler started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start Enhanced ARI Handler: {e}")
        await self.stop()
        return False

async def _start_ari_websocket(self):
    """Start ARI WebSocket connection to register Stasis application"""
    try:
        import websockets
        import base64
        from urllib.parse import urlencode
        
        # Create WebSocket URL with authentication and app subscription
        auth_string = f"{self.config.ari_username}:{self.config.ari_password}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        
        # ARI WebSocket endpoint with app subscription
        ws_url = f"ws://localhost:8088/ari/events?{urlencode({'app': self.config.stasis_app})}"
        
        headers = {
            "Authorization": f"Basic {auth_encoded}"
        }
        
        print(f"🔌 Connecting to ARI WebSocket for Stasis registration...")
        print(f"📱 Subscribing to Stasis app: {self.config.stasis_app}")
        
        # Connect to WebSocket (this registers the Stasis app)
        self.ari_websocket = await websockets.connect(ws_url, extra_headers=headers)
        
        print(f"✅ ARI WebSocket connected - Stasis app registered")
        
        # Start listening for events in background
        asyncio.create_task(self._listen_ari_events())
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to start ARI WebSocket: {e}")
        return False

async def _listen_ari_events(self):
    """Listen for ARI events from WebSocket"""
    try:
        while self.is_running and self.ari_websocket:
            try:
                message = await asyncio.wait_for(self.ari_websocket.recv(), timeout=1.0)
                event = json.loads(message)
                
                # Handle the event using existing handler
                await self.handle_ari_event(event)
                
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                logger.warning("ARI WebSocket connection closed")
                break
                
    except Exception as e:
        logger.error(f"Error listening for ARI events: {e}")
