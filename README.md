<p align="center">
  <img src="docs/assets/netra-logo.svg" alt="Netra" width="80" height="80" />
</p>

<h1 align="center">NETRA</h1>

<p align="center">
  <strong>Network Evolution, Threat Recognition & Attack Forecasting Intelligence System</strong>
</p>

<p align="center">
  <a href="#architecture"><img src="https://img.shields.io/badge/Architecture-Microservices-0066CC?style=flat-square&logo=blueprint" alt="Architecture" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" /></a>
  <a href="#tech-stack"><img src="https://img.shields.io/badge/PyTorch-2.4-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch" /></a>
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" /></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#demo">Demo</a> ·
  <a href="#research">Research</a> ·
  <a href="#api-reference">API</a>
</p>

---

> **Smart India Hackathon 2026 — Problem Statement ID: 26153**
>
> *AI based Network Attack Forecasting from Network Traffic Data*

---

## Overview

Netra is a unified **Network Intelligence, Detection & Response, Forensics, and Attack Forecasting** platform. Unlike traditional IDS/IPS that only detect ongoing attacks, Netra **forecasts probable next attack stages, predicts likely targets, and visualizes attack paths** — all on a live, automatically-generated network topology.

```
Traditional IDS:    Traffic → Attack Detected.

Netra:              Historical State + Current State + Topology + Behavior + Evidence
                    → Current Attack Stage
                    → Next Probable Stages (with confidence)
                    → Probable Next Target
                    → Expected Attack Path
                    → Impact / Blast Radius
                    → Recommended Response
```

### What Makes Netra Different

| # | Capability | Description |
|---|-----------|-------------|
| 1 | **Automatic Network Digital Twin** | The network topology draws itself from observed traffic |
| 2 | **Full Network Observability** | Packets + Flows + Protocols + Topology + eBPF |
| 3 | **Deep Packet Forensics** | Alert → Incident → Flow → Session → Packet |
| 4 | **Behavioral NDR** | Learns normal vs. abnormal per-host behavior |
| 5 | **Attack Stage Forecasting** | Predicts what attack stage comes next |
| 6 | **Target Prediction** | Predicts which host will be targeted next |
| 7 | **Dynamic Attack Graph** | Forecast visualized on live topology |
| 8 | **Forecast Explainability** | Every prediction shows why, when, where, confidence |
| 9 | **Incident Black Box** | Complete chronological attack replay |
| 10 | **Optional Deception** | Honeypot integration for active defense |
| 11 | **Modern Telemetry** | Zeek + Suricata + PCAP + JA4 + Community ID |
| 12 | **Offline-First** | Works without any cloud APIs |

---

## Features

### Network Digital Twin & Topology

```
                          INTERNET
                             │
                        [ Gateway ]
                             │
                        [ Firewall ]
                             │
                      [ Core Switch ]
                       /     |     \
                      /      |      \
            [Switch-A]   [Server]  [Switch-B]
                │           │          │
          ┌─────┴────┐   ┌──┴──┐    ┌──┴─────┐
          PC-01  PC-02  WEB   DB   AP-01  CCTV
```

- **Passive Discovery**: ARP, DHCP, DNS, LLDP, CDP, STP, mDNS, SSDP, MAC OUI, VLAN tags, flow relationships
- **Device Classification**: Router, Switch, Firewall, Server, Workstation, IoT, Camera — each with confidence + evidence
- **10 View Modes**: Physical, L2, L3, Logical, Security, Attack, Forensic, Forecast, VLAN, Subnet
- **Layout Engines**: Hierarchical, Force-directed, Radial, Tree
- **Topology Time Machine**: Replay network state at any past timestamp
- **Topology Diff**: Compare two points in time — see what changed

### Attack Forecasting Engine

