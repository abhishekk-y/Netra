"""Validated, persistent API for the local telemetry workbench."""
from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(analytics_router)

class FlowInput(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    srcIp: str
    dstIp: str
    srcPort: int = Field(0, ge=0, le=65535)
    dstPort: int = Field(0, ge=0, le=65535)
    protocol: Literal['TCP', 'UDP', 'ICMP', 'OTHER', 'SCTP'] = 'TCP'
    packets: int = Field(ge=0, le=10**12)
    bytes: int = Field(ge=0, le=10**15)
    duration: float = Field(ge=0, le=31536000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field('ingested', min_length=1, max_length=200)
    eventId: str | None = Field(None, max_length=128)
    communityId: str | None = Field(None, max_length=100)
    evidenceId: str | None = Field(None, max_length=128)
    evidenceReference: str | None = Field(None, max_length=256)
    rawSource: str | None = Field(None, max_length=200)
    sessionUid: str | None = Field(None, max_length=200)
    @field_validator('srcIp','dstIp')
    @classmethod
    def address(cls, v):
        return str(ip_address(v))
    @field_validator('protocol', mode='before')
    @classmethod
    def uppercase(cls, v):
        return v.upper() if isinstance(v,str) else v
    @field_validator('timestamp')
    @classmethod
    def utc(cls,v):
        if v.tzinfo is None:
            raise ValueError('timestamp must include a timezone')
        return v.astimezone(timezone.utc)
class Ingestion(BaseModel):
    model_config = ConfigDict(extra='forbid')
    flows: list[FlowInput] = Field(min_length=1,max_length=1000)
class AlertUpdate(BaseModel):
    status: Literal['new','acknowledged','resolved']
class IncidentUpdate(BaseModel):
    status: Literal['active','investigating','mitigated','closed']
class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    profile: Literal['LIGHT','STANDARD','FORENSIC'] | None = None
    retentionDays: int | None = Field(None,ge=1,le=365)
    autoRefresh: bool | None = None
class HuntQuery(BaseModel):
    query: str = Field('',max_length=500)

@api_router.get('/dashboard/summary')
@api_router.get('/summary',include_in_schema=False)
def summary(request: Request):
    return request.app.state.store.summary()

def collection(kind):
    def endpoint(request: Request, page: int = Query(1,ge=1), pageSize: int = Query(100,ge=1,le=1000), search: str = Query('',max_length=200)):
        return request.app.state.store.page(kind,page,pageSize,search)
    endpoint.__name__ = 'list_' + kind
    return endpoint
for kind in ('hosts','flows','alerts','incidents','forecasts','audit'):
    api_router.add_api_route('/'+kind,collection(kind),methods=['GET'],tags=[kind])

@api_router.get('/hosts/{entity_id}')
def host(request: Request,entity_id: str):
    return request.app.state.store.host_detail(entity_id)
@api_router.get('/flows/{entity_id}')
def flow(request: Request,entity_id: str):
    return request.app.state.store.get('flows',entity_id)
@api_router.patch('/alerts/{entity_id}')
def alert_status(request: Request,entity_id: str,body: AlertUpdate):
    return request.app.state.store.update_status('alerts',entity_id,body.status)
@api_router.get('/incidents/{entity_id}')
@api_router.get('/incidents/{entity_id}/report')
def incident(request: Request,entity_id: str):
    return request.app.state.store.incident_detail(entity_id)
@api_router.patch('/incidents/{entity_id}')
def incident_status(request: Request,entity_id: str,body: IncidentUpdate):
    return request.app.state.store.update_status('incidents',entity_id,body.status)
@api_router.get('/topology/graph')
def topology(request: Request):
    return request.app.state.store.topology()
@api_router.get('/forecasts/current')
def forecast(request: Request):
    return request.app.state.store.forecast()
@api_router.get('/forecasts/history')
def forecasts(request: Request):
    return request.app.state.store.page('forecasts',page_size=1000)
@api_router.get('/health')
def health(request: Request):
    try:
        return request.app.state.store.health()
    except Exception as exc:
        import traceback
        trace = traceback.format_exc()
        print("HEALTH ERROR:", trace)
        return {"status": "error", "message": str(exc), "trace": trace}
@api_router.get('/settings')
def settings(request: Request):
    return request.app.state.store.settings()
@api_router.patch('/settings')
def settings_update(request: Request,body: SettingsUpdate):
    return request.app.state.store.update_settings(body.model_dump(exclude_none=True))
@api_router.post('/ingest/flows',status_code=201)
def ingest(request: Request,body: Ingestion):
    return request.app.state.store.ingest([f.model_dump(mode='json',exclude_none=True) for f in body.flows])
@api_router.post('/hunting/query')
def hunt(request: Request,body: HuntQuery):
    try:
        return request.app.state.store.hunt(body.query)
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc
@api_router.get('/replay')
def replay(request: Request):
    return request.app.state.store.replay()
@api_router.post('/demo/run')
def demo(request: Request):
    store=request.app.state.store
    with store.lock:
        if not store.all('metadata'):
            store.seed()
        store.update_settings({'demoMode':True})
    return store.summary()
@api_router.get('/ml/status')
def ml_status():
    from app.runtime import _ml_status
    return _ml_status()
@api_router.post('/ml/predict')
def ml_predict(body: FlowInput):
    from app.runtime import _ml_predict_flow
    return _ml_predict_flow(body.model_dump(mode='json',exclude_none=True))

from .forensics import router as forensics_router
api_router.include_router(forensics_router)

