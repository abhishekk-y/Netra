"""
Netra Risk Engine
Deterministic, explainable risk scoring with component breakdown.
Risk = w1*anomaly + w2*forecast + w3*signature + w4*behavior + w5*graph + w6*criticality + w7*threat
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


CRITICALITY_SCORES: dict[str, float] = {
    "low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0,
}

DEFAULT_WEIGHTS: dict[str, float] = {
    "anomaly": 0.20,
    "forecast": 0.20,
    "signature": 0.15,
    "behavior": 0.15,
    "graph": 0.10,
    "criticality": 0.10,
    "threat": 0.10,
}


@dataclass
class RiskComponents:
    anomaly: float = 0.0
    forecast: float = 0.0
    signature: float = 0.0
    behavior: float = 0.0
    graph: float = 0.0
    criticality: float = 0.0
    threat: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "anomaly": round(self.anomaly, 2),
            "forecast": round(self.forecast, 2),
            "signature": round(self.signature, 2),
            "behavior": round(self.behavior, 2),
            "graph": round(self.graph, 2),
            "criticality": round(self.criticality, 2),
            "threat": round(self.threat, 2),
        }


@dataclass
class RiskResult:
    host_id: str
    host_ip: str
    total_score: float
    components: RiskComponents
    explanation: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    contributing_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "host_ip": self.host_ip,
            "total_score": round(self.total_score, 2),
            "components": self.components.to_dict(),
            "explanation": self.explanation,
            "timestamp": self.timestamp.isoformat(),
            "contributing_factors": self.contributing_factors,
        }


class RiskEngine:
    """Deterministic, explainable risk scoring engine."""

    def __init__(self, weights: Optional[dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self._host_risk_history: dict[str, list[tuple[datetime, float]]] = {}

    def calculate_risk(
        self,
        host_id: str,
        host_ip: str,
        anomaly_score: float = 0.0,
        forecast_score: float = 0.0,
        signature_score: float = 0.0,
        behavior_deviation: float = 0.0,
        graph_proximity: float = 0.0,
        asset_criticality: str = "medium",
        threat_evidence: float = 0.0,
    ) -> RiskResult:
        crit_score = CRITICALITY_SCORES.get(asset_criticality.lower(), 0.3)

        components = RiskComponents(
            anomaly=min(100.0, max(0.0, anomaly_score)),
            forecast=min(100.0, max(0.0, forecast_score)),
            signature=min(100.0, max(0.0, signature_score)),
            behavior=min(100.0, max(0.0, behavior_deviation)),
            graph=min(100.0, max(0.0, graph_proximity)),
            criticality=crit_score * 100,
            threat=min(100.0, max(0.0, threat_evidence)),
        )

        total = (
            self.weights["anomaly"] * components.anomaly +
            self.weights["forecast"] * components.forecast +
            self.weights["signature"] * components.signature +
            self.weights["behavior"] * components.behavior +
            self.weights["graph"] * components.graph +
            self.weights["criticality"] * components.criticality +
            self.weights["threat"] * components.threat
        )
        total = min(100.0, max(0.0, total))

        factors: list[str] = []
        scored = [
            ("Anomaly detection", components.anomaly, self.weights["anomaly"]),
            ("Attack forecast", components.forecast, self.weights["forecast"]),
            ("Signature match", components.signature, self.weights["signature"]),
            ("Behavior deviation", components.behavior, self.weights["behavior"]),
            ("Graph proximity", components.graph, self.weights["graph"]),
            ("Asset criticality", components.criticality, self.weights["criticality"]),
            ("Threat evidence", components.threat, self.weights["threat"]),
        ]
        scored.sort(key=lambda x: x[1] * x[2], reverse=True)
        for name, score, weight in scored:
            contribution = round(score * weight, 1)
            if contribution > 0.5:
                factors.append(f"{name}: +{contribution}")

        explanation = f"Risk {round(total, 1)} — " + ", ".join(factors[:4]) if factors else f"Risk {round(total, 1)} — No significant risk factors"

        now = datetime.now(timezone.utc)
        if host_id not in self._host_risk_history:
            self._host_risk_history[host_id] = []
        self._host_risk_history[host_id].append((now, total))
        if len(self._host_risk_history[host_id]) > 500:
            self._host_risk_history[host_id] = self._host_risk_history[host_id][-250:]

        return RiskResult(
            host_id=host_id,
            host_ip=host_ip,
            total_score=total,
            components=components,
            explanation=explanation,
            timestamp=now,
            contributing_factors=factors,
        )

    def get_risk_timeline(self, host_id: str) -> list[dict[str, Any]]:
        history = self._host_risk_history.get(host_id, [])
        return [{"timestamp": ts.isoformat(), "score": round(s, 2)} for ts, s in history]

    def get_top_risk_hosts(self, n: int = 10) -> list[dict[str, Any]]:
        latest: dict[str, tuple[datetime, float]] = {}
        for hid, history in self._host_risk_history.items():
            if history:
                latest[hid] = history[-1]
        sorted_hosts = sorted(latest.items(), key=lambda x: -x[1][1])[:n]
        return [
            {"host_id": hid, "score": round(score, 2), "timestamp": ts.isoformat()}
            for hid, (ts, score) in sorted_hosts
        ]

    def update_weights(self, new_weights: dict[str, float]) -> None:
        for key in new_weights:
            if key in self.weights:
                self.weights[key] = max(0.0, min(1.0, new_weights[key]))
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}
