<div align="center">

# 🔮 Beacon

**Local-first observability for AI agents**

Your agents are running blind. Turn on the lights.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## The Problem

You shipped an AI agent last week. It runs 800 times a day. You have **zero visibility** into whether it's succeeding, looping, or quietly burning $200/month in API credits.

LangSmith wants your company's credit card. Custom logging means piping `console.log` into a spreadsheet.

**Beacon is a local-first, open-source observability platform built for AI agents.**

---

## What It Does

| Feature | Description |
|---------|-------------|
| **Live WebSocket Dashboard** | Real-time updates — new traces and alerts appear instantly without refresh |
| **Agent Registry** | Auto-discovers and registers agents on first trace |
| **Live Activity Feed** | Real-time stream of agent runs with status and cost |
| **Token & Cost Tracking** | Per-agent dollar cost tracking with budget alerts |
| **Success/Failure Trends** | 7-day rolling success rates |
| **Loop & Stall Detection** | Alerts when an agent cycles without progress or stalls |
| **Slack Alert Integration** | Critical alerts pushed to your Slack channel |
| **Prometheus Export** | `/api/v1/metrics/prometheus` endpoint for Grafana scraping |

---

## Quick Start

### 1. Install

```bash
curl -fsSL https://raw.githubusercontent.com/pisigmac/beacon-trace/main/install.sh | bash
```

This clones the repo to `~/.beacon/app`, installs all dependencies, and adds a `beacon` CLI command.

Requires: `git`, `python3` (3.8+), `pip`, `node` (18+), `npm`.

### 2. Start

```bash
beacon start
```