```
  ┌─────────────────────────────────────────────────┐
  │              CURRENT STATE                      │
  │  Stage: Reconnaissance    Confidence: 91%       │
  ├─────────────────────────────────────────────────┤
  │           FORECAST (Next 60 seconds)            │
  │                                                 │
  │  Initial Access ............... ████████ 48%    │
  │  Credential Access ........... ██████   29%     │
  │  Reconnaissance continues .... ████     16%     │
  │  Session Ends ................ ██        7%     │
  ├─────────────────────────────────────────────────┤
  │           NEXT LIKELY TARGET                    │
  │  192.168.56.20  Ubuntu Web Server  Prob: 61%   │
  ├─────────────────────────────────────────────────┤
  │           EXPECTED PATH                         │
  │  Kali → Web Server → App Server → Database     │
  │  Critical Asset Exposure: HIGH                  │
  └─────────────────────────────────────────────────┘
```

- **Multi-Horizon**: T+10s, T+30s, T+1m, T+5m
- **Top-K Predictions**: Multiple scenarios with probability distributions
- **Uncertainty Quantification**: Entropy, confidence spread, calibration metrics
- **Forecast vs. Reality**: Compare what was predicted against what happened

### Multi-Engine Detection

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Engine A: Signatures      │ Suricata rules, Zeek notices   │
  │  Engine B: Statistical     │ Z-score, EWMA, MAD, Entropy   │
  │  Engine C: Unsupervised    │ Isolation Forest, Autoencoder  │
  │  Engine D: Supervised      │ XGBoost multi-class classifier │
  │  Engine E: Temporal        │ GRU / LSTM sequence models     │
  │  Engine F: Graph           │ NetworkX graph analytics       │
  │  Engine G: Correlation     │ Multi-event temporal rules     │
  └──────────────────────────────────────────────────────────────┘
```

### Explainable Risk Scoring

```
  RISK 82
  ├── Forecast contribution:         +26
  ├── Behavior anomaly:              +21
  ├── Signature match:               +14
  ├── Critical asset proximity:      +12
  └── New destination observed:       +9
```

No magic scores. Every value is traceable and decomposable.

### Forensic Replay (Incident Black Box)

Controls: `PLAY` `PAUSE` `STEP BACK` `STEP FORWARD` `0.5x` `1x` `2x` `5x` `10x`

- Topology changes over time
- Edges appear and disappear
- Risk propagation visible
- Attack state transitions
- Forecast probabilities update in real-time
- All from **real recorded incident data**

---

## Architecture

```
 ┌─────────────────────────────────────────────────────────────────┐
 │                        DATA SOURCES                            │
 │  PCAP Files │ Live Capture │ Zeek │ Suricata │ IPFIX │ eBPF   │
 └──────┬──────┴──────┬───────┴──┬───┴────┬─────┴───┬───┴────┬───┘
        │             │          │        │         │        │
 ┌──────▼─────────────▼──────────▼────────▼─────────▼────────▼───┐
 │                     INGESTION LAYER                            │
 │  Capture Adapter │ Event Normalizer │ Community ID │ Flow Eng  │
 └──────┬──────────────────────┬──────────────────────┬──────────┘
        │                      │                      │
 ┌──────▼──────────┐   ┌──────▼──────────┐   ┌──────▼──────────┐
 │  INTELLIGENCE   │   │   DETECTION     │   │  FORECASTING    │
 │  Topology Disc. │   │   Signatures    │   │  Attack State   │
 │  Device Class.  │   │   Statistical   │   │  GRU Sequence   │
 │  Host Profiler  │   │   IsolationForest│  │  LSTM Temporal  │
 │  Baseline Eng.  │   │   XGBoost       │   │  Target Predict │
 │  Fingerprinting │   │   Correlation   │   │  Explainability │
 └──────┬──────────┘   └──────┬──────────┘   └──────┬──────────┘
        │                      │                      │
 ┌──────▼──────────────────────▼──────────────────────▼──────────┐
 │                      RESPONSE LAYER                            │
 │  Risk Engine │ Incident Manager │ ATT&CK Mapper │ Deception   │
 └──────┬──────────────────────┬──────────────────────┬──────────┘
        │                      │                      │
 ┌──────▼──────────┐   ┌──────▼──────────┐   ┌──────▼──────────┐
 │    STORAGE      │   │     API         │   │   FRONTEND      │
 │  PostgreSQL +   │   │   FastAPI REST  │   │  React + TS     │
 │  TimescaleDB    │   │   WebSocket     │   │  Cytoscape.js   │
 │  Valkey/Redis   │   │   50+ Endpoints │   │  ECharts        │
 │  PCAP Store     │   │                 │   │  Tailwind CSS   │
 └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### ML Model Pipeline

