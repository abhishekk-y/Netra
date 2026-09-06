"""
Netra — Forecast Manager
Orchestrates all forecasting: attack state tracking, sequence prediction,
temporal forecasting, target prediction, and explanation generation.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from .attack_state_machine import AttackStateMachine, AttackStage, STAGE_SEVERITY


class ForecastRecord:
    """A single forecast record with predictions and metadata."""

    __slots__ = (
        "forecast_id", "timestamp", "host_id", "host_ip", "incident_id",
        "current_stage", "current_confidence", "predictions",
        "target_predictions", "attack_path", "blast_radius",
        "model_name", "uncertainty", "explanation",
        "actual_outcome", "actual_outcome_time",
    )

    def __init__(self, host_id: str, host_ip: str):
        self.forecast_id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc)
        self.host_id = host_id
        self.host_ip = host_ip
        self.incident_id: Optional[str] = None
        self.current_stage: str = "benign"
        self.current_confidence: float = 1.0
        self.predictions: list[dict] = []
        self.target_predictions: list[dict] = []
        self.attack_path: list[dict] = []
        self.blast_radius: dict = {}
        self.model_name: str = "ensemble_v1"
        self.uncertainty: dict = {}
        self.explanation: dict = {}
        self.actual_outcome: Optional[str] = None
        self.actual_outcome_time: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "forecast_id": self.forecast_id,
            "timestamp": self.timestamp.isoformat(),
            "host_id": self.host_id,
            "host_ip": self.host_ip,
            "incident_id": self.incident_id,
            "current_stage": self.current_stage,
            "current_confidence": round(self.current_confidence, 4),
            "predictions": self.predictions,
            "target_predictions": self.target_predictions,
            "attack_path": self.attack_path,
            "blast_radius": self.blast_radius,
            "model_name": self.model_name,
            "uncertainty": self.uncertainty,
            "explanation": self.explanation,
            "actual_outcome": self.actual_outcome,
            "actual_outcome_time": self.actual_outcome_time.isoformat() if self.actual_outcome_time else None,
        }


# Transition probability matrix (prior knowledge + will be updated by ML)
TRANSITION_PRIORS: dict[str, list[tuple[str, float]]] = {
    "reconnaissance": [
        ("initial_access", 0.35),
        ("credential_access", 0.25),
        ("reconnaissance", 0.20),
        ("discovery", 0.12),
        ("benign", 0.08),
    ],
    "initial_access": [
        ("execution", 0.30),
        ("persistence", 0.20),
        ("credential_access", 0.20),
        ("discovery", 0.15),
        ("privilege_escalation", 0.10),
        ("initial_access", 0.05),
    ],
    "credential_access": [
        ("lateral_movement", 0.30),
        ("privilege_escalation", 0.25),
        ("discovery", 0.20),
        ("persistence", 0.15),
        ("credential_access", 0.10),
    ],
    "discovery": [
        ("lateral_movement", 0.30),
        ("collection", 0.25),
        ("credential_access", 0.20),
        ("discovery", 0.15),
        ("command_and_control", 0.10),
    ],
    "lateral_movement": [
        ("collection", 0.25),
        ("credential_access", 0.20),
        ("discovery", 0.15),
        ("command_and_control", 0.15),
        ("privilege_escalation", 0.10),
        ("lateral_movement", 0.10),
        ("exfiltration", 0.05),
    ],
    "execution": [
        ("persistence", 0.25),
        ("privilege_escalation", 0.20),
        ("defense_evasion", 0.20),
        ("discovery", 0.15),
        ("collection", 0.10),
        ("command_and_control", 0.10),
    ],
    "persistence": [
        ("privilege_escalation", 0.25),
        ("defense_evasion", 0.20),
        ("discovery", 0.20),
        ("credential_access", 0.15),
        ("command_and_control", 0.10),
        ("lateral_movement", 0.10),
    ],
    "privilege_escalation": [
        ("defense_evasion", 0.20),
        ("credential_access", 0.20),
        ("discovery", 0.20),
        ("lateral_movement", 0.15),
        ("persistence", 0.10),
        ("collection", 0.10),
        ("command_and_control", 0.05),
    ],
    "command_and_control": [
        ("exfiltration", 0.30),
        ("collection", 0.25),
        ("lateral_movement", 0.20),
        ("impact", 0.10),
        ("command_and_control", 0.10),
        ("discovery", 0.05),
    ],
    "collection": [
        ("exfiltration", 0.35),
        ("command_and_control", 0.25),
        ("lateral_movement", 0.15),
        ("collection", 0.15),
        ("impact", 0.10),
    ],
    "exfiltration": [
        ("impact", 0.30),
        ("exfiltration", 0.25),
        ("command_and_control", 0.20),
        ("defense_evasion", 0.15),
        ("benign", 0.10),
    ],
    "defense_evasion": [
        ("credential_access", 0.25),
        ("discovery", 0.20),
        ("lateral_movement", 0.20),
        ("collection", 0.15),
        ("persistence", 0.10),
        ("command_and_control", 0.10),
    ],
    "impact": [
        ("impact", 0.40),
        ("exfiltration", 0.20),
        ("defense_evasion", 0.15),
        ("benign", 0.15),
        ("command_and_control", 0.10),
    ],
    "benign": [
        ("benign", 0.75),
        ("reconnaissance", 0.15),
        ("unknown", 0.10),
    ],
}


class ForecastManager:
    """Orchestrates attack forecasting, target prediction, and explanation."""

    def __init__(self, ml_inference=None):
        self.attack_sm = AttackStateMachine()
        self.ml_inference = ml_inference
        self._forecast_history: list[ForecastRecord] = []
        self._host_forecasts: dict[str, list[ForecastRecord]] = {}
        self._max_history = 5000

    def process_detection(
        self,
        host_id: str,
        host_ip: str,
        attack_type: str,
        confidence: float,
        evidence_sources: list[str],
        flow_features: Optional[dict] = None,
        host_features: Optional[dict] = None,
        graph_context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Process a detection event and generate forecast."""
        stage = self._map_attack_to_stage(attack_type)
        transition = self.attack_sm.add_evidence(
            host_id=host_id,
            host_ip=host_ip,
            stage=stage,
            confidence=confidence,
            sources=evidence_sources,
        )
        state = self.attack_sm.get_state(host_id)
        current_stage = state["current_stage"] if state else "benign"
        current_conf = state["current_confidence"] if state else 1.0
        predictions = self._generate_predictions(
            current_stage, flow_features, host_features
        )
        target_preds = self._predict_targets(
            host_id, host_ip, current_stage, graph_context
        )
        explanation = self._generate_explanation(
            current_stage, current_conf, predictions, evidence_sources
        )
        record = ForecastRecord(host_id, host_ip)
        record.current_stage = current_stage
        record.current_confidence = current_conf
        record.predictions = predictions
        record.target_predictions = target_preds
        record.explanation = explanation
        record.uncertainty = {
            "entropy": self._calc_entropy(predictions),
            "confidence_spread": self._calc_confidence_spread(predictions),
        }
        self._forecast_history.append(record)
        if host_id not in self._host_forecasts:
            self._host_forecasts[host_id] = []
        self._host_forecasts[host_id].append(record)
        if len(self._forecast_history) > self._max_history:
            self._forecast_history = self._forecast_history[-self._max_history // 2:]
        if len(self._host_forecasts.get(host_id, [])) > 200:
            self._host_forecasts[host_id] = self._host_forecasts[host_id][-100:]

        result = record.to_dict()
        result["transition"] = transition
        return result

    def _map_attack_to_stage(self, attack_type: str) -> AttackStage:
        mapping: dict[str, AttackStage] = {
            "benign": AttackStage.BENIGN,
            "portscan": AttackStage.RECONNAISSANCE,
            "reconnaissance": AttackStage.RECONNAISSANCE,
            "scanning": AttackStage.RECONNAISSANCE,
            "brute_force": AttackStage.CREDENTIAL_ACCESS,
            "credential_access": AttackStage.CREDENTIAL_ACCESS,
            "ssh_bruteforce": AttackStage.CREDENTIAL_ACCESS,
            "ftp_bruteforce": AttackStage.CREDENTIAL_ACCESS,
            "initial_access": AttackStage.INITIAL_ACCESS,
            "exploit": AttackStage.INITIAL_ACCESS,
            "web_attack": AttackStage.INITIAL_ACCESS,
            "sql_injection": AttackStage.INITIAL_ACCESS,
            "xss": AttackStage.INITIAL_ACCESS,
            "lateral_movement": AttackStage.LATERAL_MOVEMENT,
            "dos": AttackStage.IMPACT,
            "ddos": AttackStage.IMPACT,
            "botnet": AttackStage.COMMAND_AND_CONTROL,
            "c2": AttackStage.COMMAND_AND_CONTROL,
            "command_and_control": AttackStage.COMMAND_AND_CONTROL,
            "exfiltration": AttackStage.EXFILTRATION,
            "data_exfiltration": AttackStage.EXFILTRATION,
            "infiltration": AttackStage.LATERAL_MOVEMENT,
        }
        return mapping.get(attack_type.lower(), AttackStage.UNKNOWN)

    def _generate_predictions(
        self,
        current_stage: str,
        flow_features: Optional[dict] = None,
        host_features: Optional[dict] = None,
    ) -> list[dict[str, Any]]:
        priors = TRANSITION_PRIORS.get(current_stage, [("unknown", 1.0)])
        predictions = []
        for stage_name, prob in priors:
            for horizon in [10, 30, 60, 300]:
            	time_factor = 1.0 - (horizon / 600.0) * 0.3
            	adj_prob = prob * time_factor
            	predictions.append({
                    "stage": stage_name,
                    "probability": round(adj_prob, 4),
                    "horizon_seconds": horizon,
                    "horizon_label": self._horizon_label(horizon),
            	})
        return predictions

    def _predict_targets(
        self,
        src_host_id: str,
        src_host_ip: str,
        current_stage: str,
        graph_context: Optional[dict] = None,
    ) -> list[dict[str, Any]]:
        if current_stage in ("benign", "unknown"):
            return []
        if graph_context and "neighbors" in graph_context:
            targets = []
            for neighbor in graph_context["neighbors"][:5]:
                score = 0.5
                reasoning = []
                if neighbor.get("has_services"):
                    score += 0.15
                    reasoning.append("Exposes services")
                if neighbor.get("criticality") in ("high", "critical"):
                    score += 0.2
                    reasoning.append(f"Asset criticality: {neighbor.get('criticality')}")
                if neighbor.get("bytes_exchanged", 0) > 0:
                    score += 0.1
                    reasoning.append("Prior communication observed")
                targets.append({
                    "host_id": neighbor.get("host_id", ""),
                    "host_ip": neighbor.get("ip", ""),
                    "hostname": neighbor.get("hostname"),
                    "probability": round(min(1.0, score), 4),
                    "reasoning": reasoning,
                })
            targets.sort(key=lambda x: -x["probability"])
            total = sum(t["probability"] for t in targets)
            if total > 0:
                for t in targets:
                    t["probability"] = round(t["probability"] / total, 4)
            return targets
        return []

    def _generate_explanation(
        self,
        current_stage: str,
        confidence: float,
        predictions: list[dict],
        evidence_sources: list[str],
    ) -> dict[str, Any]:
        top_pred = predictions[0] if predictions else None
        what = top_pred["stage"] if top_pred else "unknown"
        when = f"Next {top_pred['horizon_seconds']}s" if top_pred else "unknown"
        why = evidence_sources[:6]
        conf = round(confidence * 100, 1)
        return {
            "what": f"Possible {what.replace('_', ' ')}",
            "when": when,
            "confidence_pct": conf,
            "why": why,
            "current_stage": current_stage,
            "model": "ensemble_v1",
        }

    @staticmethod
    def _horizon_label(seconds: int) -> str:
        if seconds < 60:
            return f"T+{seconds}s"
        return f"T+{seconds // 60}m"

    @staticmethod
    def _calc_entropy(predictions: list[dict]) -> float:
        import math
        probs = [p["probability"] for p in predictions if p.get("horizon_seconds") == 10]
        if not probs:
            return 0.0
        total = sum(probs)
        if total <= 0:
            return 0.0
        entropy = -sum((p / total) * math.log2(p / total) for p in probs if p > 0)
        return round(entropy, 4)

    @staticmethod
    def _calc_confidence_spread(predictions: list[dict]) -> float:
        probs = [p["probability"] for p in predictions if p.get("horizon_seconds") == 10]
        if len(probs) < 2:
            return 0.0
        return round(max(probs) - min(probs), 4)

    def get_current_forecast(self) -> dict[str, Any]:
        active = self.attack_sm.get_active_attacks()
        latest_forecasts = []
        for host_id, records in self._host_forecasts.items():
            if records:
                latest_forecasts.append(records[-1].to_dict())
        return {
            "active_attacks": active,
            "latest_forecasts": latest_forecasts[-20:],
            "stage_distribution": self.attack_sm.get_stage_distribution(),
        }

    def get_forecast_history(self, host_id: Optional[str] = None,
                              limit: int = 50) -> list[dict]:
        if host_id:
            records = self._host_forecasts.get(host_id, [])
        else:
            records = self._forecast_history
        return [r.to_dict() for r in records[-limit:]]

    def get_forecast_vs_actual(self, limit: int = 50) -> list[dict]:
        results = []
        for record in self._forecast_history[-limit:]:
            entry = {
                "forecast_id": record.forecast_id,
                "timestamp": record.timestamp.isoformat(),
                "host_id": record.host_id,
                "predicted_stage": record.predictions[0]["stage"] if record.predictions else None,
                "predicted_confidence": record.predictions[0]["probability"] if record.predictions else 0,
                "actual_outcome": record.actual_outcome,
                "actual_outcome_time": record.actual_outcome_time.isoformat() if record.actual_outcome_time else None,
                "correct": (
                    record.actual_outcome == record.predictions[0]["stage"]
                    if record.actual_outcome and record.predictions else None
                ),
            }
            results.append(entry)
        return results

    def record_actual_outcome(self, host_id: str, actual_stage: str) -> None:
        records = self._host_forecasts.get(host_id, [])
        now = datetime.now(timezone.utc)
        for record in reversed(records[-10:]):
            if record.actual_outcome is None:
                record.actual_outcome = actual_stage
                record.actual_outcome_time = now
                break
