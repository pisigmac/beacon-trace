# Beacon: Code Map & Architecture

**Version**: 1.0.2 (with Lineage Features)

Quick reference for finding and modifying features.

---

## Directory Structure

```
beacon-trace/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app setup, routes, WebSocket
│   │   ├── models.py          # Pydantic models (Agent, Trace, Alert, etc.)
│   │   ├── database.py        # SQLite connection, schema initialization
│   │   ├── websocket.py       # WebSocket connection manager
│   │   ├── routers/           # API endpoints
│   │   │   ├── traces.py      # POST/GET traces, log steps
│   │   │   ├── agents.py      # GET agents, agent stats
│   │   │   ├── metrics.py     # Prometheus export, summary stats
│   │   │   └── alerts.py      # GET/resolve alerts
│   │   └── services/
│   │       └── alert_service.py  # Alert detection & Slack webhooks
│   ├── sdk/
│   │   ├── python/            # Python SDK (decorator + raw API)
│   │   │   └── beacon/
│   │   │       ├── __init__.py
│   │   │       ├── tracer.py  # BeaconTracer class
│   │   │       └── decorator.py # @trace decorator
│   │   └── typescript/        # TypeScript SDK (wrapper + raw API)
│   │       └── src/
│   │           ├── index.ts
│   │           └── tracer.ts
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React + Vite dashboard
│   ├── src/
│   │   ├── main.tsx          # Entry point
│   │   ├── App.tsx           # Root component
│   │   ├── index.css         # Global styles (Tailwind)
│   │   ├── types.ts          # TypeScript interfaces
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.tsx # Main dashboard layout
│   │   │   ├── MissionControl.tsx # Agent grid
│   │   │   ├── CostTrend.tsx # 7-day cost chart
│   │   │   ├── ActivityBars.tsx # 24-hour activity
│   │   │   ├── AlertPanel.tsx # Alert list
│   │   │   └── TraceExplorer.tsx # Trace table
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useWebSocket.ts # WebSocket connection
│   │   │   └── useApi.ts     # API calls
│   │   ├── pages/            # Page components
│   │   └── types/            # Type definitions
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── examples/
│   ├── python_example.py     # Python SDK usage
│   └── typescript_example.ts # TypeScript SDK usage
│
├── cli/
│   └── beacon-cli.ts         # CLI commands (start, backend, frontend)
│
├── docker-compose.yml        # Docker setup
├── Dockerfile
├── Makefile
├── README.md
└── LICENSE
```

---

## Core Files & Their Responsibilities

### Backend

#### `backend/app/main.py`
**What it does**: FastAPI app initialization, route registration, WebSocket setup

**Key functions**:
- `lifespan()`: Startup/shutdown lifecycle (init DB, start alert monitor)
- `health()`: Health check endpoint
- `websocket_endpoint()`: WebSocket connection handler

**Modify when**:
- Adding new API routes → add `app.include_router()`
- Changing startup behavior → edit `lifespan()`
- Adding CORS origins → modify `CORSMiddleware`

---

#### `backend/app/models.py`
**What it does**: Pydantic data models for all entities

**Key classes**:
- `Agent`: Agent metadata and stats
- `Trace`: Single execution record
- `Step`: Action within a trace
- `Alert`: Alert notification
- `TraceStatus`, `AgentStatus`, `AlertType`, `AlertSeverity`: Enums

**Modify when**:
- Adding new fields to traces → edit `Trace` model
- Adding new alert types → add to `AlertType` enum
- Changing agent metadata → edit `Agent` model

---

#### `backend/app/database.py`
**What it does**: SQLite connection, schema creation, query helpers

**Key functions**:
- `init_db()`: Create tables if not exist
- `get_db()`: Get database connection
- Schema definitions for: agents, traces, steps, alerts

**Modify when**:
- Adding new database tables → add schema in `init_db()`
- Changing table structure → update schema
- Adding indexes → modify schema

---

#### `backend/app/websocket.py`
**What it does**: WebSocket connection management

**Key class**:
- `ConnectionManager`: Manages active WebSocket connections, broadcasts messages

