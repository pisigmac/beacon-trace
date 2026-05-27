from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db, compress_steps, decompress_steps, _db_lock
from backend.app.models import TraceCreate, TraceUpdate, Trace, Step, TraceStatus

router = APIRouter()

@router.post("/", response_model=Trace)
def create_trace(trace: TraceCreate):
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO agents (id, name, last_seen, total_runs)
            VALUES (?, ?, CURRENT_TIMESTAMP, 0)
        """, (trace.agent_id, trace.agent_id))
        cursor.execute("""
            INSERT INTO traces (id, agent_id, status, metadata)
            VALUES (?, ?, ?, ?)
        """, (trace.id, trace.agent_id, "running",
              __import__('json').dumps(trace.metadata) if trace.metadata else None))
        conn.commit()
        conn.close()

    return {"id": trace.id, "agent_id": trace.agent_id, "status": "running",
            "started_at": datetime.now(), "ended_at": None, "duration_ms": None,
            "total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}

@router.patch("/{trace_id}", response_model=Trace)
def update_trace(trace_id: str, update: TraceUpdate):
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()

        updates = []
        params = []

        if update.status:
            updates.append("status = ?")
            params.append(update.status.value)
        if update.ended_at:
            updates.append("ended_at = ?")
            params.append(update.ended_at)
        if update.duration_ms is not None:
            updates.append("duration_ms = ?")
            params.append(update.duration_ms)
        if update.total_tokens is not None:
            updates.append("total_tokens = ?")
            params.append(update.total_tokens)
        if update.prompt_tokens is not None:
            updates.append("prompt_tokens = ?")
            params.append(update.prompt_tokens)
        if update.completion_tokens is not None:
            updates.append("completion_tokens = ?")
            params.append(update.completion_tokens)
        if update.cost_usd is not None:
            updates.append("cost_usd = ?")
            params.append(update.cost_usd)
        if update.error_message:
            updates.append("error_message = ?")
            params.append(update.error_message)
        if update.steps:
            updates.append("steps_compressed = ?")
            params.append(compress_steps([s.dict() for s in update.steps]))

        if updates:
            params.append(trace_id)
            cursor.execute(f"UPDATE traces SET {', '.join(updates)} WHERE id = ?", params)

            cursor.execute("SELECT agent_id, cost_usd FROM traces WHERE id = ?", (trace_id,))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE agents SET
                        last_seen = CURRENT_TIMESTAMP,
                        total_runs = total_runs + 1,
                        total_cost_usd = total_cost_usd + ?
                    WHERE id = ?
                """, (row[1] or 0.0, row[0]))

        conn.commit()
        conn.close()

    return get_trace(trace_id)

def _row_to_trace(row) -> dict:
    trace = dict(row)
    if trace.get("steps_compressed"):
        trace["steps"] = decompress_steps(trace["steps_compressed"])
        del trace["steps_compressed"]
    if trace.get("metadata") and isinstance(trace["metadata"], str):
        try:
            import json
            trace["metadata"] = json.loads(trace["metadata"])
        except Exception:
            trace["metadata"] = None
    return trace

@router.get("/{trace_id}", response_model=Trace)
def get_trace(trace_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM traces WHERE id = ?", (trace_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Trace not found")

    return _row_to_trace(row)

@router.get("/", response_model=List[Trace])
def list_traces(agent_id: Optional[str] = None, limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()

    if agent_id:
        cursor.execute("""
            SELECT * FROM traces WHERE agent_id = ?
            ORDER BY started_at DESC LIMIT ?
        """, (agent_id, limit))
    else:
        cursor.execute("""
            SELECT * FROM traces ORDER BY started_at DESC LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [_row_to_trace(r) for r in rows]
