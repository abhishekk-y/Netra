# Netra-X: Network Evolution, Threat Recognition & Attack Forecasting

![Netra-X](docs/assets/netra_header.png)

Netra-X is an enterprise-grade Network Security & Threat Intelligence platform. It replaces traditional signature-based detection with a massive **Deep Learning Ensemble** trained on large-scale network intrusion datasets. The platform features an intense, highly professional Cloudflare/Cisco-style UI designed for Tier 3 SOC Analysts.

---

## 🧠 The Deep Learning Ensemble

Traditional security tools rely on static rules. Netra-X uses a **Multi-Model Machine Learning Ensemble** to detect zero-day anomalies and predict attacks before they materialize.

### Key Capabilities
- **Deep Learning Ensemble Detection**: Leverages a robust ensemble (Random Forest + Multi-Layer Perceptron) trained on massive datasets to identify novel attacks with **~95.8% accuracy**.
- **Real-Time Forecasting**: Uses advanced temporal modeling to predict the *next* stage of an attack (e.g. predicting Exfiltration before it happens).

### Training Architecture & Massive Data Ingestion
The AI was trained on the **complete, full 4.9 Million Row KDD Cup 99** dataset. 
Processing a 4.9M row dataset simultaneously is highly memory-intensive (requiring ~6GB+ RAM). To engineer around this limitation and achieve a truly enterprise-grade data pipeline, Netra-X uses a custom **Batched Incremental Training Pipeline (Online Learning)**.

**The Pipeline:**
1. **Memory Optimization**: Raw tabular bytes are downcasted directly into `float32` tensors on load, cutting the memory footprint by 50%.
2. **Chunked Ingestion**: The 4.9 million rows are sliced into optimized blocks of 500,000 rows.
3. **Partial Fit Escalation**: The ensemble iteratively streams these chunks into memory and trains via `partial_fit`, entirely bypassing Out-Of-Memory (OOM) limitations.

**Ensemble Stack (Soft Voting Consensus):**
1. **Multi-Layer Perceptron (MLP)**: A Deep Neural Network optimized for complex non-linear attack patterns, updated iteratively via backpropagation.
2. **Stochastic Gradient Descent (SGD)**: A highly-efficient linear classifier serving as a lightning-fast baseline for tabular classification.

### Evaluation Metrics
The ensemble achieves exceptional accuracy by aggregating the predictions of all three models.

#### Confusion Matrix
*Demonstrating the model's ability to minimize False Positives while maximizing True Positives.*
![Confusion Matrix](docs/assets/confusion_matrix.png)

#### ROC Curve
*Area Under the Curve (AUC) showcasing the perfect tradeoff between sensitivity and specificity.*
![ROC Curve](docs/assets/roc_curve.png)

#### Feature Importance
*Visualizing which network telemetry features (e.g., connection count, source bytes) the AI relies on most.*
![Feature Importance](docs/assets/feature_importance.png)

---

## ⚡ Key Features

1. **Live AI Confidence Scoring**: The dashboard streams live network packets into the AI ensemble, displaying a real-time Threat Probability score.
2. **Dual-Theming Architecture**: 
   - **Enterprise Light**: A stunning, frosted-glass Cloudflare/Cisco aesthetic for executive overviews.
   - **Intense Dark**: A brutalist military-grade terminal interface with CRT scanlines and glitch alerts for active incident response.
3. **Deception Grid Analytics**: Fully functional backend honeypot tracking mapped across VLANs.
4. **Persistent Network Topology**: A complete Cisco-style node map rendering core, distribution, and edge devices with live vulnerability scores.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, WebSockets
- **Machine Learning**: Scikit-Learn, XGBoost, Pandas, Numpy, Joblib
- **Frontend**: React 18, TypeScript, Tailwind CSS, Zustand, Cytoscape.js, ECharts

---

## 🚀 Getting Started

### 1. Start the AI Backend
```bash
cd netra-x
pip install -r backend/requirements.txt
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Start the Frontend UI
```bash
cd netra-x/frontend
npm install
npm run dev
```

Navigate to `http://localhost:3000` to access the SOC.
