from .tracer import BeaconTracer

def trace(agent_id: str = "default", api_url: str = "http://localhost:8000"):
    tracer = BeaconTracer(api_url=api_url, agent_id=agent_id)
    return tracer.trace
