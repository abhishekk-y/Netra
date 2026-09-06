# Netra Implementation Status

This document tracks the complete status of what is currently implemented in the Netra project versus what is left, organized by component.

## Backend
- [x] Application structure (FastAPI)
- [x] SQLite database schema and persistence logic
- [x] In-process event bus and WebSockets for real-time updates
- [x] Core API endpoints (REST)
- [/] Risk and profiling services (skeleton/basic logic implemented)
- [ ] Integration with advanced databases (TimescaleDB/PostgreSQL - files exist but currently offline)

## Frontend
- [x] Application layout and routing (React)
- [x] Dashboard UI with TailwindCSS
- [/] Topology graph visualization
- [/] Forensics investigation view
- [ ] Fully functional live WebSocket updates displaying ML predictions

## ML
- [x] Machine Learning pipeline structure setup
- [/] Risk Engine (Placeholder returning deterministic risk scores)
- [/] Host Profiler Service (Basic heuristics)
- [/] Baseline Engine (Simple thresholds)
- [ ] Fully trained LSTM-based forecasting models
- [ ] GNN implementation for lateral movement prediction

## Sensor
- [x] PCAP sensor capture logic
- [x] Zeek log watcher integration
- [x] Suricata EVE watcher integration
- [x] Event Normalizer (Community ID)
- [x] Sensor Health monitoring

## Demo
- [x] Judge Mode Controller
- [x] Demo Traffic Generator (simulated traffic)
- [ ] Live traffic generation requiring root privileges (currently bypassed via simulated data)

## Docs
- [x] Architecture documentation (`ARCHITECTURE.md`)
- [x] Demo guide (`DEMO.md`)
- [x] Installation guide (`INSTALLATION.md`)
- [x] API Reference (`API.md`)
- [x] ML Pipeline (`ML_PIPELINE.md`)
- [x] Forensics and Security docs
- [x] Topology discovery doc
- [x] SIH Judges guide (`SIH_JUDGES_GUIDE.md`)

## Tests
- [x] Pytest skeleton and configuration
- [/] Unit tests for Backend components
- [/] Unit tests for ML pipeline placeholders
- [ ] End-to-end integration tests
- [ ] Frontend component tests
