# Beacon: Agent Onboarding Guide

**Version**: 1.0.2 (with Lineage Features)

## What is Beacon?

Beacon is a **local-first observability platform** for AI agents. It provides real-time visibility into agent execution, cost tracking, and automated alerting without requiring external services or credit cards.

### Core Problem Solved
- Agents run blind: no visibility into success, loops, or cost
- External solutions (LangSmith, Langfuse) require payment and send data to third parties
- Custom logging is manual and fragmented

### Core Solution
- **Local SQLite database** at `~/.beacon/beacon.db` — data never leaves your machine
- **Real-time WebSocket dashboard** at `http://localhost:3000` — live updates without refresh
- **Zero-dependency SDKs** — fails silently, never breaks your agent
- **Built-in intelligence** — loop detection, cost tracking, failure analysis

---

## Key Concepts

### 1. Agent
A registered AI agent that runs tasks. Each agent has:
- **ID**: Unique identifier (e.g., `invoice-parser`)
- **Name**: Human-readable name
- **Framework**: Optional (e.g., `langchain`, `crewai`)
- **Model**: Optional (e.g., `gpt-4`, `claude-3`)
- **Status**: `healthy`, `warning`, `critical`, or `inactive`
- **Metrics**: success rate, avg latency, total cost, run count

Agents are **auto-discovered** on first trace — no manual registration needed.

### 2. Trace
A single execution of an agent. Each trace contains:
- **ID**: Unique identifier for this run
- **Status**: `success`, `failure`, `running`, or `timeout`
- **Duration**: How long the trace took (ms)
- **Cost**: Total USD spent (LLM calls, API usage)
- **Tokens**: Prompt tokens, completion tokens, total
- **Steps**: Ordered list of actions taken (LLM calls, tool calls, state changes)
- **Metadata**: Custom context (user_id, request_id, etc.)
- **Error**: If failed, the error message

### 3. Step
A single action within a trace. Types include:
- **llm_call**: LLM API call (GPT-4, Claude, etc.)
- **tool_call**: External tool invocation (API, database, etc.)
- **state_change**: Internal state update

Each step records:
- Duration (ms)
- Tokens (input/output)
- Cost (USD)
- Model used
- Status (ok, error)
- Error details if failed

### 4. Alert
Automated notifications when something goes wrong. Types:
- **loop_detected**: Agent cycles >5 times in 10 min with <2s avg duration
- **cost_spike**: >$5 spent in 1 hour
- **failure_rate**: >50% failures in 1 hour
- **latency_spike**: Avg latency increases significantly
- **context_window**: Token usage approaching model limit
- **stall**: Trace running >5 minutes
- **excessive_retries**: >5 retries per trace or >3 per step
- **tool_failure**: >50% tool call failure rate in 1 hour

Severity levels: `low`, `medium`, `high`, `critical`

Alerts can be sent to:
- Dashboard (real-time)
- Slack (via webhook)
- Prometheus (for Grafana)

---

## Advanced Features

### Parent Task (Trace Lineage)
Link child traces to parent traces for multi-agent orchestration:
```python
# Orchestrator agent
orchestrator_trace = tracer.start_trace()

# Worker agents
worker_a_trace = worker_tracer.start_trace(parent_trace_id=orchestrator_trace)
worker_b_trace = worker_tracer.start_trace(parent_trace_id=orchestrator_trace)
```

Dashboard shows trace hierarchy with parent at top and workers as children.

### Tool Calls Metadata
Track tool-specific information:
```python
tracer.log_step(
    step_type="tool_call",
    tool_name="search_api",
    tool_status="ok",
    tool_response_code=200,
    latency_ms=500
)
```

### Retry Tracking
Monitor retry attempts and identify flaky operations:
```python
tracer.log_step(
    step_type="llm_call",
    retry_count=2,
    retry_history=[
        {"attempt": 1, "status": "timeout"},
        {"attempt": 2, "status": "timeout"},
        {"attempt": 3, "status": "success"}
    ]
)
```

### First Failure Boundary
Identify exactly where traces fail:
```python
tracer.end_trace(
    status="failure",
    first_failure_step_number=3,
    first_failure_reason="API rate limit exceeded"
)
```

Dashboard shows failure point with steps before (✅), failure (❌), and after (⊘).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Agent Code                         │
│  (Python decorator or TypeScript wrapper around your logic) │
└────────────────────┬────────────────────────────────────────┘
                     │ (sends traces via HTTP)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Beacon Backend (FastAPI)                       │
