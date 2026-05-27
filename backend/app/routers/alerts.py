from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

from backend.app.database import get_db, _db_lock
from backend.app.models import Alert, AlertSeverity, AlertType

router = APIRouter()

@router.get("/", response_model=List[Alert])
def list_alerts(resolved: Optional[bool] = None, agent_id: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if resolved is not None:
        query += " AND resolved = ?"
        params.append(int(resolved))
    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)

    query += " ORDER BY created_at DESC LIMIT 100"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/", response_model=Alert)
def create_alert(agent_id: Optional[str], type: AlertType, severity: AlertSeverity, message: str):
    conn = get_db()
    cursor = conn.cursor()
    alert_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO alerts (id, agent_id, type, severity, message)
        VALUES (?, ?, ?, ?, ?)
    """, (alert_id, agent_id, type.value, severity.value, message))

    conn.commit()
    conn.close()
    return {"id": alert_id, "agent_id": agent_id, "type": type, "severity": severity,
            "message": message, "created_at": datetime.now(), "resolved": False}

@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE alerts SET resolved = 1, resolved_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (alert_id,))
    conn.commit()
    conn.close()
    return {"resolved": True}