Opens the backend on port 8000 and the dashboard at [http://localhost:3000](http://localhost:3000).

Or use Docker:
```bash
docker-compose up
```

### Manual install (alternative)

```bash
git clone https://github.com/pisigmac/beacon-trace.git
cd beacon-trace
pip install -r backend/requirements.txt
pip install beacon-trace        # or: pip install backend/sdk/python (local)
cd frontend && npm install

# Start backend
uvicorn backend.app.main:app --port 8000

# Start dashboard (separate terminal)
cd frontend && npm run dev
```

### 3. Instrument your agent

Install the SDK:

```bash
pip install beacon-trace
```

**Python — one decorator:**
```python
from beacon import trace

@trace(agent_id="invoice-parser", api_url="http://localhost:8000")
def process_invoice(pdf_path):
    result = run_llm(extract_text(pdf_path))
    return result
```

**Python — full control:**
```python
from beacon import BeaconTracer

tracer = BeaconTracer(agent_id="my-agent", api_url="http://localhost:8000")
tracer.start_trace(metadata={"user_id": "123"})

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

**TypeScript — one wrapper:**
```typescript
import { trace } from 'beacon-agent';

const processInvoice = trace('invoice-parser', 'http://localhost:8000')(
  async (pdfPath: string) => {
    const result = await runLLM(extractText(pdfPath));
    return result;
  }
);
```

---

## CLI Commands

After install, the `beacon` command is available:

```bash
beacon start      # Start backend + dashboard
beacon backend    # Start backend only (port 8000)
beacon frontend   # Start dashboard only (port 3000)
beacon update     # Pull latest and reinstall
```

Environment variables:
```bash
BEACON_PORT=8000                          # Backend port
BEACON_SLACK_WEBHOOK=https://hooks...     # Slack alerts
```

---

## Run the Examples

```bash
# Python
python3 examples/python_example.py

# TypeScript (requires ts-node)
npx ts-node examples/typescript_example.ts
```

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Agent     │────▶│   Beacon     │────▶│  SQLite DB  │
│   (Your     │     │   Collector  │     │  (~/.beacon) │
│   Code)     │     │   FastAPI    │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                    ┌───────┴────────┐
                    ▼                ▼
             ┌──────────┐    ┌──────────────┐
             │WebSocket │    │  Prometheus  │
             │Broadcast │    │  /metrics    │
             └──────────┘    └──────────────┘
                    │
          ┌─────────┴──────────┐
          ▼                    ▼
   ┌─────────────┐    ┌──────────────┐
   │   Slack     │    │  Dashboard   │
   │  Webhooks   │    │  React + Vite│
   └─────────────┘    └──────────────┘
```

- **SQLite locally** — trace data stored at `~/.beacon/beacon.db`, never leaves your machine
- **WebSocket live updates** — dashboard refreshes instantly when traces or alerts arrive
- **Prometheus export** — scrape `/api/v1/metrics/prometheus` with your existing Grafana stack
- **Slack integration** — set `BEACON_SLACK_WEBHOOK` and critical alerts hit your channel
- **Zero-dependency SDK** — fails silently, observability never breaks your agent
- **Compressed storage** — zlib-compressed steps for efficient local storage

---

## Prometheus Integration

Beacon exports standard Prometheus metrics at `/api/v1/metrics/prometheus`:

```
# HELP beacon_agents_total Total number of registered agents
beacon_agents_total 5

# HELP beacon_traces_24h_total Traces in last 24 hours
beacon_traces_24h_total 847

# HELP beacon_cost_usd_24h_total Cost in last 24 hours
beacon_cost_usd_24h_total 12.340000

# HELP beacon_success_rate Average success rate (0-1)
beacon_success_rate 0.9732

# HELP beacon_alerts_active Number of unresolved alerts
beacon_alerts_active 2
```

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'beacon'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics/prometheus'
```

---

## Slack Alerts

1. Create a Slack app and enable Incoming Webhooks: https://api.slack.com/messaging/webhooks
2. Copy your webhook URL
3. Set the environment variable:

```bash
export BEACON_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
uvicorn backend.app.main:app --port 8000
```

Or with Docker:
```bash
BEACON_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL docker-compose up
```

Alerts are color-coded by severity:
- 🔴 **Critical** — cost spikes
- 🟡 **High** — loop detection, failure rate spikes
- 🔵 **Medium** — stalled traces
---

## Dashboard Preview

The dashboard features:
- **Live Connection Badge** — Green "Live" indicator when WebSocket is connected
- **Mission Control Grid** — Live agent health status with color-coded indicators
- **Cost Trend Charts** — 7-day area chart showing dollar burn per day
- **Hourly Activity Bars** — 24-hour run distribution
- **Alert Panel** — Real-time severity-ranked alerts with auto-resolution
- **Trace Explorer** — Filterable table of all executions with token/cost breakdown

---

---

## Alert Types

| Alert | Trigger | Severity |
|-------|---------|----------|
| `loop_detected` | >5 runs in 10 min with <2s avg duration | High |
| `cost_spike` | >$5 spent in 1 hour | Critical |
| `failure_rate` | >50% failures in 1 hour | High |
| `stall` | Trace running >5 minutes | Medium |

---

## Configuration

Environment variables (all optional):

```bash
# Slack webhook for alerts
BEACON_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Frontend — override API and WebSocket URLs
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLite, asyncio, WebSocket
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **SDKs**: Python (decorator + raw API), TypeScript (wrapper + raw API)
- **Observability**: Prometheus text export, Slack webhooks

---

## Why Beacon Over Alternatives?

| | Beacon | LangSmith | Langfuse | Custom Logging |
|---|---|---|---|---|
| **Cost** | Free | $$/seat | $$/seat | Free |
| **Local Data** | Yes | No | No | Yes |
| **Live Dashboard** | WebSocket | Polling | Polling | No |
| **Prometheus** | Built-in | No | No | Build yourself |
| **Slack Alerts** | Built-in | No | No | Build yourself |
| **Loop Detection** | Built-in | No | No | Build yourself |

---

## Roadmap

- [x] WebSocket live updates
- [x] Prometheus/Grafana metrics export
- [x] Slack webhook alerts
- [x] Python SDK (decorator + raw)
- [x] TypeScript SDK (wrapper + raw)
- [ ] Trace diff — compare two traces side-by-side
- [ ] Agent dependency graph visualization
- [ ] OpenTelemetry compatibility layer
- [ ] Discord webhook support
- [x] Published PyPI / npm packages

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built for builders who ship agents and need to see them.**

⭐ Star us if Beacon saves you from a $50 API surprise.
</div>
