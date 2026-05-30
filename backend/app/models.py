from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    INACTIVE = "inactive"

class TraceStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    TIMEOUT = "timeout"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    LOOP_DETECTED = "loop_detected"
    COST_SPIKE = "cost_spike"
    FAILURE_RATE = "failure_rate"
    LATENCY_SPIKE = "latency_spike"
    CONTEXT_WINDOW = "context_window"
    STALL = "stall"
    EXCESSIVE_RETRIES = "excessive_retries"
    TOOL_FAILURE = "tool_failure"

class AgentCreate(BaseModel):
    id: str
    name: str
    framework: Optional[str] = None
    model: Optional[str] = None

class Agent(BaseModel):
    id: str
    name: str
    framework: Optional[str]
    model: Optional[str]
    created_at: datetime
    last_seen: Optional[datetime]
    total_runs: int
    success_rate: float
    avg_latency_ms: float
    total_cost_usd: float
    status: AgentStatus

class Step(BaseModel):
    step_number: int
    type: str  # llm_call, tool_call, state_change
    timestamp: datetime
    duration_ms: int
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    tool_name: Optional[str] = None
    model: Optional[str] = None
    latency_ms: int = 0
    status: str = "ok"
    error: Optional[str] = None
    tool_status: str = "ok"
    tool_response_code: Optional[int] = None
    tool_error: Optional[str] = None
    retry_count: int = 0
    retry_history: Optional[List[Dict[str, Any]]] = None

class TraceCreate(BaseModel):
    id: str
    agent_id: str
    metadata: Optional[Dict[str, Any]] = None
    parent_trace_id: Optional[str] = None

class TraceUpdate(BaseModel):
    status: Optional[TraceStatus] = None
    ended_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    total_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    steps: Optional[List[Step]] = None
    error_message: Optional[str] = None
    first_failure_step_number: Optional[int] = None
    first_failure_reason: Optional[str] = None
    retry_count: Optional[int] = None

class Trace(BaseModel):
    id: str
    agent_id: str
    status: TraceStatus
    started_at: datetime
    ended_at: Optional[datetime]
    duration_ms: Optional[int]
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float
    steps: Optional[List[Step]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    parent_trace_id: Optional[str] = None
    first_failure_step_number: Optional[int] = None
    first_failure_reason: Optional[str] = None
    retry_count: int = 0

class Alert(BaseModel):
    id: str
    agent_id: Optional[str]
    type: AlertType
    severity: AlertSeverity
    message: str
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved: bool

class MetricsSummary(BaseModel):
    total_agents: int
    total_traces_24h: int
    total_cost_24h: float
    avg_success_rate: float
    active_alerts: int
    top_agents_by_cost: List[Dict[str, Any]]
    hourly_activity: List[Dict[str, Any]]
    cost_trend: List[Dict[str, Any]]
