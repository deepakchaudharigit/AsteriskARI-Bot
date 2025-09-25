"""
Enhanced ARI Methods for Call Transfer and Data Collection
Extension methods for the RealTimeARIHandler class.
"""

import logging
from typing import Optional, Dict, Any
from .call_transfer_handler import CallTransferHandler
from ..data.customer_data_manager import InquiryType, Priority, ResolutionStatus

logger = logging.getLogger(__name__)


class EnhancedARIMethods:
    """Mixin class for enhanced ARI functionality"""
    
    # Call Transfer Methods
    
    async def transfer_call_to_agent(self, channel_id: str, agent_id: str = "agent1") -> Optional[str]:
        """Transfer call to a specific agent"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                logger.error(f"No active call found for channel: {channel_id}")
                return None
            
            session_id = call_info.get("session_id")
            
            # Record transfer in customer data
            if session_id:
                await self.customer_data_manager.record_transfer(
                    session_id=session_id,
                    transfer_type="agent",
                    destination=agent_id,
                    reason="Customer requested agent assistance"
                )
            
            # Perform blind transfer
            transfer_id = await self.call_transfer_handler.blind_transfer(
                channel_id=channel_id,
                destination=agent_id,
                initiated_by="telephonic_bot"
            )
            
            logger.info(f"Transferred call {channel_id} to agent {agent_id}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Failed to transfer call to agent: {e}")
            return None
    
    async def transfer_call_to_queue(self, channel_id: str, queue_name: str) -> Optional[str]:
        """Transfer call to a queue"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                logger.error(f"No active call found for channel: {channel_id}")
                return None
            
            session_id = call_info.get("session_id")
            
            # Record transfer in customer data
            if session_id:
                await self.customer_data_manager.record_transfer(
                    session_id=session_id,
                    transfer_type="queue",
                    destination=queue_name,
                    reason="Transferred to specialized queue"
                )
            
            # Perform queue transfer
            transfer_id = await self.call_transfer_handler.transfer_to_queue(
                channel_id=channel_id,
                queue_name=queue_name,
                initiated_by="telephonic_bot"
            )
            
            logger.info(f"Transferred call {channel_id} to queue {queue_name}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Failed to transfer call to queue: {e}")
            return None
    
    async def transfer_call_to_supervisor(self, channel_id: str) -> Optional[str]:
        """Transfer call to supervisor"""
        return await self.transfer_call_to_agent(channel_id, "supervisor")
    
    # Customer Data Methods
    
    async def update_inquiry_type(self, channel_id: str, inquiry_type: str, description: str):
        """Update customer inquiry type during call"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            # Map string to enum
            inquiry_type_map = {
                "billing": InquiryType.BILLING_INQUIRY,
                "outage": InquiryType.POWER_OUTAGE,
                "technical": InquiryType.TECHNICAL_SUPPORT,
                "complaint": InquiryType.COMPLAINT,
                "new_connection": InquiryType.NEW_CONNECTION,
                "payment": InquiryType.PAYMENT_ISSUE
            }
            
            inquiry_enum = inquiry_type_map.get(inquiry_type.lower(), InquiryType.GENERAL_INQUIRY)
            
            await self.customer_data_manager.update_inquiry_type(
                session_id=session_id,
                inquiry_type=inquiry_enum,
                description=description,
                priority=Priority.MEDIUM
            )
            
            logger.info(f"Updated inquiry type for {channel_id}: {inquiry_type}")
            
        except Exception as e:
            logger.error(f"Failed to update inquiry type: {e}")
    
    async def add_conversation_note(self, channel_id: str, note: str, note_type: str = "ai_response"):
        """Add conversation note for customer data"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            await self.customer_data_manager.add_conversation_note(
                session_id=session_id,
                note=note,
                note_type=note_type
            )
            
        except Exception as e:
            logger.error(f"Failed to add conversation note: {e}")
    
    async def set_customer_satisfaction(self, channel_id: str, rating: int):
        """Set customer satisfaction rating"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            # This will be applied when the call ends
            call_info["satisfaction_rating"] = rating
            
            logger.info(f"Set satisfaction rating for {channel_id}: {rating}")
            
        except Exception as e:
            logger.error(f"Failed to set satisfaction rating: {e}")
    
    async def resolve_inquiry(self, channel_id: str, resolution_notes: str, agent_id: str = None):
        """Mark inquiry as resolved"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            await self.customer_data_manager.set_resolution_status(
                session_id=session_id,
                status=ResolutionStatus.RESOLVED,
                resolution_notes=resolution_notes,
                assigned_agent=agent_id
            )
            
            logger.info(f"Marked inquiry as resolved for {channel_id}")
            
        except Exception as e:
            logger.error(f"Failed to resolve inquiry: {e}")
    
    async def escalate_inquiry(self, channel_id: str, escalation_reason: str):
        """Escalate inquiry to supervisor"""
        try:
            call_info = self.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            await self.customer_data_manager.set_resolution_status(
                session_id=session_id,
                status=ResolutionStatus.ESCALATED,
                resolution_notes=f"Escalated: {escalation_reason}"
            )
            
            # Transfer to supervisor
            await self.transfer_call_to_supervisor(channel_id)
            
            logger.info(f"Escalated inquiry for {channel_id}: {escalation_reason}")
            
        except Exception as e:
            logger.error(f"Failed to escalate inquiry: {e}")
    
    # Enhanced call info with customer data
    
    def get_enhanced_call_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced call information including customer data"""
        call_info = self.active_calls.get(channel_id)
        if not call_info:
            return None
        
        session_id = call_info.get("session_id")
        session = self.session_manager.get_session(session_id) if session_id else None
        
        return {
            "call_info": call_info,
            "session_summary": session.get_session_summary() if session else None,
            "external_media": self.external_media_handler.get_connection_info(channel_id),
            "customer_data": self.customer_data_manager.get_active_session_info(session_id) if session_id else None,
            "transfer_stats": self.call_transfer_handler.get_transfer_statistics(),
            "customer_history": await self.customer_data_manager.get_customer_history(
                call_info.get("caller_number", ""), limit=5
            ) if call_info.get("caller_number") else []
        }