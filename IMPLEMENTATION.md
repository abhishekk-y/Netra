# Implementation ledger

This ledger records verified delivery separately from the broader product specification. An entry becomes complete only after its checks pass. See [architecture](docs/ARCHITECTURE.md) for the frozen interfaces and [project state](PROJECT_STATE.md) for the latest validation.

## Phase 0 — Architecture freeze

Decision: deliver an offline laptop application with React, FastAPI, an in-process event bus, SQLite persistence, passive sensor adapters, and explicit synthetic replay. PostgreSQL/TimescaleDB files from the initial scaffold are retained as migration references, not required runtime services. A two-container deployment avoids unnecessary database/queue overhead. All published ports bind to loopback by default.

Data contract: sensor record → normalized event → observed flow → host/communication graph → evidence-backed detection → incident → recorded heuristic forecast → analyst investigation. Observed activity and estimated future activity remain distinguishable.

## Phase 1 — Core application (in progress)

Parallel implementation: backend API/persistence, frontend working pages, sensor/ML correctness, deployment/documentation. Verification will cover empty telemetry, replay, invalid input, persistence, WebSockets, and frontend production compilation.

## Acceptance boundaries

The requested enterprise vision also includes trained temporal/GNN models, calibrated multi-horizon forecasts, physical L2 infrastructure discovery, Arkime, eBPF, NetBox, IPFIX, honeypot redirection, multi-role access control, and large-scale storage. Those capabilities must not be described as delivered unless an actual implementation and its validation are recorded below. No external live sensor or VM is assumed present on the development laptop.