| Model | Architecture | Purpose | Input | Output |
|-------|-------------|---------|-------|--------|
| Flow Classifier | XGBoost | Multi-class attack classification | 40+ flow features | Attack type + confidence |
| Anomaly Detector | Isolation Forest | Unsupervised anomaly scoring | Flow + host features | Score 0-100 |
| Behavior Model | Dense Autoencoder | Reconstruction-error anomaly | Host behavior vectors | Reconstruction error |
| Stage Forecaster | GRU (2-layer, 128h) | Next attack stage prediction | Attack state sequence | Top-K stages + probabilities |
| Temporal Forecaster | LSTM (2-layer, 256h) | Multi-horizon forecasting | Time-windowed features | Stage probs at T+10s/30s/1m/5m |
| Target Predictor | MLP + Graph features | Probable next target host | Graph + host + context | Host probability ranking |
| Changepoint Detector | BOCPD | Behavioral regime detection | Time series metric | Changepoint + confidence |

### Database Schema

```
 ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
 │   hosts     │────▶│    flows     │────▶│   alerts     │
 │  (identity) │     │ (hypertable) │     │ (hypertable) │
 └──────┬──────┘     └──────┬───────┘     └──────┬───────┘
        │                   │                     │
 ┌──────▼──────┐     ┌──────▼───────┐     ┌──────▼───────┐
 │  baselines  │     │   events     │     │  incidents   │
 │ (per-host)  │     │ (normalized) │     │ (correlated) │
 └─────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
 ┌─────────────┐     ┌──────────────┐     ┌──────▼───────┐
 │  topology   │     │  dns_records │     │  forecasts   │
 │  nodes/edges│     │ (hypertable) │     │ (hypertable) │
 └─────────────┘     └──────────────┘     └──────────────┘

 ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
 │ risk_scores │     │ tls_records  │     │  pcap_index  │
 │ (hypertable)│     │ (hypertable) │     │ (evidence)   │
 └─────────────┘     └──────────────┘     └──────────────┘
```

All time-series tables use **TimescaleDB hypertables** for efficient range queries.

---

## Project Structure