│  - Receives traces from SDKs                               │
│  - Stores in SQLite (~/.beacon/beacon.db)                  │
│  - Broadcasts via WebSocket                                │
│  - Monitors for alerts                                     │
│  - Exports Prometheus metrics                              │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │SQLite  │  │WebSocket│ │Prometheus│
    │Database│  │Broadcast│ │Metrics   │
    └────────┘  └────────┘  └──────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
        ┌────────────────────────┐
        │  Dashboard (React)     │
        │  - Live agent status   │
        │  - Cost trends         │
        │  - Alert panel         │
        │  - Trace explorer      │
        └────────────────────────┘
        
        ┌────────────────────────┐
        │  Slack Webhooks        │
        │  - Critical alerts     │
        │  - Color-coded by type │
        └────────────────────────┘
        
        ┌────────────────────────┐
        │  Grafana (optional)    │
        │  - Scrapes Prometheus  │
        │  - Custom dashboards   │
        └────────────────────────┘
```

---

## How to Use Beacon

### Step 1: Start the Backend & Dashboard

```bash
beacon start
```

This starts:
- Backend on `http://localhost:8000`
- Dashboard on `http://localhost:3000`
- SQLite database at `~/.beacon/beacon.db`

Or manually:
```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Step 2: Instrument Your Agent

#### Python (Decorator)
```python
from beacon import trace

@trace(agent_id="invoice-parser", api_url="http://localhost:8000")
def process_invoice(pdf_path):
    result = run_llm(extract_text(pdf_path))
    return result

# Use it normally
process_invoice("invoice.pdf")
```

#### Python (Full Control)
```python
from beacon import BeaconTracer

tracer = BeaconTracer(agent_id="my-agent", api_url="http://localhost:8000")
tracer.start_trace(metadata={"user_id": "123"})

# Do work...
tracer.log_step(
    step_type="llm_call",
    model="gpt-4",
    input_tokens=1200,
    output_tokens=400,
    cost_usd=0.012,
    latency_ms=1200
)

tracer.end_trace(status="success")
```

#### TypeScript (Wrapper)
```typescript
import { trace } from 'beacon-agent';

const processInvoice = trace('invoice-parser', 'http://localhost:8000')(
  async (pdfPath: string) => {
    const result = await runLLM(extractText(pdfPath));
    return result;
  }
);

// Use it normally
await processInvoice("invoice.pdf");
```

### Step 3: View in Dashboard

Open `http://localhost:3000`:
- **Mission Control**: Live agent health grid
- **Cost Trends**: 7-day spending chart
- **Activity**: Hourly run distribution
- **Alerts**: Real-time severity-ranked alerts
- **Trace Explorer**: Filterable table of all executions

---

## Dashboard Features

### Live Connection Badge
Green "Live" indicator when WebSocket is connected. Red when disconnected.

### Mission Control Grid
Color-coded agent status:
- 🟢 **Green (Healthy)**: >90% success rate, normal latency
- 🟡 **Yellow (Warning)**: 70-90% success rate or elevated latency
- 🔴 **Red (Critical)**: <70% success rate or high cost spike
- ⚫ **Gray (Inactive)**: No runs in 24 hours

### Cost Trend Chart
7-day area chart showing daily USD spend per agent. Helps identify cost spikes.

### Hourly Activity Bars
24-hour distribution of agent runs. Identifies peak usage times.

### Alert Panel
Real-time alerts ranked by severity:
- 🔴 **Critical** (red): Cost spikes, immediate action needed
- 🟡 **High** (orange): Loop detection, failure rate spikes
- 🔵 **Medium** (blue): Stalled traces, latency issues
- ⚪ **Low** (gray): Informational

Click to resolve alerts manually.

### Trace Explorer
Filterable table of all traces:
- Agent ID
- Status (success/failure/running)
- Duration
- Cost
- Token usage
- Timestamp

Click a trace to see detailed step breakdown.

---

## Alert Types & Triggers

| Alert | Trigger | Severity | Action |
|-------|---------|----------|--------|
| `loop_detected` | >5 runs in 10 min, <2s avg duration | High | Check agent logic for infinite loops |
| `cost_spike` | >$5 spent in 1 hour | Critical | Review LLM calls, check for runaway costs |
| `failure_rate` | >50% failures in 1 hour | High | Check error logs, review recent changes |
| `latency_spike` | Avg latency increases >50% | High | Check external API performance |
| `context_window` | Token usage >80% of model limit | Medium | Optimize prompts, use summarization |
| `stall` | Trace running >5 minutes | Medium | Check for deadlocks, timeout issues |

