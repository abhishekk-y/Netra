# SIH Judges Guide

## Welcome to NETRA-X
NETRA-X solves Problem Statement 26153 by shifting the paradigm from *detection* to *forecasting*.

## What Makes NETRA-X Different
Traditional NDRs alert you *after* a lateral movement or exfiltration event has occurred. NETRA-X observes Reconnaissance and Initial Access, and uses ML to probabilistically forecast the exact host that will be targeted for Lateral Movement next.

## Evaluation Checklist
1. **Real-time Ingestion**: We natively integrate Zeek and Suricata logs.
2. **Predictive Engine**: Watch our demo transition from "Active Threat" to "Forecasted Next Stage".
3. **Forensic Capabilities**: We link flows using Community ID, enabling one-click PCAP retrieval.

## Guided Demo
Please refer to `docs/DEMO.md` to run the interactive `judge_mode.py` script.