```
netra/
├── frontend/                          # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/             # SOC Dashboard
│   │   │   ├── topology/              # Cytoscape.js topology canvas
│   │   │   ├── forecast/              # Attack forecasting display
│   │   │   ├── packets/               # Wireshark-inspired packet explorer
│   │   │   ├── incidents/             # Incident management
│   │   │   ├── flows/                 # Flow analytics
│   │   │   ├── alerts/                # Alert management
│   │   │   ├── hunting/               # Threat hunting workspace
│   │   │   ├── mitre/                 # ATT&CK matrix
│   │   │   ├── forensics/             # Incident replay
│   │   │   ├── assets/                # Asset inventory
│   │   │   ├── dns/                   # DNS forensics
│   │   │   ├── tls/                   # TLS forensics
│   │   │   ├── deception/             # Honeypot management
│   │   │   ├── health/                # System health
│   │   │   ├── settings/              # Configuration
│   │   │   └── common/                # Shared components
│   │   ├── stores/                    # Zustand state management
│   │   ├── services/                  # API + WebSocket clients
│   │   ├── hooks/                     # React hooks
│   │   ├── types/                     # TypeScript types
│   │   └── utils/                     # Utilities
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                           # Python FastAPI
│   └── app/
│       ├── api/v1/                    # 19 REST endpoint modules
│       │   ├── auth.py                # Authentication
│       │   ├── dashboard.py           # SOC metrics
│       │   ├── hosts.py               # Host management
│       │   ├── topology.py            # Topology graph/diff/path
│       │   ├── flows.py               # Flow analytics
│       │   ├── alerts.py              # Alert management
│       │   ├── incidents.py           # Incident lifecycle
│       │   ├── forecasts.py           # Attack forecasting
│       │   ├── packets.py             # Packet exploration
│       │   ├── dns.py                 # DNS forensics
│       │   ├── tls.py                 # TLS forensics
│       │   ├── assets.py              # Asset inventory
│       │   ├── mitre.py               # ATT&CK mapping
│       │   ├── risk.py                # Risk scoring
│       │   ├── hunting.py             # Threat hunting queries
│       │   ├── forensics.py           # Evidence & replay
│       │   ├── deception.py           # Honeypot management
│       │   ├── health.py              # System health
│       │   └── settings.py            # Feature flags
│       ├── core/                      # Config, DB, Security, Events
│       ├── models/                    # 14 SQLAlchemy models
│       ├── schemas/                   # Pydantic v2 schemas
│       ├── services/
│       │   ├── telemetry/             # Community ID, Normalizer, Flow Engine
│       │   ├── topology/              # Discovery, Classifier, Builder, Snapshot, Path
│       │   ├── detection/             # Statistical, ML, Correlation, Manager
│       │   ├── forecasting/           # Attack State Machine, Forecast Manager
│       │   ├── profiling/             # Host Profiler, Baseline Engine
│       │   ├── risk/                  # Explainable Risk Engine
│       │   ├── incidents/             # Incident Manager
│       │   ├── mitre/                 # ATT&CK Mapper + 35 techniques
│       │   ├── forensics/             # Evidence Engine, PCAP Manager
│       │   └── health/                # Health Monitor, Sensor Quality
│       └── websocket/                 # Real-time WebSocket manager
│
├── ml/                                # Machine Learning Pipeline
│   ├── features/                      # Feature extraction (40+ flow features)
│   │   ├── flow_features.py           # Per-flow features
│   │   ├── host_features.py           # Per-host behavioral features
│   │   ├── temporal_features.py       # Sequence features for RNNs
│   │   └── graph_features.py          # NetworkX graph features
│   ├── models/                        # 7 ML models
│   │   ├── classifier.py              # XGBoost flow classifier
│   │   ├── anomaly.py                 # Isolation Forest
│   │   ├── autoencoder.py             # PyTorch behavior autoencoder
│   │   ├── sequence_model.py          # GRU next-stage predictor
│   │   ├── temporal_model.py          # LSTM multi-horizon forecaster
│   │   ├── target_model.py            # Target prediction MLP
│   │   └── changepoint.py             # BOCPD changepoint detector
│   ├── datasets/adapters/             # CIC-IDS2017, CIC-IDS2018, UNSW-NB15
│   ├── training/                      # Training scripts
│   ├── inference/                     # Real-time inference engine
│   └── metrics/                       # Forecast metrics + calibration
│
├── sensor/                            # Network Sensor Layer
│   ├── capture/                       # PCAP capture (Scapy)
│   ├── zeek/                          # Zeek log watcher
│   ├── suricata/                      # Suricata EVE watcher
│   ├── normalizer/                    # Event normalization
│   └── health/                        # Sensor health reporter
│
├── demo/                              # SIH Demo Tooling
│   ├── traffic_generator.py           # Safe traffic generation
│   ├── attack_scenarios.py            # 6-phase demo scenario
│   └── judge_mode.py                  # Judge presentation controller
│
├── tests/                             # Unit + Integration tests
├── docs/                              # Documentation
├── docker/                            # Dockerfiles + DB init
├── docker-compose.yml                 # Full stack orchestration
├── .env.example                       # Environment template
├── start.sh                           # Linux startup
├── start.ps1                          # Windows startup
└── README.md                          # This file
```

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Core runtime |
| FastAPI | 0.115+ | Async REST API + WebSocket |
| SQLAlchemy | 2.0+ | Async ORM |
| Pydantic | 2.9+ | Data validation + schemas |
| PostgreSQL | 16 | Primary database |
| TimescaleDB | 2.x | Time-series hypertables |
| Valkey | 8 | Event bus, caching, pub/sub |
| Scapy | 2.6+ | Packet parsing |
| structlog | 24.x | Structured JSON logging |

