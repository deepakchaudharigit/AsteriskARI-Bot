#!/usr/bin/env python3
"""
Database setup script for NPCL Telephonic Bot
Creates all required tables and indexes for customer data management.
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_database():
    """Setup complete database schema"""
    
    db_path = project_root / "data" / "npcl_customer_data.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Setting up database: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create customers table
            print("Creating customers table...")
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
            print("Creating inquiries table...")
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
            print("Creating call_records table...")
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
            
            # Create call_logs table for basic logging
            print("Creating call_logs table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS call_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caller_number TEXT,
                    extension TEXT,
                    duration REAL,
                    timestamp REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create transfers table
            print("Creating transfers table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transfers (
                    transfer_id TEXT PRIMARY KEY,
                    source_channel TEXT,
                    destination TEXT,
                    transfer_type TEXT,
                    status TEXT,
                    initiated_by TEXT,
                    timestamp REAL,
                    completed_at REAL,
                    metadata TEXT
                )
            """)
            
            # Create agent_performance table
            print("Creating agent_performance table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    date DATE,
                    calls_handled INTEGER DEFAULT 0,
                    avg_call_duration REAL DEFAULT 0,
                    customer_satisfaction REAL DEFAULT 0,
                    transfers_received INTEGER DEFAULT 0,
                    inquiries_resolved INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create system_metrics table
            print("Creating system_metrics table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp REAL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            print("Creating indexes...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone_number)",
                "CREATE INDEX IF NOT EXISTS idx_customers_type ON customers (customer_type)",
                "CREATE INDEX IF NOT EXISTS idx_inquiries_phone ON inquiries (phone_number)",
                "CREATE INDEX IF NOT EXISTS idx_inquiries_status ON inquiries (resolution_status)",
                "CREATE INDEX IF NOT EXISTS idx_inquiries_type ON inquiries (inquiry_type)",
                "CREATE INDEX IF NOT EXISTS idx_inquiries_created ON inquiries (created_at)",
                "CREATE INDEX IF NOT EXISTS idx_calls_session ON call_records (session_id)",
                "CREATE INDEX IF NOT EXISTS idx_calls_time ON call_records (call_start_time)",
                "CREATE INDEX IF NOT EXISTS idx_calls_phone ON call_records (phone_number)",
                "CREATE INDEX IF NOT EXISTS idx_calls_outcome ON call_records (call_outcome)",
                "CREATE INDEX IF NOT EXISTS idx_logs_caller ON call_logs (caller_number)",
                "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON call_logs (timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_transfers_channel ON transfers (source_channel)",
                "CREATE INDEX IF NOT EXISTS idx_transfers_status ON transfers (status)",
                "CREATE INDEX IF NOT EXISTS idx_agent_perf_agent ON agent_performance (agent_id)",
                "CREATE INDEX IF NOT EXISTS idx_agent_perf_date ON agent_performance (date)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_name ON system_metrics (metric_name)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics (timestamp)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            # Insert sample data
            print("Inserting sample data...")
            
            # Sample customers
            sample_customers = [
                ("9876543210", "John Doe", "NPCL001", "123 Main St, Noida", "CON001", "john@example.com", "en-IN", "residential"),
                ("9876543211", "Jane Smith", "NPCL002", "456 Oak Ave, Greater Noida", "CON002", "jane@example.com", "hi-IN", "commercial"),
                ("9876543212", "राम कुमार", "NPCL003", "789 Park Road, Ghaziabad", "CON003", "ram@example.com", "hi-IN", "residential")
            ]
            
            import time
            current_time = time.time()
            
            for customer in sample_customers:
                cursor.execute("""
                    INSERT OR IGNORE INTO customers 
                    (phone_number, name, customer_id, address, connection_number, email, preferred_language, customer_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, customer + (current_time, current_time))
            
            # Sample agent performance data
            cursor.execute("""
                INSERT OR IGNORE INTO agent_performance 
                (agent_id, date, calls_handled, avg_call_duration, customer_satisfaction, transfers_received, inquiries_resolved)
                VALUES 
                ('agent1', date('now'), 25, 180.5, 4.2, 5, 20),
                ('supervisor', date('now'), 15, 240.0, 4.5, 8, 12),
                ('tech1', date('now'), 18, 300.2, 4.1, 3, 15)
            """)
            
            conn.commit()
            
            # Verify tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"\nDatabase setup complete!")
            print(f"Created {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  - {table[0]}: {count} records")
            
            print(f"\nDatabase location: {db_path}")
            print("Ready for NPCL Telephonic Bot operations!")
            
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("NPCL Telephonic Bot - Database Setup")
    print("=" * 50)
    
    if setup_database():
        print("\n✅ Database setup completed successfully!")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()