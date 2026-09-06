from app.services.graph_analytics import build_graph, communication_path, blast_radius, topology_diff, behavior_summary
import pytest


def flow(i, src="10.0.0.1", dst="10.0.0.2", port=443):
    return {"id": str(i), "timestamp": f"2026-01-01T00:{i // 60:02}:{i % 60:02}Z", "srcIp": src, "dstIp": dst,
        "dstPort": port, "protocol": "TCP", "bytes": 100 + i, "packets": 1, "riskScore": i}


def test_historical_graph_does_not_leak_future_flows_or_risk():
    graph = build_graph([], [flow(1), flow(50, dst="10.0.0.3")], at="2026-01-01T00:00:02Z")
    assert graph["flowCount"] == 1
    assert {n["ip"] for n in graph["nodes"]} == {"10.0.0.1", "10.0.0.2"}
    assert graph["edges"][0]["risk"] == 1
    assert graph["edges"][0]["flowIds"] == ["1"]


def test_directed_path_and_radius_handle_cycles_and_unreachable_nodes():
    graph = build_graph([], [flow(1), flow(2, "10.0.0.2", "10.0.0.3"), flow(3, "10.0.0.3", "10.0.0.1"), flow(4, "10.0.0.4", "10.0.0.5")])
    assert communication_path(graph, "10.0.0.1", "10.0.0.3")["hops"] == 2
    assert communication_path(graph, "10.0.0.1", "10.0.0.4")["found"] is False
    radius = blast_radius(graph, "10.0.0.1")
    assert radius["totalCount"] == 2
    assert radius["directCount"] == 1
    with pytest.raises(ValueError):
        blast_radius(graph, "10.0.0.99")


def test_window_diff_identifies_new_relationships_and_service_changes():
    before = build_graph([], [flow(1)])
    after = build_graph([], [flow(1), flow(2, port=22), flow(3, dst="10.0.0.3")])
    diff = topology_diff(before, after)
    assert len(diff["addedNodes"]) == 1
    assert len(diff["addedEdges"]) == 1
    assert diff["changedEdges"][0]["changes"]["ports"]["after"] == [22, 443]


def test_periodicity_requires_evidence_and_zero_mad_is_not_infinity():
    assert behavior_summary([flow(i) for i in range(5)])["periodicity"] == []
    values = [{**flow(i), "bytes": 100} for i in range(20)]
    result = behavior_summary(values)
    assert result["periodicity"][0]["regularityScore"] == 1
    assert result["sourceProfiles"][0]["robustShiftScore"] is None
    assert len(result["periodicity"][0]["flowIds"]) == 20


def test_empty_and_invalid_time_window():
    assert build_graph([], [])["nodes"] == []
    with pytest.raises(ValueError):
        build_graph([], [], at="2026-01-01", since="2026-02-01")
