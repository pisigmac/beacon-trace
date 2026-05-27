import asyncio
import uuid
import os
import json
from datetime import datetime, timedelta
from backend.app.database import get_db, _db_lock
from backend.app.websocket import manager

class AlertService:
    def __init__(self):
        self.interval = 30  # seconds
        self.slack_webhook = os.environ.get("BEACON_SLACK_WEBHOOK", "")

    async def monitor_loop(self):
        while True:
            await asyncio.sleep(self.interval)
            self.check_loops()
            self.check_cost_spikes()
            self.check_failure_rates()
            self.check_stalls()

    def check_loops(self):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, COUNT(*) as cnt, AVG(duration_ms) as avg_dur
            FROM traces 
            WHERE started_at > datetime('now', '-10 minutes')
            GROUP BY agent_id HAVING cnt > 5 AND avg_dur < 2000
        """)

        for row in cursor.fetchall():
            agent_id, cnt, avg_dur = row
            self._create_alert_if_new(
                agent_id, "loop_detected", "high",
                f"Agent {agent_id} executed {cnt} runs in 10min (avg {avg_dur:.0f}ms). Possible loop."
            )

        conn.close()

    def check_cost_spikes(self):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, SUM(cost_usd) as cost
            FROM traces 
            WHERE started_at > datetime('now', '-1 hour')
            GROUP BY agent_id HAVING cost > 5.0
        """)

        for row in cursor.fetchall():
            agent_id, cost = row
            self._create_alert_if_new(
                agent_id, "cost_spike", "critical",
                f"Agent {agent_id} burned ${cost:.2f} in the last hour."
            )

        conn.close()

    def check_failure_rates(self):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT agent_id, 
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as fails
            FROM traces 
            WHERE started_at > datetime('now', '-1 hour')
            GROUP BY agent_id HAVING total > 3
        """)

        for row in cursor.fetchall():
            agent_id, total, fails = row
            rate = fails / total if total else 0
            if rate > 0.5:
                self._create_alert_if_new(
                    agent_id, "failure_rate", "high",
                    f"Agent {agent_id} failure rate: {rate*100:.0f}% ({fails}/{total}) in last hour."
                )

        conn.close()

    def check_stalls(self):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, agent_id, started_at 
            FROM traces 
            WHERE status = 'running' 
            AND started_at < datetime('now', '-5 minutes')
        """)

        for row in cursor.fetchall():
            trace_id, agent_id, started = row
            self._create_alert_if_new(
                agent_id, "stall", "medium",
                f"Trace {trace_id[:8]}... stalled for >5 minutes."
            )

        conn.close()

    def _create_alert_if_new(self, agent_id, alert_type, severity, message):
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM alerts 
            WHERE agent_id = ? AND type = ? AND resolved = 0
            AND created_at > datetime('now', '-1 hour')
        """, (agent_id, alert_type))

        if not cursor.fetchone():
            alert_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO alerts (id, agent_id, type, severity, message)
                VALUES (?, ?, ?, ?, ?)
            """, (alert_id, agent_id, alert_type, severity, message))
            conn.commit()

            # Send Slack notification
            self._send_slack(alert_id, agent_id, alert_type, severity, message)

        conn.close()

    def _send_slack(self, alert_id, agent_id, alert_type, severity, message):
        if not self.slack_webhook:
            return

        try:
            import urllib.request
            import urllib.parse

            color = {"critical": "#FCA5A5", "high": "#FCD34D", "medium": "#85C1E9", "low": "#9CA3AF"}[severity]

            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"Beacon Alert: {alert_type.replace('_', ' ').title()}",
                    "text": message,
                    "fields": [
                        {"title": "Agent", "value": agent_id, "short": True},
                        {"title": "Severity", "value": severity.upper(), "short": True},
                        {"title": "Alert ID", "value": alert_id[:8], "short": True}
                    ],
                    "footer": "Beacon",
                    "ts": int(datetime.now().timestamp())
                }]
            }

            req = urllib.request.Request(
                self.slack_webhook,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # Fail silently — alerts must not break