**Key methods**:
- `connect()`: Add new connection
- `disconnect()`: Remove connection
- `broadcast()`: Send message to all connected clients

**Modify when**:
- Changing broadcast format → edit `broadcast()`
- Adding connection filtering → modify `connect()`

---

#### `backend/app/routers/traces.py`
**What it does**: Trace API endpoints

**Key endpoints**:
- `POST /api/v1/traces` → Create new trace
- `GET /api/v1/traces` → List traces (with filters)
- `GET /api/v1/traces/{trace_id}` → Get trace details
- `PUT /api/v1/traces/{trace_id}` → Update trace (add steps, end trace)

**Modify when**:
- Adding trace filtering options → edit `GET /traces`
- Changing trace update logic → edit `PUT /traces/{trace_id}`
- Adding new trace endpoints → add new route

---

#### `backend/app/routers/agents.py`
**What it does**: Agent API endpoints

**Key endpoints**:
- `GET /api/v1/agents` → List all agents
- `GET /api/v1/agents/{agent_id}` → Get agent details
- `GET /api/v1/agents/{agent_id}/stats` → Agent statistics

**Modify when**:
- Adding agent filtering → edit `GET /agents`
- Changing agent stats calculation → edit `/agents/{agent_id}/stats`

---

#### `backend/app/routers/metrics.py`
**What it does**: Prometheus metrics and summary statistics

**Key endpoints**:
- `GET /api/v1/metrics/prometheus` → Prometheus text format
- `GET /api/v1/metrics/summary` → Dashboard summary stats

**Modify when**:
- Adding new Prometheus metrics → edit `prometheus()` function
- Changing summary calculation → edit `summary()` function

---

#### `backend/app/routers/alerts.py`
**What it does**: Alert API endpoints

**Key endpoints**:
- `GET /api/v1/alerts` → List alerts
- `PUT /api/v1/alerts/{alert_id}/resolve` → Mark alert resolved

**Modify when**:
- Adding alert filtering → edit `GET /alerts`
- Changing alert resolution logic → edit `PUT /alerts/{alert_id}/resolve`

---

#### `backend/app/services/alert_service.py`
**What it does**: Alert detection logic and Slack webhook integration

**Key class**:
- `AlertService`: Monitors traces, detects anomalies, sends alerts

**Key methods**:
- `monitor_loop()`: Continuous monitoring task
- `detect_loop()`: Detect infinite loops
- `detect_cost_spike()`: Detect cost anomalies
- `detect_failure_rate()`: Detect high failure rates
- `send_slack_alert()`: Send Slack webhook

**Modify when**:
- Adding new alert types → add detection method
- Changing alert thresholds → edit detection logic
- Changing Slack message format → edit `send_slack_alert()`

---

### Python SDK

#### `backend/sdk/python/beacon/tracer.py`
**What it does**: Core tracer class for manual instrumentation

**Key class**:
- `BeaconTracer`: Main tracer for full control

**Key methods**:
- `start_trace()`: Begin trace
- `log_step()`: Record action
- `end_trace()`: Complete trace

**Modify when**:
- Adding new step types → modify `log_step()`
- Changing trace metadata → edit `start_trace()`
- Adding retry logic → modify HTTP calls

---

#### `backend/sdk/python/beacon/decorator.py`
**What it does**: Decorator for automatic instrumentation

**Key function**:
- `@trace()`: Decorator wrapper

**Modify when**:
- Changing decorator behavior → edit wrapper logic
- Adding automatic metadata extraction → modify decorator

---

### Frontend

#### `frontend/src/App.tsx`
**What it does**: Root React component, routing setup

**Modify when**:
- Adding new pages → add routes
- Changing layout → modify JSX

---

#### `frontend/src/components/Dashboard.tsx`
**What it does**: Main dashboard layout

**Key sections**:
- Live connection badge
- Mission Control grid
- Cost trend chart
- Activity bars
- Alert panel
- Trace explorer

**Modify when**:
- Changing dashboard layout → edit JSX
- Adding new sections → add components

---

#### `frontend/src/components/MissionControl.tsx`
**What it does**: Agent status grid

**Displays**:
- Agent name, status (color-coded)
- Success rate, latency, cost
- Last seen timestamp

