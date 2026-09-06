"""Read-only advanced analytics; all results retain their supporting flow identifiers."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from app.services.graph_analytics import build_graph, blast_radius, communication_path, topology_diff, behavior_summary

router = APIRouter(tags=["evidence-backed analytics"])


def graph(request: Request, at: str | None = None, since: str | None = None):
    store = request.app.state.store
    try:
        return build_graph(store.all("hosts"), store.all("flows"), at=at, since=since)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/topology/history")
def history(request: Request, at: datetime | None = None, since: datetime | None = None):
    return graph(request, at.isoformat() if at else None, since.isoformat() if since else None)


@router.get("/topology/path")
def path(request: Request, source: str = Query(max_length=45), destination: str = Query(max_length=45)):
    try:
        return communication_path(graph(request), source, destination)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/topology/blast-radius")
def radius(request: Request, source: str = Query(max_length=45), max_hops: int = Query(2, ge=1, le=5)):
    try:
        return blast_radius(graph(request), source, max_hops)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/topology/diff")
def diff(request: Request, before: datetime, after: datetime, window_seconds: int = Query(300, ge=1, le=86400)):
    before = before.replace(tzinfo=timezone.utc) if before.tzinfo is None else before
    after = after.replace(tzinfo=timezone.utc) if after.tzinfo is None else after
    if before > after:
        raise HTTPException(422, "before must not be later than after")
    earlier = graph(request, before.isoformat(), (before - timedelta(seconds=window_seconds)).isoformat())
    later = graph(request, after.isoformat(), (after - timedelta(seconds=window_seconds)).isoformat())
    return {"before": before.isoformat(), "after": after.isoformat(), "windowSeconds": window_seconds, **topology_diff(earlier, later)}


@router.get("/analytics/behavior")
def behavior(request: Request):
    return behavior_summary(request.app.state.store.all("flows"))
