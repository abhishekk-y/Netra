# Machine Learning Pipeline

## Overview
NETRA-X utilizes a multi-stage ML pipeline to detect anomalies and forecast attacks.

## Pipeline Stages
1. **Feature Extraction**: Network packets are summarized into flow records (duration, bytes in/out, packet inter-arrival times).
2. **Behavioral Baselining**: An Autoencoder learns the normal baseline of the network (Phase 1).
3. **Anomaly Detection**: Deviations from the baseline are flagged as anomalous.
4. **Sequence Modeling**: An LSTM network processes the sequence of anomalies to predict the next MITRE ATT&CK tactic.
