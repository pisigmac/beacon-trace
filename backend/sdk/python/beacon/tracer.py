import os
import uuid
import time
import json
import requests
from typing import Optional, Dict, Any, Callable
from functools import wraps

class BeaconTracer:
    def __init__(self, api_url: str = "http://localhost:8000", agent_id: str = "default"):
        self.api_url = api_url.rstrip("/")
        self.agent_id = agent_id
        self._active_trace: Optional[str] = None
        self._steps: list = []

    def start_trace(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        trace_id = str(uuid.uuid4())
        self._active_trace = trace_id
        self._steps = []

        try:
            requests.post(
                f"{self.api_url}/api/v1/traces/",
                json={"id": trace_id, "agent_id": self.agent_id, "metadata": metadata},
                timeout=2
            )
        except Exception:
            pass  # Fail silently — observability must not break the agent

        return trace_id

    def log_step(self, step_type: str, tool_name: str = None, model: str = None,
                 input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0,
                 latency_ms: int = 0, status: str = "ok", error: str = None):
        self._steps.append({
            "step_number": len(self._steps) + 1,
            "type": step_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost_usd,
            "tool_name": tool_name,
            "model": model,
            "latency_ms": latency_ms,
            "status": status,
            "error": error
        })

    def end_trace(self, status: str = "success", error_message: str = None):
        if not self._active_trace:
            return

        total_tokens = sum(s["input_tokens"] + s["output_tokens"] for s in self._steps)
        total_cost = sum(s["cost_usd"] for s in self._steps)

        try:
            requests.patch(
                f"{self.api_url}/api/v1/traces/{self._active_trace}",
                json={
                    "status": status,
                    "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "total_tokens": total_tokens,
                    "prompt_tokens": sum(s["input_tokens"] for s in self._steps),
                    "completion_tokens": sum(s["output_tokens"] for s in self._steps),
                    "cost_usd": total_cost,
                    "steps": self._steps,
                    "error_message": error_message
                },
                timeout=2
            )
        except Exception:
            pass

        self._active_trace = None
        self._steps = []

    def trace(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.start_trace(metadata={"function": func.__name__})
            start = time.time()
            try:
                result = func(*args, **kwargs)
                self.end_trace(status="success")
                return result
            except Exception as e:
                self.end_trace(status="failure", error_message=str(e))
                raise
        return wrapper
