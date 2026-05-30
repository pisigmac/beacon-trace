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

    def start_trace(self, metadata: Optional[Dict[str, Any]] = None, parent_trace_id: Optional[str] = None) -> str:
        trace_id = str(uuid.uuid4())
        self._active_trace = trace_id
        self._steps = []

        try:
            payload = {"id": trace_id, "agent_id": self.agent_id, "metadata": metadata}
            if parent_trace_id:
                payload["parent_trace_id"] = parent_trace_id
            requests.post(
                f"{self.api_url}/api/v1/traces/",
                json=payload,
                timeout=2
            )
        except Exception:
            pass  # Fail silently — observability must not break the agent

        return trace_id

    def log_step(self, step_type: str, tool_name: str = None, model: str = None,
                 input_tokens: int = 0, output_tokens: int = 0, cost_usd: float = 0.0,
                 latency_ms: int = 0, status: str = "ok", error: str = None,
                 tool_status: str = "ok", tool_response_code: int = None, tool_error: str = None,
                 retry_count: int = 0, retry_history: list = None):
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
            "error": error,
            "tool_status": tool_status,
            "tool_response_code": tool_response_code,
            "tool_error": tool_error,
            "retry_count": retry_count,
            "retry_history": retry_history
        })

    def end_trace(self, status: str = "success", error_message: str = None, 
                  first_failure_step_number: int = None, first_failure_reason: str = None,
                  retry_count: int = None):
        if not self._active_trace:
            return

        total_tokens = sum(s["input_tokens"] + s["output_tokens"] for s in self._steps)
        total_cost = sum(s["cost_usd"] for s in self._steps)
        
        if retry_count is None:
            retry_count = sum(s.get("retry_count", 0) for s in self._steps)

        try:
            payload = {
                "status": status,
                "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_tokens": total_tokens,
                "prompt_tokens": sum(s["input_tokens"] for s in self._steps),
                "completion_tokens": sum(s["output_tokens"] for s in self._steps),
                "cost_usd": total_cost,
                "steps": self._steps,
                "error_message": error_message,
                "retry_count": retry_count
            }
            if first_failure_step_number is not None:
                payload["first_failure_step_number"] = first_failure_step_number
            if first_failure_reason:
                payload["first_failure_reason"] = first_failure_reason
            
            resp = requests.patch(
                f"{self.api_url}/api/v1/traces/{self._active_trace}",
                json=payload,
                timeout=2
            )
            if resp.status_code != 200:
                print(f"Error updating trace: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Exception in end_trace: {e}")

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
