import { v4 as uuidv4 } from 'uuid';

export interface Step {
  step_number: number;
  type: string;
  timestamp: string;
  duration_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  tool_name?: string;
  model?: string;
  latency_ms: number;
  status: string;
  error?: string;
  tool_status?: string;
  tool_response_code?: number;
  tool_error?: string;
  retry_count?: number;
  retry_history?: any[];
}

export interface TraceMetadata {
  [key: string]: any;
}

export class BeaconTracer {
  private apiUrl: string;
  private agentId: string;
  private activeTrace: string | null = null;
  private steps: Step[] = [];

  constructor(apiUrl: string = 'http://localhost:8000', agentId: string = 'default') {
    this.apiUrl = apiUrl.replace(/\/$/, '');
    this.agentId = agentId;
  }

  async startTrace(metadata?: TraceMetadata, parentTraceId?: string): Promise<string> {
    const traceId = uuidv4();
    this.activeTrace = traceId;
    this.steps = [];

    try {
      const payload: any = { id: traceId, agent_id: this.agentId, metadata };
      if (parentTraceId) payload.parent_trace_id = parentTraceId;
      
      await fetch(`${this.apiUrl}/api/v1/traces/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch {
      // Fail silently
    }

    return traceId;
  }

  logStep(params: {
    stepType: string;
    toolName?: string;
    model?: string;
    inputTokens?: number;
    outputTokens?: number;
    costUsd?: number;
    latencyMs?: number;
    status?: string;
    error?: string;
    toolStatus?: string;
    toolResponseCode?: number;
    toolError?: string;
    retryCount?: number;
    retryHistory?: any[];
  }): void {
    this.steps.push({
      step_number: this.steps.length + 1,
      type: params.stepType,
      timestamp: new Date().toISOString(),
      duration_ms: params.latencyMs || 0,
      input_tokens: params.inputTokens || 0,
      output_tokens: params.outputTokens || 0,
      cost_usd: params.costUsd || 0,
      tool_name: params.toolName,
      model: params.model,
      latency_ms: params.latencyMs || 0,
      status: params.status || 'ok',
      error: params.error,
      tool_status: params.toolStatus || 'ok',
      tool_response_code: params.toolResponseCode,
      tool_error: params.toolError,
      retry_count: params.retryCount || 0,
      retry_history: params.retryHistory,
    });
  }

  async endTrace(
    status: string = 'success',
    errorMessage?: string,
    firstFailureStepNumber?: number,
    firstFailureReason?: string,
    retryCount?: number
  ): Promise<void> {
    if (!this.activeTrace) return;

    const totalTokens = this.steps.reduce((s, step) => s + step.input_tokens + step.output_tokens, 0);
    const totalCost = this.steps.reduce((s, step) => s + step.cost_usd, 0);
    const calculatedRetryCount = retryCount ?? this.steps.reduce((s, step) => s + (step.retry_count || 0), 0);

    try {
      const payload: any = {
        status,
        ended_at: new Date().toISOString(),
        total_tokens: totalTokens,
        prompt_tokens: this.steps.reduce((s, step) => s + step.input_tokens, 0),
        completion_tokens: this.steps.reduce((s, step) => s + step.output_tokens, 0),
        cost_usd: totalCost,
        steps: this.steps,
        error_message: errorMessage,
        retry_count: calculatedRetryCount,
      };
      
      if (firstFailureStepNumber !== undefined) payload.first_failure_step_number = firstFailureStepNumber;
      if (firstFailureReason) payload.first_failure_reason = firstFailureReason;

      await fetch(`${this.apiUrl}/api/v1/traces/${this.activeTrace}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch {
      // Fail silently
    }

    this.activeTrace = null;
    this.steps = [];
  }

  wrap<T extends (...args: any[]) => any>(fn: T, metadata?: TraceMetadata): T {
    const self = this;
    return (async (...args: any[]) => {
      await self.startTrace(metadata);
      const start = Date.now();
      try {
        const result = await fn(...args);
        await self.endTrace('success');
        return result;
      } catch (error) {
        await self.endTrace('failure', error instanceof Error ? error.message : String(error));
        throw error;
      }
    }) as T;
  }
}
