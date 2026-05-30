from fastapi import APIRouter, Response
from typing import List, Dict, Any
from datetime import datetime, timedelta

from backend.app.database import get_db
from backend.app.models import MetricsSummary

router = APIRouter()

@router.get("/summary", response_model=MetricsSummary)
def get_summary():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM agents")
    total_agents = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*), SUM(cost_usd) FROM traces 
        WHERE started_at > datetime('now', '-1 day')
    """)
    row = cursor.fetchone()
    total_traces_24h = row[0] or 0
    total_cost_24h = row[1] or 0.0

    cursor.execute("""
        SELECT AVG(CASE WHEN status = 'success' THEN 1.0 ELSE 0.0 END)
        FROM traces WHERE started_at > datetime('now', '-7 days')
    """)
    avg_success_rate = (cursor.fetchone()[0] or 0.0) * 100

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = 0")
    active_alerts = cursor.fetchone()[0]

    cursor.execute("""
        SELECT agent_id, SUM(cost_usd) as cost FROM traces 
        WHERE started_at > datetime('now', '-7 days')
        GROUP BY agent_id ORDER BY cost DESC LIMIT 5
    """)
    top_agents = [{"agent_id": r[0], "cost_usd": r[1]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT strftime('%H', started_at) as hour, COUNT(*) as count
        FROM traces WHERE started_at > datetime('now', '-1 day')
        GROUP BY hour ORDER BY hour
    """)
    hourly = [{"hour": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT date(started_at) as day, SUM(cost_usd) as cost
        FROM traces WHERE started_at > datetime('now', '-7 days')
        GROUP BY day ORDER BY day
    """)
    cost_trend = [{"day": r[0], "cost_usd": r[1]} for r in cursor.fetchall()]

    conn.close()

    return {
        "total_agents": total_agents,
        "total_traces_24h": total_traces_24h,
        "total_cost_24h": round(total_cost_24h, 4),
        "avg_success_rate": round(avg_success_rate, 1),
        "active_alerts": active_alerts,
        "top_agents_by_cost": top_agents,
        "hourly_activity": hourly,
        "cost_trend": cost_trend
    }

@router.get("/agent/{agent_id}")
def get_agent_metrics(agent_id: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COUNT(*) as total_runs,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successes,
            AVG(duration_ms) as avg_latency,
            SUM(cost_usd) as total_cost,
            AVG(total_tokens) as avg_tokens
        FROM traces WHERE agent_id = ? AND started_at > datetime('now', '-7 days')
    """, (agent_id,))
    row = cursor.fetchone()

    conn.close()

    return {
        "agent_id": agent_id,
        "total_runs_7d": row[0],
        "success_rate": round((row[1] / row[0] * 100) if row[0] else 0, 1),
        "avg_latency_ms": round(row[2] or 0, 1),
        "total_cost_7d": round(row[3] or 0, 4),
        "avg_tokens": round(row[4] or 0, 0)
    }

@router.get("/prometheus")
def prometheus_metrics():
    """Export metrics in Prometheus text format for scraping."""
    conn = get_db()
    cursor = conn.cursor()

    lines = []
    lines.append("# HELP beacon_agents_total Total number of registered agents")
    lines.append("# TYPE beacon_agents_total gauge")
    cursor.execute("SELECT COUNT(*) FROM agents")
    lines.append(f'beacon_agents_total {cursor.fetchone()[0]}')

    lines.append("# HELP beacon_traces_total Total number of traces")
    lines.append("# TYPE beacon_traces_total counter")
    cursor.execute("SELECT COUNT(*) FROM traces")
    lines.append(f'beacon_traces_total {cursor.fetchone()[0]}')

    lines.append("# HELP beacon_traces_24h_total Traces in last 24 hours")
    lines.append("# TYPE beacon_traces_24h_total counter")
    cursor.execute("SELECT COUNT(*) FROM traces WHERE started_at > datetime('now', '-1 day')")
    lines.append(f'beacon_traces_24h_total {cursor.fetchone()[0]}')

    lines.append("# HELP beacon_cost_usd_total Total cost in USD")
    lines.append("# TYPE beacon_cost_usd_total counter")
    cursor.execute("SELECT SUM(cost_usd) FROM traces")
    val = cursor.fetchone()[0] or 0
    lines.append(f'beacon_cost_usd_total {val:.6f}')

    lines.append("# HELP beacon_cost_usd_24h_total Cost in last 24 hours")
    lines.append("# TYPE beacon_cost_usd_24h_total counter")
    cursor.execute("SELECT SUM(cost_usd) FROM traces WHERE started_at > datetime('now', '-1 day')")
    val = cursor.fetchone()[0] or 0
    lines.append(f'beacon_cost_usd_24h_total {val:.6f}')

    lines.append("# HELP beacon_success_rate Average success rate (0-1)")
    lines.append("# TYPE beacon_success_rate gauge")
    cursor.execute("""
        SELECT AVG(CASE WHEN status = 'success' THEN 1.0 ELSE 0.0 END)
        FROM traces WHERE started_at > datetime('now', '-7 days')
    """)
    val = cursor.fetchone()[0] or 0
    lines.append(f'beacon_success_rate {val:.4f}')

    lines.append("# HELP beacon_alerts_active Number of unresolved alerts")
    lines.append("# TYPE beacon_alerts_active gauge")
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = 0")
    lines.append(f'beacon_alerts_active {cursor.fetchone()[0]}')

    lines.append("# HELP beacon_agent_runs_total Runs per agent")
    lines.append("# TYPE beacon_agent_runs_total counter")
    cursor.execute("SELECT id, total_runs FROM agents")
    for row in cursor.fetchall():
        lines.append(f'beacon_agent_runs_total{{agent_id="{row[0]}"}} {row[1]}')

    lines.append("# HELP beacon_agent_cost_usd_total Cost per agent")
    lines.append("# TYPE beacon_agent_cost_usd_total counter")
    cursor.execute("SELECT id, total_cost_usd FROM agents")
    for row in cursor.fetchall():
        lines.append(f'beacon_agent_cost_usd_total{{agent_id="{row[0]}"}} {row[1]:.6f}')

    conn.close()

    return Response(content="\n".join(lines) + "\n", media_type="text/plain")

@router.get("/retry-distribution")
def get_retry_distribution():
    """Get retry count distribution across traces."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT retry_count, COUNT(*) as count
        FROM traces
        WHERE started_at > datetime('now', '-7 days')
        GROUP BY retry_count
        ORDER BY retry_count
    """)
    
    distribution = [{"retry_count": r[0], "trace_count": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("""
        SELECT AVG(cost_usd) FROM traces
        WHERE retry_count > 0 AND started_at > datetime('now', '-7 days')
    """)
    avg_cost_with_retries = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "distribution": distribution,
        "avg_cost_with_retries": round(avg_cost_with_retries, 4)
    }