**Modify when**:
- Changing agent card layout → edit JSX
- Adding new agent metrics → modify component

---

#### `frontend/src/components/CostTrend.tsx`
**What it does**: 7-day cost chart (Recharts)

**Modify when**:
- Changing chart type → modify Recharts config
- Adding new metrics to chart → edit data processing

---

#### `frontend/src/components/AlertPanel.tsx`
**What it does**: Real-time alert list

**Features**:
- Severity-ranked display
- Color-coded by type
- Resolve button

**Modify when**:
- Changing alert display → edit JSX
- Adding alert actions → modify handlers

---

#### `frontend/src/components/TraceExplorer.tsx`
**What it does**: Filterable trace table

**Features**:
- Filter by agent, status, date range
- Sort by cost, duration, timestamp
- Click to view details

**Modify when**:
- Adding filters → edit filter logic
- Changing table columns → modify JSX
- Adding trace detail view → add modal

---

#### `frontend/src/hooks/useWebSocket.ts`
**What it does**: WebSocket connection management

**Key function**:
- `useWebSocket()`: Hook for WebSocket connection

**Modify when**:
- Changing WebSocket URL → edit connection logic
- Adding message handlers → modify hook

---

#### `frontend/src/hooks/useApi.ts`
**What it does**: API call wrapper

**Key function**:
- `useApi()`: Hook for API requests

**Modify when**:
- Adding new API endpoints → add methods
- Changing error handling → modify hook

---

#### `frontend/src/types.ts`
**What it does**: TypeScript interfaces

**Key types**:
- `Agent`, `Trace`, `Step`, `Alert`, `Metrics`

**Modify when**:
- Adding new fields → update interfaces
- Changing data structure → modify types

---

## Common Tasks & Where to Modify

### Add a New Alert Type

1. **Backend**:
   - `backend/app/models.py`: Add to `AlertType` enum
   - `backend/app/services/alert_service.py`: Add detection method
   - `backend/app/routers/alerts.py`: Update alert response if needed

2. **Frontend**:
   - `frontend/src/components/AlertPanel.tsx`: Add color/icon for new type
   - `frontend/src/types.ts`: Update `Alert` type if needed

---

### Add a New Agent Metric

1. **Backend**:
   - `backend/app/models.py`: Add field to `Agent` model
   - `backend/app/routers/agents.py`: Calculate metric in `/agents/{agent_id}/stats`
   - `backend/app/routers/metrics.py`: Add to Prometheus export if needed

2. **Frontend**:
   - `frontend/src/components/MissionControl.tsx`: Display metric on agent card
   - `frontend/src/types.ts`: Update `Agent` type

---

### Add a New Dashboard Chart

1. **Backend**:
   - `backend/app/routers/metrics.py`: Add data endpoint

2. **Frontend**:
   - `frontend/src/components/Dashboard.tsx`: Add chart component
   - Create new component (e.g., `frontend/src/components/NewChart.tsx`)
   - `frontend/src/hooks/useApi.ts`: Add API call if needed

---

### Change Trace Storage Format

1. **Backend**:
   - `backend/app/database.py`: Modify schema
   - `backend/app/models.py`: Update `Trace` model
   - `backend/app/routers/traces.py`: Update trace creation/update logic

2. **Frontend**:
   - `frontend/src/types.ts`: Update `Trace` type
   - `frontend/src/components/TraceExplorer.tsx`: Update display

---

### Add Slack Alert Customization

1. **Backend**:
   - `backend/app/services/alert_service.py`: Modify `send_slack_alert()` method
   - Add environment variables if needed

---

### Add New API Endpoint

1. **Backend**:
   - Create new router file in `backend/app/routers/` or add to existing
   - `backend/app/main.py`: Register router with `app.include_router()`
   - `backend/app/models.py`: Add request/response models

2. **Frontend**:
   - `frontend/src/hooks/useApi.ts`: Add API call
   - `frontend/src/types.ts`: Add types
   - Create component to use endpoint

---

### Modify Alert Thresholds

**File**: `backend/app/services/alert_service.py`

