"""End-to-end API regression tests with isolated SQLite stores and no server."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import create_app
from app.runtime import Store, community_id

API = "/api/v1"

@pytest.fixture(autouse=True)
def local_environment(monkeypatch):
    monkeypatch.delenv("NETRA_API_TOKEN", raising=False)
    monkeypatch.setenv("NETRA_ENABLE_ML", "false")
    monkeypatch.setenv("NETRA_SEED_DEMO", "false")

@pytest.fixture
def client():
    with TestClient(create_app(":memory:", seed_demo=False)) as connection:
        yield connection

def flow(**changes):
    return {"srcIp": "10.0.0.10", "dstIp": "10.0.0.20", "srcPort": 45000,
            "dstPort": 443, "protocol": "TCP", "packets": 20, "bytes": 2000,
            "duration": 2.0, "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "test-capture", **changes}

def ingest(client, *flows):
    response = client.post(API + "/ingest/flows", json={"flows": list(flows)})
    assert response.status_code == 201, response.text
    return response.json()

def test_empty_default_and_contracts(client):
    assert client.get("/health").json()["status"] == "ok"
    summary = client.get(API + "/dashboard/summary").json()
    assert summary["totalFlows"] == summary["totalHosts"] == summary["activeIncidents"] == 0
    assert summary["dataMode"] == "empty"
    for resource in ("hosts", "flows", "alerts", "incidents", "forecasts/history"):
        assert client.get(f"{API}/{resource}").json()["data"] == []
    assert client.get(API + "/topology/graph").json()["edges"] == []
    assert client.get(API + "/forecasts/current").json()["nextStages"] == []
    assert client.get("/api/flows").json()["total"] == 0
    assert client.get(API + "/hosts/missing").status_code == 404
    health = client.get(API + "/health").json()
    assert health["components"]["database"] == "up"
    assert health["components"]["capture"] == "down"
    assert health["ml"]["available"] is False

@pytest.mark.parametrize("changes", [
    {"srcIp": "bad"}, {"dstPort": 65536}, {"bytes": -1}, {"duration": -1},
    {"protocol": "NOT-A-PROTOCOL"}, {"timestamp": "2026-01-01T10:00:00"},
    {"madeUp": "value"},
])
def test_validation_is_atomic(client, changes):
    response = client.post(API + "/ingest/flows", json={"flows": [flow(), flow(**changes)]})
    assert response.status_code == 422
    assert client.get(API + "/flows").json()["total"] == 0

def test_ingestion_persistence_provenance_and_graph(client):
    record = ingest(client, flow(evidenceId="a" * 64, rawSource="zeek", sessionUid="uid-1"))["flows"][0]
    assert record["synthetic"] is False
    assert record["communityId"].startswith("1:")
    assert record["evidenceId"] == "a" * 64
    assert record["mlAvailable"] is False
    assert record["attackType"] is None
    assert client.get(API + "/flows/" + record["id"]).json()["sessionUid"] == "uid-1"
    graph = client.get(API + "/topology/graph").json()
    assert len(graph["nodes"]) == 2
    assert graph["edges"][0]["data"]["flowIds"] == [record["id"]]
    assert graph["edges"][0]["data"]["weight"] == 2000
    assert client.get(API + "/hosts").json()["total"] == 2
    assert client.get(API + "/flows?pageSize=1&page=2").json()["data"] == []
    assert client.get(API + "/flows?pageSize=0").status_code == 422

def test_rule_alert_incident_actions_and_audit(client):
    result = ingest(client, flow(dstPort=445, packets=30))
    assert result["alertsCreated"] == result["incidentsCreated"] == 1
    alert = client.get(API + "/alerts").json()["data"][0]
    incident = client.get(API + "/incidents").json()["data"][0]
    assert alert["flowId"] == result["flows"][0]["id"]
    assert alert["confidenceMeaning"].startswith("Rule priority")
    assert incident["stage"] == "Lateral Movement"
    assert client.patch(API + "/alerts/" + alert["id"], json={"status": "resolved"}).status_code == 200
    assert client.patch(API + "/incidents/" + incident["id"], json={"status": "closed"}).status_code == 200
    assert client.patch(API + "/incidents/" + incident["id"], json={"status": "invalid"}).status_code == 422
    assert client.get(API + "/dashboard/summary").json()["activeIncidents"] == 0
    assert client.get(API + "/forecasts/current").json()["currentStage"] == "No active incident"
    report = client.get(API + "/incidents/" + incident["id"] + "/report").json()
    assert report["flows"][0]["id"] == result["flows"][0]["id"]
    audit = client.get(API + "/audit").json()["data"]
    assert {item["action"] for item in audit} >= {"flows.ingest", "alerts.status", "incidents.status"}

def test_hunting_language_rejects_code_and_compares_fields(client):
    ingest(client, flow(dstPort=22), flow(dstPort=443, bytes=500))
    result = client.post(API + "/hunting/query", json={"query": "appProtocol == 'SSH' and bytes > 1000"})
    assert result.status_code == 200
    assert result.json()["total"] == 1
    bad = client.post(API + "/hunting/query", json={"query": "bytes > 0; DROP TABLE entities"})
    assert bad.status_code == 422
    assert client.get(API + "/flows").json()["total"] == 2

def test_historical_replay_never_claims_prospective_lead_time(client):
    base = datetime(2020, 1, 1, tzinfo=timezone.utc)
    ingest(client, flow(dstPort=445, timestamp=base.isoformat()))
    before = client.get(API + "/forecasts/current").json()
    assert before["calibrated"] is False
    assert "outcome" not in before
    ingest(client, flow(dstIp="8.8.8.8", bytes=6_000_000, timestamp=(base+timedelta(seconds=60)).isoformat()))
    history = client.get(API + "/forecasts/history").json()["data"]
    original = next(f for f in history if f["id"] == before["id"])
    assert original["timestamp"] == before["timestamp"]
    assert original["nextStages"] == before["nextStages"]
    assert original["outcome"]["leadTimeSeconds"] is None
    assert original["outcome"]["prospective"] is False
    assert original["outcome"]["ingestionDelaySeconds"] >= 0
    assert client.get(API + "/flows").json()["total"] == 2

def test_same_batch_has_no_hindsight_forecast(client):
    base = datetime(2020, 1, 1, tzinfo=timezone.utc)
    ingest(client, flow(dstPort=445, timestamp=base.isoformat()),
           flow(dstIp="8.8.8.8", bytes=6_000_000, timestamp=(base+timedelta(seconds=60)).isoformat()))
    snapshots = client.get(API + "/forecasts/history").json()["data"]
    assert len(snapshots) == 1
    assert snapshots[0]["currentStage"] == "Exfiltration"
    assert "outcome" not in snapshots[0]


def test_persistence_restart_stays_empty_until_ingested(tmp_path):
    database = tmp_path / "netra.db"
    with TestClient(create_app(database, seed_demo=False)) as first:
        assert first.get(API + "/flows").json()["total"] == 0
        record = ingest(first, flow())["flows"][0]
        first.patch(API + "/settings", json={"retentionDays": 90, "profile": "LIGHT"})
    with TestClient(create_app(database, seed_demo=False)) as second:
        assert second.get(API + "/flows").json()["data"][0]["id"] == record["id"]
        assert second.get(API + "/settings").json()["retentionDays"] == 90
        assert second.get(API + "/flows").json()["total"] == 1


def test_token_http_and_websocket(monkeypatch):
    monkeypatch.setenv("NETRA_API_TOKEN", "test-local-token")
    with TestClient(create_app(":memory:", seed_demo=False)) as client:
        assert client.get("/health").status_code == 200
        assert client.get(API + "/flows").status_code == 401
        assert client.get(API + "/flows", headers={"Authorization": "Bearer test-local-token"}).status_code == 200
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws"):
                pass
        with client.websocket_connect("/ws", subprotocols=["netra", "bearer.test-local-token"]) as ws:
            assert ws.accepted_subprotocol == "netra"
            assert ws.receive_json()["payload"]["hostsCount"] == 0
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/ws", headers={"Origin": "https://untrusted.invalid"}, subprotocols=["netra", "bearer.test-local-token"]):
                pass


def test_community_id_direction_same_address_and_unknown_protocol():
    forward = flow(srcIp="10.0.0.1", dstIp="10.0.0.1", srcPort=100, dstPort=200)
    reverse = {**forward, "srcPort": 200, "dstPort": 100}
    assert community_id(forward) == community_id(reverse)
    assert community_id(flow(protocol="ICMP")) is None


def test_retention_keeps_incident_and_forecast_evidence():
    store = Store(":memory:", seed_demo=False)
    try:
        risky = store.ingest([flow(dstPort=445)])["flows"][0]
        ordinary = store.ingest([flow(srcIp="10.1.1.1")])["flows"][0]
        old = (datetime.now(timezone.utc)-timedelta(days=40)).isoformat()
        with store.lock, store.db:
            for record in store.all("flows") + store.all("alerts"):
                kind = "alerts" if "flowId" in record else "flows"
                record["ingestedAt"] = old
                store.put(kind, record)
        store.prune()
        assert store.get("flows", risky["id"])["id"] == risky["id"]
        assert ordinary["id"] not in {f["id"] for f in store.all("flows")}
        incident = store.all("incidents")[0]
        assert store.incident_detail(incident["id"])["alerts"]
        assert store.incident_detail(incident["id"])["flows"]
    finally:
        store.close()


def test_idempotent_collector_event_and_zero_duration():
    store = Store(":memory:", seed_demo=False)
    try:
        entry = flow(eventId="sensor-one-unique-event", duration=0, packets=1)
        assert store.ingest([entry])["accepted"] == 1
        result = store.ingest([entry])
        assert result["accepted"] == 0 and result["duplicates"] == 1
        assert len(store.all("flows")) == 1
        assert store.all("alerts") == []
    finally:
        store.close()
