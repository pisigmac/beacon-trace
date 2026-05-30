#!/usr/bin/env python3
"""
Migration script to add lineage features to existing Beacon databases.
Handles schema updates for parent_trace_id, first_failure_*, and retry_count.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".beacon" / "beacon.db"

def migrate():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("Starting migration...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(traces)")
    columns = {row[1] for row in cursor.fetchall()}
    
    # Add parent_trace_id if not exists
    if 'parent_trace_id' not in columns:
        print("Adding parent_trace_id column...")
        cursor.execute("ALTER TABLE traces ADD COLUMN parent_trace_id TEXT")
    
    # Add first_failure_step_number if not exists
    if 'first_failure_step_number' not in columns:
        print("Adding first_failure_step_number column...")
        cursor.execute("ALTER TABLE traces ADD COLUMN first_failure_step_number INTEGER")
    
    # Add first_failure_reason if not exists
    if 'first_failure_reason' not in columns:
        print("Adding first_failure_reason column...")
        cursor.execute("ALTER TABLE traces ADD COLUMN first_failure_reason TEXT")
    
    # Add first_failure_timestamp if not exists
    if 'first_failure_timestamp' not in columns:
        print("Adding first_failure_timestamp column...")
        cursor.execute("ALTER TABLE traces ADD COLUMN first_failure_timestamp TIMESTAMP")
    
    # Add retry_count if not exists
    if 'retry_count' not in columns:
        print("Adding retry_count column...")
        cursor.execute("ALTER TABLE traces ADD COLUMN retry_count INTEGER DEFAULT 0")
    
    # Add indexes
    print("Adding indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_parent ON traces(parent_trace_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traces_retry ON traces(retry_count)")
    
    conn.commit()
    conn.close()
    
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