### Machine Learning

| Technology | Version | Purpose |
|-----------|---------|---------|
| PyTorch | 2.4+ | GRU, LSTM, Autoencoder, MLP |
| XGBoost | 2.1+ | Flow classification |
| scikit-learn | 1.5+ | Isolation Forest, preprocessing |
| NetworkX | 3.4+ | Graph analytics |
| NumPy | 1.26+ | Numerical operations |
| Pandas | 2.2+ | Data manipulation |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 5.6 | Type safety |
| Vite | 5.4 | Build tooling |
| Tailwind CSS | 3.4 | Styling |
| Cytoscape.js | 3.30 | Topology visualization |
| ECharts | 5.5 | Charts + graphs |
| Zustand | 5.0 | State management |
| TanStack Query | 5.59 | Server state |
| Lucide React | 0.453 | Icons |

### Optional Integrations

| Technology | Purpose | Required |
|-----------|---------|----------|
| Zeek 8.x | Semantic network telemetry | Optional |
| Suricata 8.x | Signature-based IDS | Optional |
| Arkime 6.x | Full packet capture indexing | Optional |
| Tetragon | eBPF process attribution | Optional |
| Cowrie/OpenCanary | Honeypot deception | Optional |
| NetBox | Infrastructure CMDB | Optional |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- 8GB+ RAM, 4+ CPU cores

### Installation

```bash
# Clone the repository
git clone https://github.com/abhishekk-y/Netra.git
cd Netra

# Configure environment
cp .env.example .env

# Start all services
docker compose up -d

# Or use the start script
./start.sh          # Linux/macOS
.\start.ps1         # Windows PowerShell
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

Default credentials: `admin` / `admin`

### Development Mode

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

---

## Demo

### Lab Network Setup

```
┌─────────────────────────────────────────────────────────┐
│                    HOST MACHINE                         │
│                   Windows 11                            │
│                                                         │
│  ┌─────────────────────────────────────────────┐        │
│  │              Netra Platform                 │        │
│  │   Frontend :3000  │  Backend :8000          │        │
│  │   PostgreSQL :5432 │  Valkey :6379          │        │
│  └─────────────────────────────────────────────┘        │
│                                                         │
│  VirtualBox Host-Only: 192.168.56.0/24                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Kali      │  │  Ubuntu    │  │  Honeypot  │        │
│  │  .56.10    │  │  .56.20    │  │  .56.30    │        │
│  │  Attacker  │  │  Server    │  │  Deception │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Demo Scenario (6 Phases)

| Phase | Duration | Activity | Netra Response |
|-------|----------|----------|----------------|
| 1. Normal | 60s | HTTP, DNS baseline | Topology builds, baselines learn |
| 2. Recon | 30s | Port scanning | Stage: Reconnaissance (91%) |
| 3. Access | 30s | SSH brute force | Forecast: Credential Access (48%) |
| 4. Lateral | 30s | Internal SSH | Target prediction shown on topology |
| 5. C2 | 30s | HTTP beaconing | Beaconing analytics trigger |
| 6. Exfil | 30s | Large transfer | Critical risk, incident created |

```bash
# Run the demo scenario
python demo/judge_mode.py
```

---

## API Reference

