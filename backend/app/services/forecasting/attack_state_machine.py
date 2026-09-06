"""
Netra — Attack State Machine
Models security progression around ATT&CK-aligned stages.
Tracks per-host attack state with confidence, evidence, and transitions.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class AttackStage(str, Enum):
    BENIGN = "benign"
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_DEVELOPMENT = "resource_development"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"
    UNKNOWN = "unknown"


STAGE_ORDER: dict[AttackStage, int] = {
    AttackStage.BENIGN: 0,
    AttackStage.RECONNAISSANCE: 1,
    AttackStage.RESOURCE_DEVELOPMENT: 2,
    AttackStage.INITIAL_ACCESS: 3,
    AttackStage.EXECUTION: 4,
    AttackStage.PERSISTENCE: 5,
    AttackStage.PRIVILEGE_ESCALATION: 6,
    AttackStage.DEFENSE_EVASION: 7,
    AttackStage.CREDENTIAL_ACCESS: 8,
    AttackStage.DISCOVERY: 9,
    AttackStage.LATERAL_MOVEMENT: 10,
    AttackStage.COLLECTION: 11,
    AttackStage.COMMAND_AND_CONTROL: 12,
    AttackStage.EXFILTRATION: 13,
    AttackStage.IMPACT: 14,
    AttackStage.UNKNOWN: -1,
}

STAGE_SEVERITY: dict[AttackStage, str] = {
    AttackStage.BENIGN: "info",
    AttackStage.RECONNAISSANCE: "low",
    AttackStage.RESOURCE_DEVELOPMENT: "low",
    AttackStage.INITIAL_ACCESS: "medium",
    AttackStage.EXECUTION: "medium",
    AttackStage.PERSISTENCE: "medium",
    AttackStage.PRIVILEGE_ESCALATION: "high",
    AttackStage.DEFENSE_EVASION: "medium",
    AttackStage.CREDENTIAL_ACCESS: "high",
    AttackStage.DISCOVERY: "low",
    AttackStage.LATERAL_MOVEMENT: "high",
    AttackStage.COLLECTION: "high",
    AttackStage.COMMAND_AND_CONTROL: "critical",
    AttackStage.EXFILTRATION: "critical",
    AttackStage.IMPACT: "critical",
    AttackStage.UNKNOWN: "info",
}

# Minimum evidence threshold to transition to each stage
EVIDENCE_THRESHOLDS: dict[AttackStage, float] = {
    AttackStage.BENIGN: 0.0,
    AttackStage.RECONNAISSANCE: 0.3,
    AttackStage.INITIAL_ACCESS: 0.4,
    AttackStage.EXECUTION: 0.5,
    AttackStage.PERSISTENCE: 0.5,
    AttackStage.PRIVILEGE_ESCALATION: 0.5,
    AttackStage.DEFENSE_EVASION: 0.4,
    AttackStage.CREDENTIAL_ACCESS: 0.4,
    AttackStage.DISCOVERY: 0.3,
    AttackStage.LATERAL_MOVEMENT: 0.5,
    AttackStage.COLLECTION: 0.5,
    AttackStage.COMMAND_AND_CONTROL: 0.5,
    AttackStage.EXFILTRATION: 0.5,
    AttackStage.IMPACT: 0.6,
    AttackStage.UNKNOWN: 0.0,
}


@dataclass
class StageEvidence:
    """Evidence supporting an attack stage assessment."""
    stage: AttackStage
    confidence: float
    sources: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "confidence": round(self.confidence, 4),
            "sources": self.sources,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HostAttackState:
    """Current attack state for a single host."""
    host_id: str
    host_ip: str
    current_stage: AttackStage = AttackStage.BENIGN
    current_confidence: float = 1.0
    stage_history: list[dict] = field(default_factory=list)
    evidence_buffer: dict[str, list[StageEvidence]] = field(default_factory=dict)
    entered_stage_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_evidence_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "host_ip": self.host_ip,
            "current_stage": self.current_stage.value,
            "current_confidence": round(self.current_confidence, 4),
            "severity": STAGE_SEVERITY.get(self.current_stage, "info"),
            "entered_stage_at": self.entered_stage_at.isoformat(),
            "stage_history": self.stage_history[-50:],
            "total_evidence_count": self.total_evidence_count,
        }


class AttackStateMachine:
    """
    Tracks attack progression per host using evidence accumulation.
    Never claims a tactic without sufficient evidence.
    """

    def __init__(self, decay_rate: float = 0.95, min_confidence: float = 0.1):
        self._host_states: dict[str, HostAttackState] = {}
        self._decay_rate = decay_rate
        self._min_confidence = min_confidence

    def get_or_create_state(self, host_id: str, host_ip: str) -> HostAttackState:
        if host_id not in self._host_states:
            self._host_states[host_id] = HostAttackState(
                host_id=host_id, host_ip=host_ip
            )
        return self._host_states[host_id]

    def add_evidence(
        self,
        host_id: str,
        host_ip: str,
        stage: AttackStage,
        confidence: float,
        sources: list[str],
    ) -> Optional[dict[str, Any]]:
        state = self.get_or_create_state(host_id, host_ip)
        evidence = StageEvidence(
            stage=stage,
            confidence=min(1.0, max(0.0, confidence)),
            sources=sources,
        )
        stage_key = stage.value
        if stage_key not in state.evidence_buffer:
            state.evidence_buffer[stage_key] = []
        state.evidence_buffer[stage_key].append(evidence)
        if len(state.evidence_buffer[stage_key]) > 100:
            state.evidence_buffer[stage_key] = state.evidence_buffer[stage_key][-50:]
        state.total_evidence_count += 1

        return self._evaluate_transition(state)

    def _evaluate_transition(self, state: HostAttackState) -> Optional[dict[str, Any]]:
        stage_scores: dict[AttackStage, float] = {}

        for stage_key, evidences in state.evidence_buffer.items():
            try:
                stage = AttackStage(stage_key)
            except ValueError:
                continue

            if not evidences:
                continue

            weighted_sum = 0.0
            weight_total = 0.0
            now = datetime.now(timezone.utc)
            for ev in evidences:
                age_seconds = (now - ev.timestamp).total_seconds()
                decay = self._decay_rate ** (age_seconds / 60.0)
                w = decay
                weighted_sum += ev.confidence * w
                weight_total += w

            avg_conf = weighted_sum / weight_total if weight_total > 0 else 0.0
            count_boost = min(1.0, len(evidences) / 5.0)
            score = avg_conf * (0.6 + 0.4 * count_boost)
            stage_scores[stage] = score

        if not stage_scores:
            return None

        best_stage = max(stage_scores, key=lambda s: stage_scores[s])
        best_score = stage_scores[best_stage]
        threshold = EVIDENCE_THRESHOLDS.get(best_stage, 0.5)

        if best_score < threshold:
            if best_score > self._min_confidence and best_stage != AttackStage.BENIGN:
                best_stage = AttackStage.UNKNOWN
                best_score = best_score * 0.5
            else:
                return None

        if best_stage != state.current_stage:
            transition = {
                "host_id": state.host_id,
                "host_ip": state.host_ip,
                "previous_stage": state.current_stage.value,
                "new_stage": best_stage.value,
                "confidence": round(best_score, 4),
                "severity": STAGE_SEVERITY.get(best_stage, "info"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evidence_count": state.total_evidence_count,
            }
            state.stage_history.append(transition)
            state.current_stage = best_stage
            state.current_confidence = best_score
            state.entered_stage_at = datetime.now(timezone.utc)
            return transition

        state.current_confidence = max(state.current_confidence, best_score)
        return None

    def get_state(self, host_id: str) -> Optional[dict[str, Any]]:
        state = self._host_states.get(host_id)
        return state.to_dict() if state else None

    def get_all_states(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self._host_states.values()]

    def get_active_attacks(self) -> list[dict[str, Any]]:
        return [
            s.to_dict() for s in self._host_states.values()
            if s.current_stage not in (AttackStage.BENIGN, AttackStage.UNKNOWN)
        ]

    def get_stage_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for state in self._host_states.values():
            stage = state.current_stage.value
            dist[stage] = dist.get(stage, 0) + 1
        return dist

    def reset_host(self, host_id: str) -> None:
        if host_id in self._host_states:
            state = self._host_states[host_id]
            state.current_stage = AttackStage.BENIGN
            state.current_confidence = 1.0
            state.evidence_buffer.clear()
            state.entered_stage_at = datetime.now(timezone.utc)
