from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from backend.app.routers import traces, agents, metrics, alerts
from backend.app.database import init_db
from backend.app.services.alert_service import AlertService
from backend.app.websocket import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    alert_service = AlertService()
    asyncio.create_task(alert_service.monitor_loop())
    yield

app = FastAPI(
    title="Beacon",
    description="Local-first observability for AI agents",
    version="1.0.2",
    lifespan=lifespan,
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(traces.router, prefix="/api/v1/traces", tags=["traces"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "beacon", "version": "1.0.2"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