**Key thresholds**:
- Loop detection: `>5 runs in 10 min, <2s avg duration`
- Cost spike: `>$5 in 1 hour`
- Failure rate: `>50% in 1 hour`
- Stall: `>5 minutes running`

Edit the detection methods to change thresholds.

---

### Change WebSocket Broadcast Format

1. **Backend**:
   - `backend/app/websocket.py`: Modify `broadcast()` method
   - `backend/app/routers/traces.py`: Change what data is broadcast

2. **Frontend**:
   - `frontend/src/hooks/useWebSocket.ts`: Update message handler
   - Components using WebSocket: Update data processing

---

### Add Database Query

1. **Backend**:
   - `backend/app/database.py`: Add query function
   - Use in routers or services

---

## Database Schema

### agents table
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT,
    framework TEXT,
    model TEXT,
    created_at TIMESTAMP,
    last_seen TIMESTAMP,
    total_runs INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    total_cost_usd REAL,
    total_latency_ms INTEGER
)
```

### traces table
```sql
CREATE TABLE traces (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    status TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_ms INTEGER,
    total_tokens INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    cost_usd REAL,
    metadata TEXT,
    error_message TEXT,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
)
```

### steps table
```sql
CREATE TABLE steps (
    id TEXT PRIMARY KEY,
    trace_id TEXT,
    step_number INTEGER,
    type TEXT,
    timestamp TIMESTAMP,
    duration_ms INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL,
    tool_name TEXT,
    model TEXT,
    latency_ms INTEGER,
    status TEXT,
    error TEXT,
    FOREIGN KEY (trace_id) REFERENCES traces(id)
)
```

### alerts table
```sql
CREATE TABLE alerts (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    type TEXT,
    severity TEXT,
    message TEXT,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved BOOLEAN,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
)
```

---

## API Endpoints Reference

### Traces
- `POST /api/v1/traces` → Create trace
- `GET /api/v1/traces` → List traces
- `GET /api/v1/traces/{trace_id}` → Get trace
- `PUT /api/v1/traces/{trace_id}` → Update trace

### Agents
- `GET /api/v1/agents` → List agents
- `GET /api/v1/agents/{agent_id}` → Get agent
- `GET /api/v1/agents/{agent_id}/stats` → Agent stats

### Metrics
- `GET /api/v1/metrics/prometheus` → Prometheus export
- `GET /api/v1/metrics/summary` → Dashboard summary

### Alerts
- `GET /api/v1/alerts` → List alerts
- `PUT /api/v1/alerts/{alert_id}/resolve` → Resolve alert

### WebSocket
- `WS /ws` → WebSocket connection

### Health
- `GET /health` → Health check

---

## Environment Variables

**Backend**:
- `BEACON_PORT`: Backend port (default: 8000)
- `BEACON_SLACK_WEBHOOK`: Slack webhook URL

**Frontend**:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:8000/ws)

---

## Dependencies

**Backend** (`backend/requirements.txt`):
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- pydantic==2.5.0
- python-multipart==0.0.6

**Frontend** (`frontend/package.json`):
- react@18
- typescript@5
- vite
- tailwindcss
- recharts (charts)

---

## Running Tests

```bash
# Backend tests (if any)
pytest backend/

# Frontend tests (if any)
npm test --prefix frontend
```

---

## Build & Deploy

```bash
# Backend
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --port 8000

