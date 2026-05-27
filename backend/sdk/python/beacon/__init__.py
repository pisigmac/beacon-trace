"""Beacon Agent SDK — One decorator, full observability."""
from .tracer import BeaconTracer
from .decorators import trace

__version__ = "1.0.0"
__all__ = ["BeaconTracer", "trace"]
