import { BeaconTracer } from './tracer';

export function trace(agentId: string = 'default', apiUrl: string = 'http://localhost:8000') {
  const tracer = new BeaconTracer(apiUrl, agentId);
  return function <T extends (...args: any[]) => any>(target: T): T {
    return tracer.wrap(target);
  };
}
