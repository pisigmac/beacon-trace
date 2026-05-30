#!/usr/bin/env python3
"""
Comprehensive example demonstrating all lineage features:
- Parent task (trace lineage)
- Tool calls metadata
- Retry count tracking
- First failure boundary
"""

import time
from beacon import BeaconTracer

def main():
    # Initialize tracers
    orchestrator = BeaconTracer(agent_id="orchestrator", api_url="http://localhost:8000")
    worker_a = BeaconTracer(agent_id="worker-a", api_url="http://localhost:8000")
    worker_b = BeaconTracer(agent_id="worker-b", api_url="http://localhost:8000")

    # Start orchestrator trace
    print("Starting orchestrator trace...")
    orchestrator_trace_id = orchestrator.start_trace(metadata={"task": "data_processing"})
    print(f"Orchestrator trace: {orchestrator_trace_id[:8]}")

    # Worker A: Successful with retries
    print("\nStarting worker A (with retries)...")
    worker_a_trace_id = worker_a.start_trace(
        parent_trace_id=orchestrator_trace_id,
        metadata={"task": "fetch_data"}
    )
    
    # Simulate tool call with retry
    worker_a.log_step(
        step_type="tool_call",
        tool_name="api_fetch",
        tool_status="error",
        tool_response_code=429,
        tool_error="Rate limited",
        latency_ms=5000,
        retry_count=1,
        retry_history=[{"attempt": 1, "status": "rate_limited"}]
    )
    time.sleep(0.1)
    
    # Retry succeeds
    worker_a.log_step(
        step_type="tool_call",
        tool_name="api_fetch",
        tool_status="ok",
        tool_response_code=200,
        latency_ms=1200,
        retry_count=0
    )
    time.sleep(0.1)
    
    # Process data with LLM
    worker_a.log_step(
        step_type="llm_call",
        model="gpt-4",
        input_tokens=500,
        output_tokens=200,
        cost_usd=0.008,
        latency_ms=2000
    )
    
    worker_a.end_trace(status="success", retry_count=1)
    print(f"Worker A completed: {worker_a_trace_id[:8]} (1 retry)")

    # Worker B: Failed with first failure boundary
    print("\nStarting worker B (will fail)...")
    worker_b_trace_id = worker_b.start_trace(
        parent_trace_id=orchestrator_trace_id,
        metadata={"task": "validate_data"}
    )
    
    # Step 1: Validation check
    worker_b.log_step(
        step_type="tool_call",
        tool_name="validation_service",
        tool_status="ok",
        tool_response_code=200,
        latency_ms=500
    )
    time.sleep(0.1)
    
    # Step 2: Database query
    worker_b.log_step(
        step_type="tool_call",
        tool_name="database_query",
        tool_status="ok",
        latency_ms=300
    )
    time.sleep(0.1)
    
    # Step 3: FAILURE - External API timeout
    worker_b.log_step(
        step_type="tool_call",
        tool_name="external_api",
        tool_status="error",
        tool_response_code=504,
        tool_error="Gateway timeout",
        latency_ms=30000,
        retry_count=3,
        retry_history=[
            {"attempt": 1, "status": "timeout"},
            {"attempt": 2, "status": "timeout"},
            {"attempt": 3, "status": "timeout"}
        ]
    )
    
    worker_b.end_trace(
        status="failure",
        error_message="External API unavailable",
        first_failure_step_number=3,
        first_failure_reason="External API returned 504 Gateway Timeout after 3 retries",
        retry_count=3
    )
    print(f"Worker B failed: {worker_b_trace_id[:8]} (failed at step 3, 3 retries)")

    # Complete orchestrator
    print("\nCompleting orchestrator...")
    orchestrator.log_step(
        step_type="state_change",
        latency_ms=100
    )
    
    orchestrator.end_trace(
        status="success",
        error_message="Worker B failed but Worker A succeeded"
    )
    print(f"Orchestrator completed: {orchestrator_trace_id[:8]}")

    print("\n✅ All traces logged successfully!")
    print("\nView in dashboard:")
    print("- Trace Tree: Shows orchestrator with 2 worker children")
    print("- Worker A: 1 retry on API call, successful")
    print("- Worker B: Failed at step 3, 3 retries on external API")
    print("- Retry Chart: Shows distribution of retries")
    print("- Alerts: Should trigger for excessive retries on Worker B")

if __name__ == "__main__":
    main()
