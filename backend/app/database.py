import sqlite3
import json
import zlib
import threading
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".beacon" / "beacon.db"
_db_lock = threading.Lock()

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=10000")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            framework TEXT,
            model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP,
            total_runs INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            avg_latency_ms REAL DEFAULT 0.0,
            total_cost_usd REAL DEFAULT 0.0,
            status TEXT DEFAULT 'healthy'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            duration_ms INTEGER,
            total_tokens INTEGER DEFAULT 0,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0.0,
            steps_compressed BLOB,
            metadata TEXT,
            error_message TEXT,
            parent_trace_id TEXT,
            first_failure_step_number INTEGER,
            first_failure_reason TEXT,
            first_failure_timestamp TIMESTAMP,
            retry_count INTEGER DEFAULT 0,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (parent_trace_id) REFERENCES traces(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolved BOOLEAN DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_agent ON traces(agent_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_started ON traces(started_at);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_parent ON traces(parent_trace_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_retry ON traces(retry_count);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON alerts(resolved);
    """)

    conn.commit()
    conn.close()

def compress_steps(steps: list) -> bytes:
    return zlib.compress(json.dumps(steps).encode(), level=9)

def decompress_steps(data: bytes) -> list:
    return json.loads(zlib.decompress(data).decode())