### Core Endpoints (50+)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | Authenticate |
| `/api/v1/dashboard/summary` | GET | SOC dashboard metrics |
| `/api/v1/hosts` | GET | List discovered hosts |
| `/api/v1/hosts/{id}` | GET | Host profile (identity, services, traffic, security, behavior) |
| `/api/v1/topology/graph` | GET | Live topology (10 view modes) |
| `/api/v1/topology/diff` | GET | Topology diff between timestamps |
| `/api/v1/topology/path` | GET | Communication path analysis |
| `/api/v1/flows` | GET | Flow search with 40+ features |
| `/api/v1/alerts` | GET | Alert search and filtering |
| `/api/v1/incidents` | GET/POST | Incident CRUD |
| `/api/v1/incidents/{id}/evidence` | GET | Evidence graph |
| `/api/v1/incidents/{id}/replay` | GET | Forensic replay data |
| `/api/v1/forecasts/current` | GET | Current attack state + forecast |
| `/api/v1/forecasts/vs-actual` | GET | Forecast accuracy timeline |
| `/api/v1/packets/search` | GET | Packet search |
| `/api/v1/packets/{id}/decode` | GET | Protocol layer decode |
| `/api/v1/dns/queries` | GET | DNS query forensics |
| `/api/v1/dns/analysis` | GET | DNS analytics (tunneling, DGA) |
| `/api/v1/tls/fingerprints` | GET | JA4 fingerprint inventory |
| `/api/v1/mitre/matrix` | GET | ATT&CK coverage matrix |
| `/api/v1/risk/scores` | GET | Explainable risk scores |
| `/api/v1/hunting/query` | POST | Investigation query language |
| `/api/v1/health` | GET | System component health |

### WebSocket Events

| Channel | Event | Description |
|---------|-------|-------------|
| `telemetry` | `flow.new` | New flow observed |
| `topology` | `node.discovered` | New host on network |
| `topology` | `edge.new` | New communication link |
| `alerts` | `alert.new` | Detection alert |
| `incidents` | `incident.new` | New correlated incident |
| `forecast` | `forecast.new` | Attack forecast update |
| `forecast` | `state.change` | Attack stage transition |
| `risk` | `risk.critical` | Critical risk threshold |
| `health` | `component.status` | Component health change |

---

## MITRE ATT&CK Coverage

Netra maps detections and forecasts to **35+ network-observable ATT&CK techniques**:

| Tactic | Techniques |
|--------|-----------|
| Reconnaissance | T1595 Active Scanning, T1046 Network Service Discovery |
| Initial Access | T1190 Exploit Public-Facing App, T1133 External Remote Services |
| Credential Access | T1110 Brute Force, T1557 Adversary-in-the-Middle |
| Lateral Movement | T1021 Remote Services (RDP/SSH/SMB), T1570 Lateral Tool Transfer |
| Command & Control | T1071 App Layer Protocol, T1573 Encrypted Channel, T1571 Non-Standard Port |
| Exfiltration | T1041 Over C2, T1048 Alternative Protocol, T1567 Web Service |
| Impact | T1498 Network DoS, T1499 Endpoint DoS |

Observed techniques are shown with **solid highlighting**. Forecast techniques use **dashed/hatched** styling.

---

## Research & References

### Foundational Research

| Paper | Authors | Relevance |
|-------|---------|-----------|
| *Network Intrusion Detection using CIC-IDS2017* | Sharafaldin et al., 2018 | Dataset design, flow feature methodology |
| *UNSW-NB15: A Comprehensive Data Set for Network Intrusion Detection* | Moustafa & Slay, 2015 | Attack taxonomy, evaluation benchmarks |
| *A Survey on Network Intrusion Detection Using ML* | Buczak & Guven, 2016 | Multi-engine detection architecture |
| *Deep Learning Approach for Network Intrusion Detection* | Vinayakumar et al., 2019 | LSTM/GRU for temporal detection |
| *Isolation Forest* | Liu et al., 2008 | Unsupervised anomaly detection |
| *XGBoost: A Scalable Tree Boosting System* | Chen & Guestrin, 2016 | Flow classification baseline |

### Network Security Standards

