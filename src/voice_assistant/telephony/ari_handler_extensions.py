"""
Extensions for RealTimeARIHandler to add transfer and data collection methods.
This file contains the methods that should be added to the RealTimeARIHandler class.
"""

import logging
from typing import Optional, Dict, Any
from ..data.customer_data_manager import InquiryType, Priority, ResolutionStatus

logger = logging.getLogger(__name__)


def add_transfer_methods(handler_instance):
    """Add transfer methods to RealTimeARIHandler instance"""
    
    async def transfer_call_to_agent(channel_id: str, agent_id: str = "agent1") -> Optional[str]:
        """Transfer call to a specific agent"""
        try:
            call_info = handler_instance.active_calls.get(channel_id)
            if not call_info:
                logger.error(f"No active call found for channel: {channel_id}")
                return None
            
            session_id = call_info.get("session_id")
            
            # Record transfer in customer data
            if session_id:
                await handler_instance.customer_data_manager.record_transfer(
                    session_id=session_id,
                    transfer_type="agent",
                    destination=agent_id,
                    reason="Customer requested agent assistance"
                )
            
            # Perform blind transfer
            transfer_id = await handler_instance.call_transfer_handler.blind_transfer(
                channel_id=channel_id,
                destination=agent_id,
                initiated_by="telephonic_bot"
            )
            
            logger.info(f"Transferred call {channel_id} to agent {agent_id}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Failed to transfer call to agent: {e}")
            return None
    
    async def transfer_call_to_queue(channel_id: str, queue_name: str) -> Optional[str]:
        """Transfer call to a queue"""
        try:
            call_info = handler_instance.active_calls.get(channel_id)
            if not call_info:
                logger.error(f"No active call found for channel: {channel_id}")
                return None
            
            session_id = call_info.get("session_id")
            
            # Record transfer in customer data
            if session_id:
                await handler_instance.customer_data_manager.record_transfer(
                    session_id=session_id,
                    transfer_type="queue",
                    destination=queue_name,
                    reason="Transferred to specialized queue"
                )
            
            # Perform queue transfer
            transfer_id = await handler_instance.call_transfer_handler.transfer_to_queue(
                channel_id=channel_id,
                queue_name=queue_name,
                initiated_by="telephonic_bot"
            )
            
            logger.info(f"Transferred call {channel_id} to queue {queue_name}")
            return transfer_id
            
        except Exception as e:
            logger.error(f"Failed to transfer call to queue: {e}")
            return None
    
    async def transfer_call_to_supervisor(channel_id: str) -> Optional[str]:
        """Transfer call to supervisor"""
        return await transfer_call_to_agent(channel_id, "supervisor")
    
    async def update_inquiry_type(channel_id: str, inquiry_type: str, description: str):
        """Update customer inquiry type during call"""
        try:
            call_info = handler_instance.active_calls.get(channel_id)
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
            
            await handler_instance.customer_data_manager.update_inquiry_type(
                session_id=session_id,
                inquiry_type=inquiry_enum,
                description=description,
                priority=Priority.MEDIUM
            )
            
            logger.info(f"Updated inquiry type for {channel_id}: {inquiry_type}")
            
        except Exception as e:
            logger.error(f"Failed to update inquiry type: {e}")
    
    async def add_conversation_note(channel_id: str, note: str, note_type: str = "ai_response"):
        """Add conversation note for customer data"""
        try:
            call_info = handler_instance.active_calls.get(channel_id)
            if not call_info:
                return
            
            session_id = call_info.get("session_id")
            if not session_id:
                return
            
            await handler_instance.customer_data_manager.add_conversation_note(
                session_id=session_id,
                note=note,
                note_type=note_type
            )
            
        except Exception as e:
            logger.error(f"Failed to add conversation note: {e}")
    
    async def set_customer_satisfaction(channel_id: str, rating: int):
        """Set customer satisfaction rating"""
        try:
            call_info = handler_instance.active_calls.get(channel_id)
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
    
    # Bind methods to instance
    handler_instance.transfer_call_to_agent = transfer_call_to_agent
    handler_instance.transfer_call_to_queue = transfer_call_to_queue
    handler_instance.transfer_call_to_supervisor = transfer_call_to_supervisor
    handler_instance.update_inquiry_type = update_inquiry_type
    handler_instance.add_conversation_note = add_conversation_note
    handler_instance.set_customer_satisfaction = set_customer_satisfaction
    
    logger.info("Added transfer and data collection methods to ARI handler")