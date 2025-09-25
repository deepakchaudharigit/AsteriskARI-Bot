"""
Customer Data Manager for NPCL Telephonic Bot
Handles customer data collection, storage, and retrieval during phone conversations.
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InquiryType(Enum):
    """Types of customer inquiries"""
    NEW_CONNECTION = "new_connection"
    BILLING_INQUIRY = "billing_inquiry"
    POWER_OUTAGE = "power_outage"
    TECHNICAL_SUPPORT = "technical_support"
    COMPLAINT = "complaint"
    PAYMENT_ISSUE = "payment_issue"
    METER_READING = "meter_reading"
    DISCONNECTION = "disconnection"
    RECONNECTION = "reconnection"
    GENERAL_INQUIRY = "general_inquiry"


class ResolutionStatus(Enum):
    """Status of inquiry resolution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    TRANSFERRED = "transferred"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    CLOSED = "closed"


class Priority(Enum):
    """Priority levels for inquiries"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


@dataclass
class CustomerInfo:
    """Customer information"""
    phone_number: str
    name: Optional[str] = None
    customer_id: Optional[str] = None
    address: Optional[str] = None
    connection_number: Optional[str] = None
    email: Optional[str] = None
    preferred_language: str = "en-IN"
    customer_type: str = "residential"  # residential, commercial, industrial
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InquiryData:
    """Customer inquiry data"""
    inquiry_id: str
    inquiry_type: InquiryType
    description: str
    priority: Priority = Priority.MEDIUM
    resolution_status: ResolutionStatus = ResolutionStatus.PENDING
    created_at: float = None
    updated_at: float = None
    resolved_at: Optional[float] = None
    assigned_agent: Optional[str] = None
    resolution_notes: Optional[str] = None
    follow_up_date: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['inquiry_type'] = self.inquiry_type.value
        data['priority'] = self.priority.value
        data['resolution_status'] = self.resolution_status.value
        return data


@dataclass
class CallRecord:
    """Complete call record with customer and inquiry data"""
    call_id: str
    session_id: str
    customer_info: CustomerInfo
    inquiry_data: InquiryData
    call_start_time: float
    call_end_time: Optional[float] = None
    call_duration: Optional[float] = None
    agent_id: Optional[str] = None
    transfer_history: List[Dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    satisfaction_rating: Optional[int] = None
    ai_confidence_score: Optional[float] = None
    language_used: str = "en-IN"
    call_outcome: str = "completed"
    
    def __post_init__(self):
        if self.transfer_history is None:
            self.transfer_history = []
    
    def calculate_duration(self):
        """Calculate call duration"""
        if self.call_end_time:
            self.call_duration = self.call_end_time - self.call_start_time
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['customer_info'] = self.customer_info.to_dict()
        data['inquiry_data'] = self.inquiry_data.to_dict()
        return data


class CustomerDataManager:
    """Manages customer data collection and storage"""
    
    def __init__(self, db_path: str = "data/npcl_customer_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage for active sessions
        self.active_sessions: Dict[str, CallRecord] = {}
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Customer Data Manager initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create customers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS customers (
                        phone_number TEXT PRIMARY KEY,
                        name TEXT,
                        customer_id TEXT,
                        address TEXT,
                        connection_number TEXT,
                        email TEXT,
                        preferred_language TEXT DEFAULT 'en-IN',
                        customer_type TEXT DEFAULT 'residential',
                        created_at REAL,
                        updated_at REAL
                    )
                """)
                
                # Create inquiries table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inquiries (
                        inquiry_id TEXT PRIMARY KEY,
                        phone_number TEXT,
                        inquiry_type TEXT,
                        description TEXT,
                        priority TEXT,
                        resolution_status TEXT,
                        created_at REAL,
                        updated_at REAL,
                        resolved_at REAL,
                        assigned_agent TEXT,
                        resolution_notes TEXT,
                        follow_up_date REAL,
                        metadata TEXT,
                        FOREIGN KEY (phone_number) REFERENCES customers (phone_number)
                    )
                """)
                
                # Create call_records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS call_records (
                        call_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        phone_number TEXT,
                        inquiry_id TEXT,
                        call_start_time REAL,
                        call_end_time REAL,
                        call_duration REAL,
                        agent_id TEXT,
                        transfer_history TEXT,
                        conversation_summary TEXT,
                        satisfaction_rating INTEGER,
                        ai_confidence_score REAL,
                        language_used TEXT,
                        call_outcome TEXT,
                        FOREIGN KEY (phone_number) REFERENCES customers (phone_number),
                        FOREIGN KEY (inquiry_id) REFERENCES inquiries (inquiry_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone_number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiries_phone ON inquiries (phone_number)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiries_status ON inquiries (resolution_status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_session ON call_records (session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_time ON call_records (call_start_time)")
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def start_call_session(self, session_id: str, phone_number: str, 
                                language: str = "en-IN") -> str:
        """
        Start a new call session and create call record
        
        Args:
            session_id: Session ID from session manager
            phone_number: Customer phone number
            language: Language preference
            
        Returns:
            Call ID
        """
        try:
            call_id = f"call_{int(time.time())}_{session_id}"
            
            # Get or create customer info
            customer_info = await self.get_customer_info(phone_number)
            if not customer_info:
                customer_info = CustomerInfo(
                    phone_number=phone_number,
                    preferred_language=language
                )
                await self.save_customer_info(customer_info)
            
            # Create initial inquiry
            inquiry_id = f"inquiry_{int(time.time())}_{call_id}"
            inquiry_data = InquiryData(
                inquiry_id=inquiry_id,
                inquiry_type=InquiryType.GENERAL_INQUIRY,
                description="Initial call - inquiry type to be determined",
                priority=Priority.MEDIUM
            )
            
            # Create call record
            call_record = CallRecord(
                call_id=call_id,
                session_id=session_id,
                customer_info=customer_info,
                inquiry_data=inquiry_data,
                call_start_time=time.time(),
                language_used=language
            )
            
            # Store in active sessions
            self.active_sessions[session_id] = call_record
            
            logger.info(f"Started call session: {call_id} for {phone_number}")
            return call_id
            
        except Exception as e:
            logger.error(f"Failed to start call session: {e}")
            raise
    
    async def update_inquiry_type(self, session_id: str, inquiry_type: InquiryType, 
                                description: str, priority: Priority = None):
        """Update inquiry type and description for active session"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            call_record.inquiry_data.inquiry_type = inquiry_type
            call_record.inquiry_data.description = description
            if priority:
                call_record.inquiry_data.priority = priority
            call_record.inquiry_data.updated_at = time.time()
            
            logger.info(f"Updated inquiry type for session {session_id}: {inquiry_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to update inquiry type: {e}")
    
    async def update_customer_info(self, session_id: str, **kwargs):
        """Update customer information during call"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            # Update customer info fields
            for field, value in kwargs.items():
                if hasattr(call_record.customer_info, field):
                    setattr(call_record.customer_info, field, value)
            
            logger.info(f"Updated customer info for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update customer info: {e}")
    
    async def add_conversation_note(self, session_id: str, note: str, 
                                  note_type: str = "general"):
        """Add a note to the conversation"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            # Add note to inquiry metadata
            if 'conversation_notes' not in call_record.inquiry_data.metadata:
                call_record.inquiry_data.metadata['conversation_notes'] = []
            
            call_record.inquiry_data.metadata['conversation_notes'].append({
                'timestamp': time.time(),
                'type': note_type,
                'note': note
            })
            
            call_record.inquiry_data.updated_at = time.time()
            
            logger.debug(f"Added conversation note for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to add conversation note: {e}")
    
    async def record_transfer(self, session_id: str, transfer_type: str, 
                            destination: str, reason: str):
        """Record call transfer information"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            transfer_record = {
                'timestamp': time.time(),
                'transfer_type': transfer_type,
                'destination': destination,
                'reason': reason
            }
            
            call_record.transfer_history.append(transfer_record)
            
            # Update inquiry status
            call_record.inquiry_data.resolution_status = ResolutionStatus.TRANSFERRED
            call_record.inquiry_data.updated_at = time.time()
            
            logger.info(f"Recorded transfer for session {session_id}: {transfer_type} to {destination}")
            
        except Exception as e:
            logger.error(f"Failed to record transfer: {e}")
    
    async def set_resolution_status(self, session_id: str, status: ResolutionStatus, 
                                  resolution_notes: str = None, assigned_agent: str = None):
        """Set inquiry resolution status"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            call_record.inquiry_data.resolution_status = status
            call_record.inquiry_data.updated_at = time.time()
            
            if resolution_notes:
                call_record.inquiry_data.resolution_notes = resolution_notes
            
            if assigned_agent:
                call_record.inquiry_data.assigned_agent = assigned_agent
                call_record.agent_id = assigned_agent
            
            if status == ResolutionStatus.RESOLVED:
                call_record.inquiry_data.resolved_at = time.time()
            
            logger.info(f"Set resolution status for session {session_id}: {status.value}")
            
        except Exception as e:
            logger.error(f"Failed to set resolution status: {e}")
    
    async def end_call_session(self, session_id: str, call_outcome: str = "completed",
                             satisfaction_rating: int = None, ai_confidence: float = None,
                             conversation_summary: str = None):
        """End call session and save to database"""
        try:
            call_record = self.active_sessions.get(session_id)
            if not call_record:
                logger.warning(f"No active session found: {session_id}")
                return
            
            # Update call record
            call_record.call_end_time = time.time()
            call_record.calculate_duration()
            call_record.call_outcome = call_outcome
            
            if satisfaction_rating:
                call_record.satisfaction_rating = satisfaction_rating
            if ai_confidence:
                call_record.ai_confidence_score = ai_confidence
            if conversation_summary:
                call_record.conversation_summary = conversation_summary
            
            # Save to database
            await self.save_call_record(call_record)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info(f"Ended call session: {call_record.call_id}")
            
        except Exception as e:
            logger.error(f"Failed to end call session: {e}")
    
    async def save_customer_info(self, customer_info: CustomerInfo):
        """Save customer information to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                current_time = time.time()
                cursor.execute("""
                    INSERT OR REPLACE INTO customers 
                    (phone_number, name, customer_id, address, connection_number, 
                     email, preferred_language, customer_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_info.phone_number,
                    customer_info.name,
                    customer_info.customer_id,
                    customer_info.address,
                    customer_info.connection_number,
                    customer_info.email,
                    customer_info.preferred_language,
                    customer_info.customer_type,
                    current_time,
                    current_time
                ))
                
                conn.commit()
                logger.debug(f"Saved customer info: {customer_info.phone_number}")
                
        except Exception as e:
            logger.error(f"Failed to save customer info: {e}")
            raise
    
    async def get_customer_info(self, phone_number: str) -> Optional[CustomerInfo]:
        """Get customer information from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT phone_number, name, customer_id, address, connection_number,
                           email, preferred_language, customer_type
                    FROM customers WHERE phone_number = ?
                """, (phone_number,))
                
                row = cursor.fetchone()
                if row:
                    return CustomerInfo(
                        phone_number=row[0],
                        name=row[1],
                        customer_id=row[2],
                        address=row[3],
                        connection_number=row[4],
                        email=row[5],
                        preferred_language=row[6] or "en-IN",
                        customer_type=row[7] or "residential"
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get customer info: {e}")
            return None
    
    async def save_call_record(self, call_record: CallRecord):
        """Save complete call record to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save customer info
                await self.save_customer_info(call_record.customer_info)
                
                # Save inquiry
                cursor.execute("""
                    INSERT OR REPLACE INTO inquiries
                    (inquiry_id, phone_number, inquiry_type, description, priority,
                     resolution_status, created_at, updated_at, resolved_at,
                     assigned_agent, resolution_notes, follow_up_date, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    call_record.inquiry_data.inquiry_id,
                    call_record.customer_info.phone_number,
                    call_record.inquiry_data.inquiry_type.value,
                    call_record.inquiry_data.description,
                    call_record.inquiry_data.priority.value,
                    call_record.inquiry_data.resolution_status.value,
                    call_record.inquiry_data.created_at,
                    call_record.inquiry_data.updated_at,
                    call_record.inquiry_data.resolved_at,
                    call_record.inquiry_data.assigned_agent,
                    call_record.inquiry_data.resolution_notes,
                    call_record.inquiry_data.follow_up_date,
                    json.dumps(call_record.inquiry_data.metadata)
                ))
                
                # Save call record
                cursor.execute("""
                    INSERT OR REPLACE INTO call_records
                    (call_id, session_id, phone_number, inquiry_id, call_start_time,
                     call_end_time, call_duration, agent_id, transfer_history,
                     conversation_summary, satisfaction_rating, ai_confidence_score,
                     language_used, call_outcome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    call_record.call_id,
                    call_record.session_id,
                    call_record.customer_info.phone_number,
                    call_record.inquiry_data.inquiry_id,
                    call_record.call_start_time,
                    call_record.call_end_time,
                    call_record.call_duration,
                    call_record.agent_id,
                    json.dumps(call_record.transfer_history),
                    call_record.conversation_summary,
                    call_record.satisfaction_rating,
                    call_record.ai_confidence_score,
                    call_record.language_used,
                    call_record.call_outcome
                ))
                
                conn.commit()
                logger.info(f"Saved call record: {call_record.call_id}")
                
        except Exception as e:
            logger.error(f"Failed to save call record: {e}")
            raise
    
    async def get_customer_history(self, phone_number: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customer call history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT cr.call_id, cr.call_start_time, cr.call_duration,
                           i.inquiry_type, i.description, i.resolution_status,
                           cr.satisfaction_rating, cr.call_outcome
                    FROM call_records cr
                    JOIN inquiries i ON cr.inquiry_id = i.inquiry_id
                    WHERE cr.phone_number = ?
                    ORDER BY cr.call_start_time DESC
                    LIMIT ?
                """, (phone_number, limit))
                
                rows = cursor.fetchall()
                history = []
                
                for row in rows:
                    history.append({
                        'call_id': row[0],
                        'call_start_time': row[1],
                        'call_duration': row[2],
                        'inquiry_type': row[3],
                        'description': row[4],
                        'resolution_status': row[5],
                        'satisfaction_rating': row[6],
                        'call_outcome': row[7]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Failed to get customer history: {e}")
            return []
    
    def get_active_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about active session"""
        call_record = self.active_sessions.get(session_id)
        return call_record.to_dict() if call_record else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get customer data statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total customers
                cursor.execute("SELECT COUNT(*) FROM customers")
                total_customers = cursor.fetchone()[0]
                
                # Total calls
                cursor.execute("SELECT COUNT(*) FROM call_records")
                total_calls = cursor.fetchone()[0]
                
                # Calls by outcome
                cursor.execute("""
                    SELECT call_outcome, COUNT(*) 
                    FROM call_records 
                    GROUP BY call_outcome
                """)
                calls_by_outcome = dict(cursor.fetchall())
                
                # Inquiries by type
                cursor.execute("""
                    SELECT inquiry_type, COUNT(*) 
                    FROM inquiries 
                    GROUP BY inquiry_type
                """)
                inquiries_by_type = dict(cursor.fetchall())
                
                # Resolution status
                cursor.execute("""
                    SELECT resolution_status, COUNT(*) 
                    FROM inquiries 
                    GROUP BY resolution_status
                """)
                resolution_status = dict(cursor.fetchall())
                
                # Average call duration
                cursor.execute("SELECT AVG(call_duration) FROM call_records WHERE call_duration IS NOT NULL")
                avg_duration = cursor.fetchone()[0] or 0
                
                # Average satisfaction rating
                cursor.execute("SELECT AVG(satisfaction_rating) FROM call_records WHERE satisfaction_rating IS NOT NULL")
                avg_satisfaction = cursor.fetchone()[0] or 0
                
                return {
                    'total_customers': total_customers,
                    'total_calls': total_calls,
                    'active_sessions': len(self.active_sessions),
                    'calls_by_outcome': calls_by_outcome,
                    'inquiries_by_type': inquiries_by_type,
                    'resolution_status': resolution_status,
                    'average_call_duration': avg_duration,
                    'average_satisfaction_rating': avg_satisfaction
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}