---

## Configuration

### Environment Variables

```bash
# Backend port (default: 8000)
BEACON_PORT=8000

# Slack webhook for alerts (optional)
BEACON_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Frontend API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000

# Frontend WebSocket URL (default: ws://localhost:8000/ws)
VITE_WS_URL=ws://localhost:8000/ws
```

### Slack Integration

1. Create a Slack app: https://api.slack.com/messaging/webhooks
2. Enable Incoming Webhooks
3. Copy webhook URL
4. Set environment variable:
   ```bash
   export BEACON_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   beacon start
   ```

Alerts are color-coded:
- 🔴 Red: Critical
- 🟡 Orange: High
- 🔵 Blue: Medium
- ⚪ Gray: Low

---

## Prometheus Integration

Beacon exports metrics at `/api/v1/metrics/prometheus`:

```
beacon_agents_total 5
beacon_traces_24h_total 847
beacon_cost_usd_24h_total 12.34
beacon_success_rate 0.9732
beacon_alerts_active 2
```

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'beacon'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics/prometheus'
```

Then visualize in Grafana.

---

## Data Storage

- **Location**: `~/.beacon/beacon.db` (SQLite)
- **Retention**: Unlimited (local storage)
- **Privacy**: All data stays on your machine
- **Compression**: Steps are zlib-compressed for efficiency

---

## Common Workflows

### Debug a Failed Trace
1. Open Dashboard → Trace Explorer
2. Filter by agent ID and status=failure
3. Click trace to see step-by-step breakdown
4. Check error message in final step

### Investigate Cost Spike
1. Open Dashboard → Cost Trend Chart
2. Identify spike date
3. Go to Trace Explorer, filter by date range
4. Sort by cost descending
5. Review high-cost traces for inefficient LLM calls

### Resolve Loop Detection Alert
1. Check alert in Dashboard → Alert Panel
2. Note agent ID and time window
3. Go to Trace Explorer, filter by agent and time
4. Look for traces with very short duration (<2s)
5. Review agent logic for infinite loops

### Monitor Agent Health
1. Open Dashboard → Mission Control Grid
2. Watch for color changes (green → yellow → red)
3. Click agent to see recent traces
4. Check success rate and latency trends

---

## SDK Behavior

### Failure Modes
- If Beacon backend is unreachable, SDK fails silently
- Traces are not sent, but agent continues running
- No exceptions thrown, no performance impact
- Observability never breaks your agent

### Retry Logic
- SDK retries failed HTTP requests up to 3 times
- Exponential backoff: 100ms, 200ms, 400ms
- Timeout: 5 seconds per request

### Performance Impact
- Minimal: <5ms per trace (async HTTP POST)
- No blocking operations
- Traces sent in background

---

## Troubleshooting

### Dashboard shows "Disconnected"
- Check backend is running: `curl http://localhost:8000/health`
- Check WebSocket URL in browser console
- Verify firewall allows port 8000

### Traces not appearing
- Verify agent_id is set correctly
- Check backend logs: `tail -f ~/.beacon/beacon.log`
- Ensure API URL is correct: `http://localhost:8000`

### High memory usage
- SQLite database growing large
- Clear old traces: `sqlite3 ~/.beacon/beacon.db "DELETE FROM traces WHERE created_at < datetime('now', '-30 days')"`

### Slack alerts not sending
- Verify webhook URL is correct
- Check backend logs for webhook errors
- Test webhook manually: `curl -X POST -H 'Content-type: application/json' --data '{"text":"test"}' YOUR_WEBHOOK_URL`

---

## Next Steps

1. **Start Beacon**: `beacon start`
2. **Instrument your agent**: Add `@trace` decorator or `BeaconTracer`
3. **Run your agent**: Execute normally
4. **View dashboard**: Open `http://localhost:3000`
5. **Set up Slack** (optional): Add webhook for alerts
6. **Monitor trends**: Check cost and success rate daily

---

## Support

- **GitHub**: https://github.com/pisigmac/beacon-trace
- **Issues**: Report bugs on GitHub
- **Examples**: See `examples/` directory for Python and TypeScript samples
