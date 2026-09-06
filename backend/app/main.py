"""Local NETRA API: loopback by default; optional NETRA_API_TOKEN gateway key."""
import asyncio
import os
from contextlib import asynccontextmanager
from hmac import compare_digest
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.runtime import Store

def create_app(db_path=None, seed_demo=None):
    @asynccontextmanager
    async def lifespan(application):
        application.state.store = Store(db_path, seed_demo)
        yield
        application.state.store.close()
    application = FastAPI(title="NETRA-X", version="1.0.0", lifespan=lifespan,
        description="Local telemetry workbench. Forecasts are explainable heuristic priorities, not calibrated predictions. Synthetic demo seeding is opt-in.")
    origins = os.getenv("NETRA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000").split(",")
    application.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type", "Authorization"])
    @application.middleware("http")
    async def authentication(request: Request, call_next):
        token = os.getenv("NETRA_API_TOKEN", "")
        if token and request.url.path not in ("/health",) and request.method != "OPTIONS":
            supplied = request.headers.get("authorization", "")
            if not compare_digest(supplied, f"Bearer {token}"):
                return JSONResponse({"detail": "Valid Bearer token required"}, status_code=401)
        return await call_next(request)
    application.include_router(api_router, prefix="/api")
    @application.get("/health")
    def readiness():
        application.state.store.ping()
        return {"status": "ok", "app": "NETRA-X", "version": "1.0.0"}
    @application.websocket("/ws")
    async def websocket(websocket: WebSocket):
        origin = websocket.headers.get("origin")
        token = os.getenv("NETRA_API_TOKEN", "")
        if (origin and origin not in origins) or (token and not compare_digest(websocket.headers.get("authorization", ""), f"Bearer {token}")):
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            while True:
                await websocket.send_json({"type": "telemetry", "payload": application.state.store.telemetry()})
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=2)
                except asyncio.TimeoutError:
                    pass
        except (WebSocketDisconnect, RuntimeError):
            pass
    return application

app = create_app()
