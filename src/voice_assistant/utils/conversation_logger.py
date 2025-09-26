"""
Conversation Logger for NPCL Voice Assistant
Captures and logs conversations between Zoiper callers and the AI bot
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import threading
import queue

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Logs conversations between callers and the AI assistant"""
    
    def __init__(self, log_file_path: str = "zoiper_talk.txt"):
        self.log_file_path = Path(log_file_path)
        self.current_session_id: Optional[str] = None
        self.conversation_queue = queue.Queue()
        self.is_logging = False
        self.log_thread: Optional[threading.Thread] = None
        
        # Ensure log file exists
        if not self.log_file_path.exists():
            self.log_file_path.touch()
        
        logger.info(f"Conversation logger initialized: {self.log_file_path}")
    
    def start_logging(self):
        """Start the conversation logging thread"""
        if not self.is_logging:
            self.is_logging = True
            self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
            self.log_thread.start()
            logger.info("Conversation logging started")
    
    def stop_logging(self):
        """Stop the conversation logging thread"""
        if self.is_logging:
            self.is_logging = False
            if self.log_thread:
                self.log_thread.join(timeout=5)
            logger.info("Conversation logging stopped")
    
    def start_session(self, session_id: str, caller_number: str = "Unknown"):
        """Start a new conversation session"""
        self.current_session_id = session_id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        session_header = f"""
=== NEW CONVERSATION SESSION ===
Session ID: {session_id}
Caller: {caller_number}
Started: {timestamp}
Mode: Direct AI Conversation (No Welcome)
=====================================
"""
        
        self._queue_log_entry(session_header)
        print(f"📝 CONVERSATION LOGGING STARTED: {session_id} for caller {caller_number}")
        logger.info(f"Started conversation session: {session_id}")
        
        # Force immediate write to ensure logging is working
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(session_header)
                f.flush()
        except Exception as e:
            print(f"❌ Error writing session header: {e}")
    
    def end_session(self, session_id: str):
        """End the current conversation session"""
        if self.current_session_id == session_id:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            session_footer = f"""
=====================================
Session {session_id} ended: {timestamp}
=====================================

"""
            
            self._queue_log_entry(session_footer)
            self.current_session_id = None
            logger.info(f"Ended conversation session: {session_id}")
    
    def log_caller_message(self, message: str, session_id: str = None):
        """Log a message from the caller"""
        if session_id and session_id != self.current_session_id:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] CALLER: {message.strip()}\n"
        self._queue_log_entry(log_entry)
        print(f"🗣️ CALLER SAID: {message.strip()}")
        logger.debug(f"Logged caller message: {message[:50]}...")
        
        # Force immediate write
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            print(f"❌ Error writing caller message: {e}")
    
    def log_bot_message(self, message: str, session_id: str = None):
        """Log a message from the AI bot"""
        if session_id and session_id != self.current_session_id:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] BOT: {message.strip()}\n"
        self._queue_log_entry(log_entry)
        print(f"🤖 BOT RESPONDED: {message.strip()}")
        logger.debug(f"Logged bot message: {message[:50]}...")
        
        # Force immediate write
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                f.flush()
        except Exception as e:
            print(f"❌ Error writing bot message: {e}")
    
    def log_system_event(self, event: str, session_id: str = None):
        """Log a system event (call start, end, etc.)"""
        if session_id and session_id != self.current_session_id:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] SYSTEM: {event}\n"
        self._queue_log_entry(log_entry)
        logger.debug(f"Logged system event: {event}")
    
    def _queue_log_entry(self, entry: str):
        """Queue a log entry for writing"""
        try:
            self.conversation_queue.put(entry, timeout=1)
        except queue.Full:
            logger.warning("Conversation log queue is full, dropping entry")
    
    def _log_worker(self):
        """Worker thread that writes log entries to file"""
        while self.is_logging:
            try:
                # Get log entry with timeout
                entry = self.conversation_queue.get(timeout=1)
                
                # Write to file
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(entry)
                    f.flush()
                
                self.conversation_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error writing to conversation log: {e}")
    
    def get_conversation_history(self, lines: int = 50) -> str:
        """Get recent conversation history"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                return ''.join(recent_lines)
        except Exception as e:
            logger.error(f"Error reading conversation history: {e}")
            return "Error reading conversation history"
    
    def clear_log(self):
        """Clear the conversation log"""
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write("=== NPCL Voice Assistant - Conversation Log ===\n")
                f.write(f"Log cleared: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            logger.info("Conversation log cleared")
        except Exception as e:
            logger.error(f"Error clearing conversation log: {e}")


# Global conversation logger instance
_conversation_logger: Optional[ConversationLogger] = None


def get_conversation_logger() -> ConversationLogger:
    """Get the global conversation logger instance"""
    global _conversation_logger
    if _conversation_logger is None:
        _conversation_logger = ConversationLogger()
        _conversation_logger.start_logging()
    return _conversation_logger


def log_caller_speech(message: str, session_id: str = None):
    """Convenience function to log caller speech"""
    logger_instance = get_conversation_logger()
    logger_instance.log_caller_message(message, session_id)


def log_bot_response(message: str, session_id: str = None):
    """Convenience function to log bot response"""
    logger_instance = get_conversation_logger()
    logger_instance.log_bot_message(message, session_id)


def log_system_event(event: str, session_id: str = None):
    """Convenience function to log system events"""
    logger_instance = get_conversation_logger()
    logger_instance.log_system_event(event, session_id)


def start_conversation_session(session_id: str, caller_number: str = "Unknown"):
    """Convenience function to start a conversation session"""
    logger_instance = get_conversation_logger()
    logger_instance.start_session(session_id, caller_number)


def end_conversation_session(session_id: str):
    """Convenience function to end a conversation session"""
    logger_instance = get_conversation_logger()
    logger_instance.end_session(session_id)