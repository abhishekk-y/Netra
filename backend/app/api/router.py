"""Netra — API Router. Includes all v1 endpoint routers."""
from __future__ import annotations
from fastapi import APIRouter
from .v1 import (
    auth, dashboard, hosts, topology, flows, alerts, incidents,
    forecasts, packets, dns, tls, assets, mitre, risk,
    hunting, forensics, deception, health, settings,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(hosts.router)
api_router.include_router(topology.router)
api_router.include_router(flows.router)
api_router.include_router(alerts.router)
api_router.include_router(incidents.router)
api_router.include_router(forecasts.router)
api_router.include_router(packets.router)
api_router.include_router(dns.router)
api_router.include_router(tls.router)
api_router.include_router(assets.router)
api_router.include_router(mitre.router)
api_router.include_router(risk.router)
api_router.include_router(hunting.router)
api_router.include_router(forensics.router)
api_router.include_router(deception.router)
api_router.include_router(health.router)
api_router.include_router(settings.router)
