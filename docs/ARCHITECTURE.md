# Architecture Document

## Overview
Netra follows a scalable, microservices-oriented architecture designed to handle high-throughput network telemetry and perform real-time AI inference.

## Components
1. **Sensors**: Edge components responsible for reading network interfaces, parsing packets (Suricata, Zeek), and sending normalized JSON payloads.
2. **Message Queue (Valkey)**: Buffers incoming telemetry to handle traffic spikes.
3. **API Layer (FastAPI)**: Ingests data, serves the frontend, and coordinates background tasks.
4. **Data Store (TimescaleDB)**: PostgreSQL extension optimized for time-series data. Stores all events, alerts, and PCAP metadata.
5. **AI Engine**: Python-based ML models that analyze sliding windows of network traffic to forecast MITRE ATT&CK techniques.
6. **Frontend**: React Single Page Application providing dashboards, alerts, and forensic views.
