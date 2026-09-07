"""Offline workbench with optional bearer authorization and observed telemetry."""
import asyncio
import os
from contextlib import asynccontextmanager
from hmac import compare_digest
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from app.api.router import api_router
from app.runtime import Store


def create_app(db_path=None, seed_demo=None):
    @asynccontextmanager
    async def lifespan(application):
        application.state.store = Store(db_path, seed_demo)
        try:
            yield
        finally:
            application.state.store.close()
    application=FastAPI(title=os.getenv('APP_NAME','Netra'),version='1.0.0',lifespan=lifespan,
        description='Local network telemetry and evidence workbench. Heuristic forecasts are uncalibrated. Demo is opt-in.')
    origins=os.getenv('CORS_ORIGINS','http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173').split(',')
    application.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,
        allow_methods=['GET','POST','PATCH'],allow_headers=['Content-Type','Authorization','X-Filename'])
    @application.middleware('http')
    async def authenticate(request: Request,call_next):
        token=os.getenv('NETRA_API_TOKEN','')
        if token and request.url.path != '/health' and request.method != 'OPTIONS':
            if not compare_digest(request.headers.get('authorization',''),f'Bearer {token}'):
                return JSONResponse({'detail':'Valid Bearer token required'},status_code=401)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff'
        return response
    application.include_router(api_router,prefix='/api/v1')
    application.include_router(api_router,prefix='/api',include_in_schema=False)
    @application.get('/health')
    def readiness():
        application.state.store.ping()
        return {'status':'ok','app':os.getenv('APP_NAME','Netra'),'version':'1.0.0'}
    @application.websocket('/ws')
    async def websocket(ws: WebSocket):
        token=os.getenv('NETRA_API_TOKEN','')
        protocols=[x.strip() for x in ws.headers.get('sec-websocket-protocol','').split(',')]
        supplied=ws.headers.get('authorization','')
        if any(p.startswith('bearer.') for p in protocols):
            supplied='Bearer '+next(p[7:] for p in protocols if p.startswith('bearer.'))
        origin=ws.headers.get('origin')
        if (origin and origin not in origins) or (token and not compare_digest(supplied,f'Bearer {token}')):
            await ws.close(code=1008)
            return
        await ws.accept(subprotocol='netra' if 'netra' in protocols else None)
        try:
            while True:
                payload=await run_in_threadpool(application.state.store.telemetry)
                await ws.send_json({'type':'telemetry','payload':payload})
                try:
                    await asyncio.wait_for(ws.receive_text(),timeout=2)
                except asyncio.TimeoutError:
                    pass
        except (WebSocketDisconnect,RuntimeError):
            pass
    return application

app=create_app()
