"""
Netra Baseline Engine
Learns and maintains behavioral baselines for every host over multiple time windows.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional


class WindowStats:
    """Rolling statistics for a single time window."""

    __slots__ = (
        "window_size", "connections", "unique_peers", "unique_destinations",
        "unique_ports", "failed_connections", "dns_queries", "bytes_sent",
        "bytes_received", "flow_durations", "sample_count",
        "_conn_rates", "_peer_counts", "_port_counts", "_dns_rates",
        "_bandwidth_samples", "_entropy_samples",
    )

    def __init__(self, window_size: str):
        self.window_size = window_size
        self.connections: int = 0
        self.unique_peers: set = set()
        self.unique_destinations: set = set()
        self.unique_ports: set = set()
        self.failed_connections: int = 0
        self.dns_queries: int = 0
        self.bytes_sent: int = 0
        self.bytes_received: int = 0
        self.flow_durations: list[float] = []
        self.sample_count: int = 0
        self._conn_rates: list[float] = []
        self._peer_counts: list[int] = []
        self._port_counts: list[int] = []
        self._dns_rates: list[float] = []
        self._bandwidth_samples: list[float] = []
        self._entropy_samples: list[float] = []

    def record_window_snapshot(self, duration_sec: float) -> None:
        if duration_sec <= 0:
            duration_sec = 1.0
        conn_rate = self.connections / duration_sec
        self._conn_rates.append(conn_rate)
        self._peer_counts.append(len(self.unique_peers))
        self._port_counts.append(len(self.unique_ports))
        dns_rate = self.dns_queries / duration_sec
        self._dns_rates.append(dns_rate)
        total_bw = (self.bytes_sent + self.bytes_received) * 8 / duration_sec
        self._bandwidth_samples.append(total_bw)
        if len(self.unique_destinations) > 1:
            dest_counts = defaultdict(int)
            for d in self.unique_destinations:
                dest_counts[d] += 1
            total = sum(dest_counts.values())
            entropy = -sum(
                (c / total) * math.log2(c / total)
                for c in dest_counts.values() if c > 0
            )
            self._entropy_samples.append(entropy)
        else:
            self._entropy_samples.append(0.0)
        self.sample_count += 1
        self._trim_history()
        self._reset_counters()

    def _trim_history(self, max_samples: int = 500) -> None:
        for attr in ("_conn_rates", "_peer_counts", "_port_counts",
                      "_dns_rates", "_bandwidth_samples", "_entropy_samples"):
            lst = getattr(self, attr)
            if len(lst) > max_samples:
                setattr(self, attr, lst[-max_samples:])

    def _reset_counters(self) -> None:
        self.connections = 0
        self.unique_peers = set()
        self.unique_destinations = set()
        self.unique_ports = set()
        self.failed_connections = 0
        self.dns_queries = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.flow_durations = []

    def get_baseline(self) -> dict[str, Any]:
        def _safe_stats(values: list) -> dict[str, float]:
            if not values:
                return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
            m = statistics.mean(values)
            s = statistics.stdev(values) if len(values) > 1 else 0.0
            return {"mean": round(m, 4), "std": round(s, 4),
                    "min": round(min(values), 4), "max": round(max(values), 4)}

        return {
            "window_size": self.window_size,
            "sample_count": self.sample_count,
            "conn_rate": _safe_stats(self._conn_rates),
            "peer_count": _safe_stats([float(x) for x in self._peer_counts]),
            "port_count": _safe_stats([float(x) for x in self._port_counts]),
            "dns_rate": _safe_stats(self._dns_rates),
            "bandwidth_bps": _safe_stats(self._bandwidth_samples),
            "dest_entropy": _safe_stats(self._entropy_samples),
        }

    def compute_deviation(self, current_values: dict[str, float]) -> dict[str, float]:
        baseline = self.get_baseline()
        deviations: dict[str, float] = {}
        for key in ("conn_rate", "peer_count", "port_count", "dns_rate",
                     "bandwidth_bps", "dest_entropy"):
            bl = baseline.get(key, {})
            mean = bl.get("mean", 0.0)
            std = bl.get("std", 0.0)
            current = current_values.get(key, 0.0)
            if std > 0:
                z = abs(current - mean) / std
            elif mean > 0:
                z = abs(current - mean) / mean * 2
            else:
                z = 0.0
            deviations[key] = round(min(z, 10.0), 4)
        return deviations


WINDOW_DURATIONS: dict[str, float] = {
    "5s": 5.0, "10s": 10.0, "30s": 30.0,
    "1m": 60.0, "5m": 300.0, "15m": 900.0,
    "1h": 3600.0, "24h": 86400.0,
}


class BaselineEngine:
    """Learns normal behavior per host across multiple time windows."""

    def __init__(self, windows: Optional[list[str]] = None):
        self._windows = windows or ["5s", "30s", "1m", "5m", "15m", "1h"]
        self._host_windows: dict[str, dict[str, WindowStats]] = defaultdict(
            lambda: {w: WindowStats(w) for w in self._windows}
        )
        self._last_snapshot: dict[str, dict[str, datetime]] = defaultdict(dict)

    def process_event(self, host_ip: str, event: dict[str, Any]) -> None:
        windows = self._host_windows[host_ip]
        now = datetime.now(timezone.utc)
        dst_ip = event.get("destination_ip", event.get("dst_ip", ""))
        dst_port = event.get("destination_port", event.get("dst_port"))
        protocol = event.get("protocol", "")
        is_failed = event.get("tcp_flags", {}).get("rst", False)
        is_dns = event.get("event_type") == "dns" or protocol.upper() == "DNS"
        bytes_out = event.get("bytes_forward", 0)
        bytes_in = event.get("bytes_backward", 0)
        duration = event.get("duration_ms", 0)

        for wname, wstats in windows.items():
            wstats.connections += 1
            if dst_ip:
                wstats.unique_peers.add(dst_ip)
                wstats.unique_destinations.add(dst_ip)
            if dst_port:
                wstats.unique_ports.add(dst_port)
            if is_failed:
                wstats.failed_connections += 1
            if is_dns:
                wstats.dns_queries += 1
            wstats.bytes_sent += bytes_out
            wstats.bytes_received += bytes_in
            if duration > 0:
                wstats.flow_durations.append(duration)

            last = self._last_snapshot.get(host_ip, {}).get(wname)
            window_dur = WINDOW_DURATIONS.get(wname, 60.0)
            if last is None or (now - last).total_seconds() >= window_dur:
                wstats.record_window_snapshot(window_dur)
                if host_ip not in self._last_snapshot:
                    self._last_snapshot[host_ip] = {}
                self._last_snapshot[host_ip][wname] = now

    def get_baseline(self, host_ip: str, window: str = "5m") -> dict[str, Any]:
        windows = self._host_windows.get(host_ip, {})
        wstats = windows.get(window)
        if wstats is None:
            return {"window_size": window, "sample_count": 0, "status": "no_data"}
        return wstats.get_baseline()

    def get_all_baselines(self, host_ip: str) -> dict[str, Any]:
        windows = self._host_windows.get(host_ip, {})
        return {w: ws.get_baseline() for w, ws in windows.items()}

    def compute_deviation(self, host_ip: str, current_values: dict[str, float],
                          window: str = "5m") -> dict[str, float]:
        windows = self._host_windows.get(host_ip, {})
        wstats = windows.get(window)
        if wstats is None or wstats.sample_count < 3:
            return {}
        return wstats.compute_deviation(current_values)

    def get_anomaly_score(self, host_ip: str, current_values: dict[str, float],
                          window: str = "5m") -> float:
        deviations = self.compute_deviation(host_ip, current_values, window)
        if not deviations:
            return 0.0
        weights = {
            "conn_rate": 1.5, "peer_count": 2.0, "port_count": 2.0,
            "dns_rate": 1.0, "bandwidth_bps": 1.0, "dest_entropy": 1.5,
        }
        weighted_sum = sum(
            deviations.get(k, 0.0) * weights.get(k, 1.0)
            for k in deviations
        )
        total_weight = sum(weights.get(k, 1.0) for k in deviations)
        raw = weighted_sum / total_weight if total_weight > 0 else 0.0
        score = min(100.0, raw * 20)
        return round(score, 2)

    def get_stats(self) -> dict[str, Any]:
        return {
            "hosts_tracked": len(self._host_windows),
            "windows": self._windows,
        }