| Standard | Application in Netra |
|----------|---------------------|
| [Community ID Flow Hashing](https://github.com/corelight/community-id-spec) | Universal flow correlation across all engines |
| [MITRE ATT&CK for Enterprise](https://attack.mitre.org/) | Attack stage taxonomy + technique mapping |
| [JA4+ Network Fingerprinting](https://github.com/FoxIO-LLC/ja4) | TLS client/server fingerprinting |
| [Zeek Network Monitor](https://zeek.org/) | Semantic network telemetry source |
| [Suricata IDS](https://suricata.io/) | Signature-based detection engine |
| [Arkime Full Packet Capture](https://arkime.com/) | PCAP indexing architecture reference |

### Architecture Influences

| System | Influence on Netra |
|--------|-------------------|
| Wireshark | Packet explorer UI, protocol decode tree, hex view |
| Security Onion / CISA Malcolm | Multi-tool integration, Community ID correlation |
| Darktrace | Self-learning behavioral baseline, peer group analytics |
| Elastic Security | Alert correlation, investigation workflows |
| Splunk ES | SOC dashboard density, faceted search |
| NetBox | Asset inventory data model |
| Cisco Network Management | Topology iconography, hierarchical layout, professional styling |

### Datasets

| Dataset | Records | Attack Types | Use |
|---------|---------|-------------|-----|
| [CIC-IDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) | 2.8M flows | 14 attack classes | Primary classifier training |
| [CSE-CIC-IDS2018](https://www.unb.ca/cic/datasets/ids-2018.html) | 16M flows | 14 attack classes | Validation dataset |
| [UNSW-NB15](https://research.unsw.edu.au/projects/unsw-nb15-dataset) | 2.5M flows | 10 attack categories | Cross-dataset evaluation |

### Evaluation Metrics

| Metric | Purpose |
|--------|---------|
| Precision, Recall, F1 | Per-class classification quality |
| AUROC, PR-AUC | Overall model discrimination |
| Top-1, Top-3 Accuracy | Forecast stage prediction quality |
| Brier Score | Probabilistic forecast calibration |
| Expected Calibration Error | Confidence reliability |
| Forecast Lead Time | How far ahead correct predictions were made |

---

## Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_ZEEK` | Enabled | Zeek telemetry ingestion |
| `FEATURE_SURICATA` | Disabled | Suricata signature engine |
| `FEATURE_ARKIME` | Disabled | Full PCAP indexing |
| `FEATURE_HONEYPOT` | Disabled | Deception engine |
| `FEATURE_EBPF` | Disabled | eBPF process correlation |
| `FEATURE_GNN` | Disabled | Graph Neural Network |
| `FEATURE_LLM` | Disabled | LLM forensic analyst |
| `FEATURE_NETBOX` | Disabled | NetBox CMDB integration |
| `FEATURE_KUBERNETES` | Disabled | K8s observability |
| `FEATURE_THREAT_INTEL` | Disabled | External threat feeds |

Core system operates fully with all optional features disabled.

---

## Performance Profiles

| Profile | Components | Resource Usage |
|---------|-----------|---------------|
| **LIGHT** | Zeek + Flow metadata + ML | ~4 GB RAM |
| **STANDARD** | Zeek + Suricata + ML + Selective PCAP | ~6 GB RAM |
| **FORENSIC** | Zeek + Suricata + Full PCAP + ML + Evidence | ~8 GB RAM |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Search |
| `F` | Open filter bar |
| `T` | Navigate to topology |
| `P` | Navigate to packets |
| `I` | Navigate to incidents |
| `Esc` | Close panel / inspector |

---

## Security

- JWT authentication with role-based access control (Viewer / Analyst / Senior Analyst / Administrator)
- CSRF protection, input validation, rate limiting
- WebSocket authorization per channel
- PCAP upload validation with size limits
- Secrets via environment variables only
- Full audit trail of analyst actions
- No arbitrary shell execution endpoints
- Evidence integrity via SHA-256 hashing

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

---

## License

This project is developed for Smart India Hackathon 2026.

---

<p align="center">
  <strong>Netra</strong> — Network Evolution, Threat Recognition & Attack Forecasting Intelligence System
</p>
<p align="center">
  SIH 2026 · PS 26153 · AI based Network Attack Forecasting from Network Traffic Data
</p>
