"""
Call Transfer Handler for NPCL Telephonic Bot
Provides comprehensive call transfer capabilities including blind transfer,
attended transfer, and queue management.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import requests

from config.settings import get_settings
from ..utils.error_handler import handle_errors

logger = logging.getLogger(__name__)


class TransferType(Enum):
    """Types of call transfers"""
    BLIND = "blind"
    ATTENDED = "attended"
    QUEUE = "queue"
    CONFERENCE = "conference"


class TransferStatus(Enum):
    """Transfer status enumeration"""
    INITIATED = "initiated"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TransferRequest:
    """Call transfer request information"""
    transfer_id: str
    source_channel: str
    destination: str
    transfer_type: TransferType
    initiated_by: str
    timestamp: float
    status: TransferStatus = TransferStatus.INITIATED
    target_channel: Optional[str] = None
    bridge_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CallTransferHandler:
    """Handles all types of call transfers for the telephonic bot"""
    
    def __init__(self):
        self.settings = get_settings()
        self.ari_base_url = self.settings.ari_base_url
        self.ari_auth = (self.settings.ari_username, self.settings.ari_password)
        
        # Active transfers tracking
        self.active_transfers: Dict[str, TransferRequest] = {}
        
        # Transfer statistics
        self.transfer_stats = {
            "total_transfers": 0,
            "successful_transfers": 0,
            "failed_transfers": 0,
            "blind_transfers": 0,
            "attended_transfers": 0,
            "queue_transfers": 0
        }
        
        logger.info("Call Transfer Handler initialized")
    
    @handle_errors(logger)
    async def blind_transfer(self, channel_id: str, destination: str, 
                           initiated_by: str = "system") -> Optional[str]:
        """
        Perform blind transfer to extension or external number
        
        Args:
            channel_id: Source channel to transfer
            destination: Target extension or number
            initiated_by: Who initiated the transfer
            
        Returns:
            Transfer ID if successful, None if failed
        """
        try:
            transfer_id = f"transfer_{int(time.time())}_{channel_id}"
            
            # Create transfer request
            transfer_request = TransferRequest(
                transfer_id=transfer_id,
                source_channel=channel_id,
                destination=destination,
                transfer_type=TransferType.BLIND,
                initiated_by=initiated_by,
                timestamp=time.time()
            )
            
            self.active_transfers[transfer_id] = transfer_request
            
            # Perform the transfer via ARI
            url = f"{self.ari_base_url}/channels/{channel_id}/redirect"
            data = {
                "endpoint": f"SIP/{destination}",
                "context": "default",
                "extension": destination,
                "priority": 1
            }
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            # Update transfer status
            transfer_request.status = TransferStatus.CONNECTING
            
            # Update statistics
            self.transfer_stats["total_transfers"] += 1
            self.transfer_stats["blind_transfers"] += 1
            
            logger.info(f"Blind transfer initiated: {channel_id} -> {destination}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Blind transfer failed: {e}")
            if transfer_id in self.active_transfers:
                self.active_transfers[transfer_id].status = TransferStatus.FAILED
                self.transfer_stats["failed_transfers"] += 1
            return None
    
    @handle_errors(logger)
    async def attended_transfer(self, channel_id: str, destination: str,
                              initiated_by: str = "system") -> Optional[str]:
        """
        Perform attended transfer with consultation
        
        Args:
            channel_id: Source channel to transfer
            destination: Target extension
            initiated_by: Who initiated the transfer
            
        Returns:
            Transfer ID if successful, None if failed
        """
        try:
            transfer_id = f"transfer_{int(time.time())}_{channel_id}"
            
            # Create transfer request
            transfer_request = TransferRequest(
                transfer_id=transfer_id,
                source_channel=channel_id,
                destination=destination,
                transfer_type=TransferType.ATTENDED,
                initiated_by=initiated_by,
                timestamp=time.time()
            )
            
            self.active_transfers[transfer_id] = transfer_request
            
            # Step 1: Create a bridge for the consultation
            bridge_id = await self._create_bridge(f"consultation_{transfer_id}")
            if not bridge_id:
                raise Exception("Failed to create consultation bridge")
            
            transfer_request.bridge_id = bridge_id
            
            # Step 2: Add original channel to bridge
            await self._add_channel_to_bridge(bridge_id, channel_id)
            
            # Step 3: Originate call to destination
            target_channel = await self._originate_call(destination, bridge_id)
            if not target_channel:
                raise Exception("Failed to originate consultation call")
            
            transfer_request.target_channel = target_channel
            transfer_request.status = TransferStatus.CONNECTING
            
            # Update statistics
            self.transfer_stats["total_transfers"] += 1
            self.transfer_stats["attended_transfers"] += 1
            
            logger.info(f"Attended transfer initiated: {channel_id} -> {destination}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Attended transfer failed: {e}")
            if transfer_id in self.active_transfers:
                self.active_transfers[transfer_id].status = TransferStatus.FAILED
                self.transfer_stats["failed_transfers"] += 1
                # Cleanup bridge if created
                if transfer_request.bridge_id:
                    await self._destroy_bridge(transfer_request.bridge_id)
            return None
    
    @handle_errors(logger)
    async def transfer_to_queue(self, channel_id: str, queue_name: str,
                              initiated_by: str = "system") -> Optional[str]:
        """
        Transfer call to a queue
        
        Args:
            channel_id: Source channel to transfer
            queue_name: Target queue name
            initiated_by: Who initiated the transfer
            
        Returns:
            Transfer ID if successful, None if failed
        """
        try:
            transfer_id = f"transfer_{int(time.time())}_{channel_id}"
            
            # Create transfer request
            transfer_request = TransferRequest(
                transfer_id=transfer_id,
                source_channel=channel_id,
                destination=queue_name,
                transfer_type=TransferType.QUEUE,
                initiated_by=initiated_by,
                timestamp=time.time()
            )
            
            self.active_transfers[transfer_id] = transfer_request
            
            # Map queue names to extensions
            queue_extensions = {
                "customer-service": "1001",
                "technical-support": "1002",
                "billing": "1003",
                "emergency": "1004"
            }
            
            extension = queue_extensions.get(queue_name, "1001")  # Default to customer service
            
            # Redirect to queue extension
            url = f"{self.ari_base_url}/channels/{channel_id}/redirect"
            data = {
                "endpoint": f"Local/{extension}@default",
                "context": "default",
                "extension": extension,
                "priority": 1
            }
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            # Update transfer status
            transfer_request.status = TransferStatus.CONNECTING
            
            # Update statistics
            self.transfer_stats["total_transfers"] += 1
            self.transfer_stats["queue_transfers"] += 1
            
            logger.info(f"Queue transfer initiated: {channel_id} -> {queue_name}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Queue transfer failed: {e}")
            if transfer_id in self.active_transfers:
                self.active_transfers[transfer_id].status = TransferStatus.FAILED
                self.transfer_stats["failed_transfers"] += 1
            return None
    
    @handle_errors(logger)
    async def transfer_to_conference(self, channel_id: str, conference_name: str,
                                   initiated_by: str = "system") -> Optional[str]:
        """
        Transfer call to a conference room
        
        Args:
            channel_id: Source channel to transfer
            conference_name: Conference room name
            initiated_by: Who initiated the transfer
            
        Returns:
            Transfer ID if successful, None if failed
        """
        try:
            transfer_id = f"transfer_{int(time.time())}_{channel_id}"
            
            # Create transfer request
            transfer_request = TransferRequest(
                transfer_id=transfer_id,
                source_channel=channel_id,
                destination=conference_name,
                transfer_type=TransferType.CONFERENCE,
                initiated_by=initiated_by,
                timestamp=time.time()
            )
            
            self.active_transfers[transfer_id] = transfer_request
            
            # Map conference names to extensions
            conference_extensions = {
                "customer-conf": "3000",
                "agent-conf": "3001"
            }
            
            extension = conference_extensions.get(conference_name, "3000")
            
            # Redirect to conference extension
            url = f"{self.ari_base_url}/channels/{channel_id}/redirect"
            data = {
                "endpoint": f"Local/{extension}@default",
                "context": "default",
                "extension": extension,
                "priority": 1
            }
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            # Update transfer status
            transfer_request.status = TransferStatus.CONNECTING
            
            # Update statistics
            self.transfer_stats["total_transfers"] += 1
            
            logger.info(f"Conference transfer initiated: {channel_id} -> {conference_name}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Conference transfer failed: {e}")
            if transfer_id in self.active_transfers:
                self.active_transfers[transfer_id].status = TransferStatus.FAILED
                self.transfer_stats["failed_transfers"] += 1
            return None
    
    @handle_errors(logger)
    async def complete_attended_transfer(self, transfer_id: str) -> bool:
        """
        Complete an attended transfer after consultation
        
        Args:
            transfer_id: Transfer ID to complete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            transfer_request = self.active_transfers.get(transfer_id)
            if not transfer_request or transfer_request.transfer_type != TransferType.ATTENDED:
                logger.error(f"Invalid transfer request: {transfer_id}")
                return False
            
            # Remove the original channel from bridge (completes transfer)
            if transfer_request.bridge_id and transfer_request.source_channel:
                await self._remove_channel_from_bridge(
                    transfer_request.bridge_id, 
                    transfer_request.source_channel
                )
            
            # Update transfer status
            transfer_request.status = TransferStatus.COMPLETED
            self.transfer_stats["successful_transfers"] += 1
            
            logger.info(f"Attended transfer completed: {transfer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete attended transfer: {e}")
            return False
    
    @handle_errors(logger)
    async def cancel_transfer(self, transfer_id: str) -> bool:
        """
        Cancel an active transfer
        
        Args:
            transfer_id: Transfer ID to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            transfer_request = self.active_transfers.get(transfer_id)
            if not transfer_request:
                logger.error(f"Transfer not found: {transfer_id}")
                return False
            
            # Cleanup based on transfer type
            if transfer_request.transfer_type == TransferType.ATTENDED:
                # Destroy consultation bridge
                if transfer_request.bridge_id:
                    await self._destroy_bridge(transfer_request.bridge_id)
                
                # Hangup target channel if exists
                if transfer_request.target_channel:
                    await self._hangup_channel(transfer_request.target_channel)
            
            # Update transfer status
            transfer_request.status = TransferStatus.CANCELLED
            self.transfer_stats["failed_transfers"] += 1
            
            logger.info(f"Transfer cancelled: {transfer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel transfer: {e}")
            return False
    
    # Helper methods for ARI operations
    
    async def _create_bridge(self, bridge_id: str) -> Optional[str]:
        """Create a bridge for attended transfer"""
        try:
            url = f"{self.ari_base_url}/bridges/{bridge_id}"
            data = {"type": "mixing"}
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            logger.debug(f"Created bridge: {bridge_id}")
            return bridge_id
            
        except Exception as e:
            logger.error(f"Failed to create bridge: {e}")
            return None
    
    async def _destroy_bridge(self, bridge_id: str) -> bool:
        """Destroy a bridge"""
        try:
            url = f"{self.ari_base_url}/bridges/{bridge_id}"
            response = requests.delete(url, auth=self.ari_auth, timeout=10)
            
            # Don't raise for 404 - bridge might not exist
            if response.status_code not in [200, 404]:
                response.raise_for_status()
            
            logger.debug(f"Destroyed bridge: {bridge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy bridge: {e}")
            return False
    
    async def _add_channel_to_bridge(self, bridge_id: str, channel_id: str) -> bool:
        """Add channel to bridge"""
        try:
            url = f"{self.ari_base_url}/bridges/{bridge_id}/addChannel"
            data = {"channel": channel_id}
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            logger.debug(f"Added channel {channel_id} to bridge {bridge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add channel to bridge: {e}")
            return False
    
    async def _remove_channel_from_bridge(self, bridge_id: str, channel_id: str) -> bool:
        """Remove channel from bridge"""
        try:
            url = f"{self.ari_base_url}/bridges/{bridge_id}/removeChannel"
            data = {"channel": channel_id}
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            logger.debug(f"Removed channel {channel_id} from bridge {bridge_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove channel from bridge: {e}")
            return False
    
    async def _originate_call(self, destination: str, bridge_id: str) -> Optional[str]:
        """Originate call to destination and add to bridge"""
        try:
            url = f"{self.ari_base_url}/channels"
            data = {
                "endpoint": f"SIP/{destination}",
                "context": "default",
                "extension": destination,
                "priority": 1,
                "app": "bridge",
                "appArgs": bridge_id
            }
            
            response = requests.post(url, json=data, auth=self.ari_auth, timeout=10)
            response.raise_for_status()
            
            channel_data = response.json()
            channel_id = channel_data.get("id")
            
            logger.debug(f"Originated call to {destination}: {channel_id}")
            return channel_id
            
        except Exception as e:
            logger.error(f"Failed to originate call: {e}")
            return None
    
    async def _hangup_channel(self, channel_id: str) -> bool:
        """Hangup a channel"""
        try:
            url = f"{self.ari_base_url}/channels/{channel_id}"
            response = requests.delete(url, auth=self.ari_auth, timeout=10)
            
            # Don't raise for 404 - channel might not exist
            if response.status_code not in [200, 404]:
                response.raise_for_status()
            
            logger.debug(f"Hung up channel: {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hangup channel: {e}")
            return False
    
    # Status and information methods
    
    def get_transfer_info(self, transfer_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific transfer"""
        transfer_request = self.active_transfers.get(transfer_id)
        if not transfer_request:
            return None
        
        return {
            "transfer_id": transfer_request.transfer_id,
            "source_channel": transfer_request.source_channel,
            "destination": transfer_request.destination,
            "transfer_type": transfer_request.transfer_type.value,
            "status": transfer_request.status.value,
            "initiated_by": transfer_request.initiated_by,
            "timestamp": transfer_request.timestamp,
            "target_channel": transfer_request.target_channel,
            "bridge_id": transfer_request.bridge_id,
            "metadata": transfer_request.metadata
        }
    
    def get_active_transfers(self) -> List[Dict[str, Any]]:
        """Get list of all active transfers"""
        return [
            self.get_transfer_info(transfer_id)
            for transfer_id in self.active_transfers.keys()
        ]
    
    def get_transfer_statistics(self) -> Dict[str, Any]:
        """Get transfer statistics"""
        return {
            **self.transfer_stats,
            "active_transfers": len(self.active_transfers),
            "success_rate": (
                self.transfer_stats["successful_transfers"] / 
                self.transfer_stats["total_transfers"] * 100
                if self.transfer_stats["total_transfers"] > 0 else 0
            )
        }
    
    def cleanup_completed_transfers(self, max_age_hours: int = 24):
        """Clean up old completed transfers"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        transfers_to_remove = []
        for transfer_id, transfer_request in self.active_transfers.items():
            if (transfer_request.status in [TransferStatus.COMPLETED, TransferStatus.FAILED, TransferStatus.CANCELLED] and
                current_time - transfer_request.timestamp > max_age_seconds):
                transfers_to_remove.append(transfer_id)
        
        for transfer_id in transfers_to_remove:
            del self.active_transfers[transfer_id]
        
        if transfers_to_remove:
            logger.info(f"Cleaned up {len(transfers_to_remove)} old transfers")