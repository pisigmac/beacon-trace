# beacon-agent

Local-first observability SDK for AI agents.

Instrument your agent with one decorator and get a live dashboard with traces, costs, and alerts — all running locally.

## Install

```bash
pip install beacon-trace
```

## Usage

```python
from beacon import trace

@trace(agent_id="my-agent", api_url="http://localhost:8000")
def run_agent(prompt: str) -> str:
    # your agent logic
    return result
```

Full control:

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

## Dashboard

Start the Beacon server to see your traces:

```bash
curl -fsSL https://raw.githubusercontent.com/pisigmac/beacon/main/install.sh | bash
beacon start
```

Then open [http://localhost:3000](http://localhost:3000).

## Links

- [GitHub](https://github.com/pisigmac/beacon)
- [Issues](https://github.com/pisigmac/beacon/issues)
