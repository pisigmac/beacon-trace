from fastapi import APIRouter, HTTPException
from typing import List, Optional

from backend.app.database import get_db, _db_lock
from backend.app.models import AgentCreate, Agent, AgentStatus

router = APIRouter()

@router.post("/", response_model=Agent)
def create_agent(agent: AgentCreate):
    with _db_lock:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agents (id, name, framework, model, status)
            VALUES (?, ?, ?, ?, ?)
        """, (agent.id, agent.name, agent.framework, agent.model, "healthy"))
        conn.commit()
        conn.close()
    return get_agent(agent.id)

@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Agent not found")
    return dict(row)

@router.get("/", response_model=List[Agent])
def list_agents(status: Optional[AgentStatus] = None):
    conn = get_db()
    cursor = conn.cursor()

    if status:
        cursor.execute("SELECT * FROM agents WHERE status = ? ORDER BY last_seen DESC", (status.value,))
    else:
        cursor.execute("SELECT * FROM agents ORDER BY last_seen DESC")

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/{agent_id}/traces")
def get_agent_traces(agent_id: str, limit: int = 20):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM traces WHERE agent_id = ? ORDER BY started_at DESC LIMIT ?
    """, (agent_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
