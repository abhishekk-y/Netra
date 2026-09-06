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
from app.websocket.manager import ws_manager

def create_app(db_path=None, seed_demo=None):
    @asynccontextmanager
    async def lifespan(application):
        application.state.store = Store(db_path, seed_demo)
        yield
        application.state.store.close()
    
    application = FastAPI(
        title="Netra", 
        version="1.0.0", 
        lifespan=lifespan,
        description="Local telemetry workbench. Forecasts are explainable heuristic priorities, not calibrated predictions. Synthetic demo seeding is opt-in."
    )
    
    application.add_middleware(
        CORSMiddleware, 
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"], 
        allow_headers=["*"]
    )
    
    @application.middleware("http")
    async def authentication(request: Request, call_next):
        token = os.getenv("NETRA_API_TOKEN", "")
        if token and request.url.path not in ("/health",) and request.method != "OPTIONS":
            supplied = request.headers.get("authorization", "")
            if not compare_digest(supplied, f"Bearer {token}"):
                return JSONResponse({"detail": "Valid Bearer token required"}, status_code=401)
        return await call_next(request)
        
    application.include_router(api_router)
    
    @application.get("/health")
    def readiness():
        application.state.store.ping()
        return {"status": "ok", "app": "Netra", "version": "1.0.0"}
        
    @application.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        client_id = await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await ws_manager.handle_client_message(client_id, data)
        except WebSocketDisconnect:
            ws_manager.disconnect(client_id)
            
    return application

app = create_app()