# Frontend
cd frontend
npm install
npm run build
npm run dev
```

---

## Quick Reference: File Locations

| Task | File |
|------|------|
| Add alert type | `backend/app/models.py`, `backend/app/services/alert_service.py` |
| Add agent metric | `backend/app/models.py`, `backend/app/routers/agents.py` |
| Add dashboard chart | `frontend/src/components/Dashboard.tsx` |
| Change alert threshold | `backend/app/services/alert_service.py` |
| Add API endpoint | `backend/app/routers/*.py`, `backend/app/main.py` |
| Change WebSocket format | `backend/app/websocket.py`, `frontend/src/hooks/useWebSocket.ts` |
| Modify Slack alerts | `backend/app/services/alert_service.py` |
| Add database table | `backend/app/database.py` |
| Change UI layout | `frontend/src/components/*.tsx` |
| Add TypeScript type | `frontend/src/types.ts` |


---

## New Features Added (Lineage Integration)

### Parent Task (Trace Lineage)
**Files Modified:**
- `backend/app/models.py`: Added `parent_trace_id` to Trace, TraceCreate, TraceUpdate
- `backend/app/database.py`: Added `parent_trace_id` column with foreign key
- `backend/sdk/python/beacon/tracer.py`: `start_trace()` accepts `parent_trace_id`
- `backend/app/routers/traces.py`: Filter by parent_trace_id, new `/children` endpoint
- `frontend/src/types.ts`: Added `parent_trace_id` to Trace type
- `frontend/src/components/TraceTree.tsx`: NEW - Hierarchical trace view

**New Endpoints:**
- `GET /api/v1/traces?parent_trace_id={id}` - Get child traces
- `GET /api/v1/traces/{trace_id}/children` - Get direct children
- `GET /api/v1/traces/{trace_id}/tree` - Get full hierarchy

### Tool Calls Metadata
**Files Modified:**
- `backend/app/models.py`: Enhanced Step with `tool_status`, `tool_response_code`, `tool_error`
- `backend/sdk/python/beacon/tracer.py`: `log_step()` accepts tool metadata
- `frontend/src/types.ts`: Added tool fields to Step type
- `frontend/src/components/TraceExplorer.tsx`: Display tool info

**New Step Fields:**
- `tool_status: str` - "ok", "error", "timeout", "rate_limited"
- `tool_response_code: Optional[int]` - HTTP status code
- `tool_error: Optional[str]` - Error message from tool

### Retry Count
**Files Modified:**
- `backend/app/models.py`: Added `retry_count`, `retry_history` to Step and Trace
- `backend/app/database.py`: Added `retry_count` column to traces
- `backend/sdk/python/beacon/tracer.py`: `log_step()` and `end_trace()` accept retry data
- `backend/app/routers/traces.py`: Filter by `retry_count_min`
- `backend/app/routers/metrics.py`: NEW endpoint `/retry-distribution`
- `frontend/src/components/RetryChart.tsx`: NEW - Retry distribution chart

**New Endpoints:**
- `GET /api/v1/metrics/retry-distribution` - Retry histogram

### First Failure Boundary
**Files Modified:**
- `backend/app/models.py`: Added `first_failure_step_number`, `first_failure_reason` to Trace
- `backend/app/database.py`: Added failure columns to traces
- `backend/sdk/python/beacon/tracer.py`: `end_trace()` accepts failure info
- `backend/app/routers/traces.py`: Filter by `first_failure_step`
- `frontend/src/types.ts`: Added failure fields to Trace type
- `frontend/src/components/TraceExplorer.tsx`: Show failure timeline

**New Trace Fields:**
- `first_failure_step_number: Optional[int]` - Step number where failure occurred
- `first_failure_reason: Optional[str]` - Reason for failure

### New Alert Types
**Files Modified:**
- `backend/app/models.py`: Added `EXCESSIVE_RETRIES`, `TOOL_FAILURE` to AlertType enum
- `backend/app/services/alert_service.py`: NEW methods `check_excessive_retries()`, `check_tool_failures()`

**New Alerts:**
- `excessive_retries` (high): >5 retries per trace or >3 per step
- `tool_failure` (high): >50% tool call failure rate in 1 hour

### Migration
**Files Added:**
- `backend/migrate.py` - Migration script to add new columns to existing databases

**Usage:**
```bash
python backend/migrate.py
```

### Frontend Components
**New Files:**
- `frontend/src/components/TraceExplorer.tsx` - Filterable trace table with detail view
- `frontend/src/components/RetryChart.tsx` - Retry distribution histogram
- `frontend/src/components/TraceTree.tsx` - Hierarchical trace tree view

**Updated Files:**
- `frontend/src/pages/Dashboard.tsx` - Integrated new components
- `frontend/src/types.ts` - Added new types for all features

### Database Indexes
Added for performance:
- `idx_traces_parent` on `parent_trace_id`
- `idx_traces_retry` on `retry_count`
