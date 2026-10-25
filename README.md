# ForgeMind: Agentic Industrial Intelligence & Digital Twin

[![Tests](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI%20%7C%20SQLAlchemy%20%7C%20Qdrant-blue.svg)]()
[![Frontend](https://img.shields.io/badge/frontend-React%20%7C%20TypeScript%20%7C%20Vite-cyan.svg)]()
[![Mode](https://img.shields.io/badge/mode-Zero--Paid--API%20%7C%20Deterministic-purple.svg)]()

ForgeMind is a factory operations investigation workbench and digital twin simulator built for local, reproducible, and verifiable industrial intelligence. It models factory assets and operational dependencies, detects anomalous sensor telemetry, orchestrates investigations using a bounded LangGraph agent workflow, retrieves evidence from technical maintenance manuals in Qdrant, calculates split-conformal uncertainty intervals, and evaluates maintenance interventions in a discrete-event digital twin.

---

## 1. Key Capabilities

1. **Factory Asset Topology & Graph Intelligence:**
   - Interactive 2D visualizer representing operational dependencies (`feeds`, `drives`, `cools`).
   - Node-level feature extraction with tabular Logistic Regression baseline and spectral Graph Convolutional Network (GCN).
2. **Telemetry & Anomaly Stream:**
   - Multi-sensor tracking (vibration, temperature, power draw, flow rate, pressure, spindle RPM).
   - Seeded synthetic drift and threshold alerts (ISO 10816-3 Class II criteria).
3. **Agentic Investigation Workflow (LangGraph):**
   - 8-stage bounded pipeline with typed state: validates incident, aggregates sensor statistics, calculates risk & uncertainty, retrieves Qdrant SOP chunks, synthesizes diagnostic hypotheses with source citations, and ranks candidate actions.
   - 100% deterministic local fallback without paid external LLM dependencies.
4. **Maintenance RAG with Qdrant:**
   - Original technical documentation corpus for electric induction motors, coolant pumps, conveyors, and CNC machining cells.
   - Dense vector embeddings with payload metadata and citation guarantees.
5. **Split-Conformal Uncertainty Quantification:**
   - Empirical coverage guarantees at nominal 90% confidence target ($\hat{q}$ nonconformity quantile).
   - Distinguishes raw anomaly scores from calibrated probabilities and transparent reliability classifications (`high`, `medium`, `low`, `insufficient_evidence`).
6. **Discrete-Event Digital Twin Simulator:**
   - Simulates intervention scenarios (`outage`, `derating`, `inspection`, `repair`).
   - Downstream cascade propagation along critical manufacturing paths.
   - Side-by-side comparison of baseline throughput vs intervention, lost production hours, and downtime costs.

---

## 2. Quickstart & Local Setup

ForgeMind requires **Python 3.10+** and **Node.js 18+**. It runs completely standalone out-of-the-box using local SQLite and embedded in-memory Qdrant. Docker Compose is optionally provided for containerized PostgreSQL and Qdrant.

### Step 1: Clone and Configure Environment
```bash
# Clone the repository
git clone https://github.com/your-username/forgemind.git
cd forgemind

# Copy environment template
cp .env.example .env
```

### Step 2: Set Up Backend
```bash
# Create and activate Python virtual environment
py -3.10 -m venv backend/.venv

# Windows:
backend\.venv\Scripts\activate
# Linux/macOS:
source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database schema and seed demo factory
python scripts/seed_demo.py

# Ingest technical maintenance manuals into Qdrant
python scripts/ingest_documents.py
```

### Step 3: Start FastAPI Backend Server
```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
Backend API will be live at `http://localhost:8000` (API docs at `http://localhost:8000/docs`).

### Step 4: Set Up and Run React Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 3. End-to-End Demo Walkthrough

1. **Open the Dashboard (`http://localhost:5173`):**
   - View the overall factory health (85.7% availability, 1 active incident on Drive Motor M-101).
   - Observe the live vibration (5.82 mm/s > 4.5 mm/s warning threshold) and temperature (86.5°C) gauges.
2. **Inspect Factory Topology (`Asset Topology` tab):**
   - View the 2D layout: Feeder $\to$ Conveyor $\to$ CNC $\to$ Inspection $\to$ Packaging.
   - Click on **Drive Motor M-101** to inspect its 24-hour telemetry sparklines and upstream/downstream connections.
3. **Execute Incident Investigation (`Incident Workbench` tab):**
   - Inspect the active incident: *Elevated Vibration & Thermal Runaway Pattern on Drive Motor M-101*.
   - Click **Re-run Agent Investigation** to observe the LangGraph pipeline:
     - Model Risk Score: ~72% (Conformal interval: [60% — 85%]).
     - Primary Hypothesis: *Incipient Drive-End Bearing Spalling (SKF 6312)*.
     - Citations: Points directly to `chk_...` from `SOP-M101: Electric Induction Motor Diagnostics`.
     - Ranked Candidate Actions: #1 Acoustic Inspection, #2 Production Load Derating, #3 Bearing Overhaul.
4. **Evaluate Intervention in Digital Twin (`Digital Twin Lab` tab):**
   - Select **Drive Motor M-101**, choose **Production Derating** at 50% capacity for 60 minutes.
   - Click **Simulate Intervention**:
     - Projected Throughput: 160 units/hr (vs 300 nominal).
     - Downstream Cascade: Main Infeed Conveyor C-101 $\to$ Precision CNC Station CNC-301.
     - Financial Impact: Net loss compared to catastrophic uncommanded outage.
5. **Inspect Model Metrics (`Model & Evaluation` tab):**
   - Review AUROC (0.963), Accuracy (0.952), Brier Calibration (0.048), and Split-Conformal coverage (81.0% empirical on test split).

---

## 4. Test Suite & Verification Results

All tests have been run and verified locally:

```bash
# Run backend pytest suite
cd backend
.venv\Scripts\pytest -v
```

### Verified Test Run Summary (15 Passed, 0 Failed):
- `tests/integration/test_api_endpoints.py::test_health_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_overview_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_factory_graph_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_asset_telemetry_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_simulation_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_recommendations_rank_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_model_evaluation_endpoint` **PASSED**
- `tests/integration/test_api_endpoints.py::test_end_to_end_investigation_workflow` **PASSED**
- `tests/unit/test_rag.py::test_rag_retrieval_returns_relevant_chunks` **PASSED**
- `tests/unit/test_rag.py::test_rag_retrieval_empty_query` **PASSED**
- `tests/unit/test_recommendations.py::test_ranking_sorts_highest_score_first` **PASSED**
- `tests/unit/test_recommendations.py::test_custom_weights_change_preference` **PASSED**
- `tests/unit/test_simulation.py::test_simulation_baseline_throughput` **PASSED**
- `tests/unit/test_simulation.py::test_simulation_motor_outage_propagation` **PASSED**
- `tests/unit/test_simulation.py::test_simulation_motor_derating` **PASSED**

### Frontend Build Verification:
```bash
cd frontend
npm run build
```
- **Result:** TypeScript check and Vite production bundle generated successfully in 9.74s (`dist/index.html`, `dist/assets/index-DdvGaxcI.css`, `dist/assets/index-DVHR12GF.js`).

---

## 5. Architectural Notes & Known Limitations

1. **Advisory Decision Support:** ForgeMind is an operations investigation and decision-support prototype. It does not interface with physical PLCs, SCADA networks, or emergency safety circuits.
2. **Synthetic Data Limitations:** Telemetry streams and anomaly labels are generated deterministically to demonstrate pipeline mechanics. They are not calibrated against physical factory telemetry.
3. **Zero-Paid-API Fallback:** RAG embeddings utilize local Sentence-Transformers or a deterministic unit-sphere dense hash projection when offline; the LangGraph agent utilizes structured template synthesis when no external LLM is configured.
