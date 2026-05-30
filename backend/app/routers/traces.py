from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db, compress_steps, decompress_steps, _db_lock
from backend.app.models import TraceCreate, TraceUpdate, Trace, Step, TraceStatus

router = APIRouter()

@router.get("/", response_model=List[Trace])
def list_traces(agent_id: Optional[str] = None, parent_trace_id: Optional[str] = None,
                retry_count_min: int = 0, first_failure_step: Optional[int] = None, limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM traces WHERE 1=1"
    params = []

    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)
    if parent_trace_id:
        query += " AND parent_trace_id = ?"
        params.append(parent_trace_id)
    if retry_count_min > 0:
        query += " AND retry_count >= ?"
        params.append(retry_count_min)
    if first_failure_step is not None:
        query += " AND first_failure_step_number = ?"
        params.append(first_failure_step)

    query += " ORDER BY started_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_trace(r) for r in rows]


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
            INSERT INTO traces (id, agent_id, status, metadata, parent_trace_id)
            VALUES (?, ?, ?, ?, ?)
        """, (trace.id, trace.agent_id, "running",
              __import__('json').dumps(trace.metadata) if trace.metadata else None,
              trace.parent_trace_id))
        conn.commit()
        conn.close()

    return {"id": trace.id, "agent_id": trace.agent_id, "status": "running",
            "started_at": datetime.now(), "ended_at": None, "duration_ms": None,
            "total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0,
            "parent_trace_id": trace.parent_trace_id, "retry_count": 0}

@router.patch("/{trace_id}", response_model=Trace)
def update_trace(trace_id: str, update: TraceUpdate):
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()

        updates = []
        params = []

        if update.status:
            updates.append("status = ?")
            params.append(update.status if isinstance(update.status, str) else update.status.value)
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
        if update.first_failure_step_number is not None:
            updates.append("first_failure_step_number = ?")
            params.append(update.first_failure_step_number)
        if update.first_failure_reason:
            updates.append("first_failure_reason = ?")
            params.append(update.first_failure_reason)
        if update.retry_count is not None:
            updates.append("retry_count = ?")
            params.append(update.retry_count)
        if update.steps:
            updates.append("steps_compressed = ?")
            steps_data = []
            for s in update.steps:
                step_dict = s.dict() if hasattr(s, 'dict') else s
                # Convert datetime to string if needed
                if isinstance(step_dict.get('timestamp'), datetime):
                    step_dict['timestamp'] = step_dict['timestamp'].isoformat()
                steps_data.append(step_dict)
            params.append(compress_steps(steps_data))

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

@router.get("/{trace_id}/children", response_model=List[Trace])
def get_child_traces(trace_id: str, limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM traces WHERE parent_trace_id = ?
        ORDER BY started_at DESC LIMIT ?
    """, (trace_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_trace(r) for r in rows]

@router.get("/{trace_id}/tree")
def get_trace_tree(trace_id: str):
    """Get full trace hierarchy (parent and all descendants)."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get root trace
    cursor.execute("SELECT * FROM traces WHERE id = ?", (trace_id,))
    root = cursor.fetchone()
    if not root:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    root_trace = _row_to_trace(root)
    
    # Get all descendants recursively
    def get_descendants(parent_id):
        cursor.execute("""
            SELECT * FROM traces WHERE parent_trace_id = ?
            ORDER BY started_at
        """, (parent_id,))
        children = []
        for row in cursor.fetchall():
            child = _row_to_trace(row)
            child["children"] = get_descendants(child["id"])
            children.append(child)
        return children
    
    root_trace["children"] = get_descendants(trace_id)
    conn.close()
    
    return root_trace

