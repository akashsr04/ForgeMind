# ForgeMind Architecture Overview

## 1. System Vision & Objective
ForgeMind is an agentic industrial intelligence platform and digital twin operations workbench designed to run completely locally without paid APIs or external services.

It integrates:
1. **Asset Topology & Graph Intelligence**: Graph representation of industrial assets and dependencies with Graph Neural Network (PyG) and transparent heuristic baselines.
2. **Telemetry & Anomaly Stream**: Real-time and seeded sensor telemetry (vibration, temperature, power, pressure, throughput) with statistical drift and spike detection.
3. **Agentic Investigation (LangGraph)**: Bounded, multi-step investigation workflow with typed state, read-only tools, deterministic hypothesis generation, and evidence citations.
4. **Maintenance RAG (Qdrant & Local Embeddings)**: Equipment maintenance procedures and manuals embedded and stored in Qdrant (supporting both embedded/in-memory mode and client-server mode).
5. **Digital Twin Simulation & Action Recommender**: Discrete event/time-step simulation for intervention testing (derating, outage, repair, inspection) with dependency propagation and multi-factor action ranking.
6. **Unified Operations Dashboard (React + TypeScript)**: Interactive 2D factory topology, incident investigation workbench, digital twin lab, and telemetry timeline charts.

---

## 2. High-Level Architecture Diagram

```
+------------------------------------------------------------------------+
|                      React + TypeScript Dashboard                      |
|  (Topology View, Incident Investigation, Digital Twin Lab, Evidence)  |
+-----------------------------------+------------------------------------+
                                    | REST / JSON (HTTP)
                                    v
+------------------------------------------------------------------------+
|                     FastAPI Application (Modular)                      |
|                                                                        |
|  [API Routes]                                                          |
|   /health, /overview, /assets, /factory/graph, /incidents,             |
|   /investigations, /simulations, /recommendations/rank, /documents     |
|                                                                        |
|  [LangGraph Agent Layer]                                               |
|   Incident Parser -> Context Collector -> Telemetry Summarizer ->     |
|   Risk Estimator -> RAG Retriever -> Hypothesis Engine ->              |
|   Action Ranker -> Output Validator                                    |
|                                                                        |
|  [Domain & Intelligence Services]                                      |
|   - Digital Twin Engine: State snapshot, dependency propagation        |
|   - Action Recommender: Weighted scoring, cost & downtime trade-offs   |
|   - ML Engine: Graph builder, baseline heuristic, PyG GNN,             |
|     uncertainty & reliability estimator                                |
|   - RAG Engine: Document chunker, embedding adapter, Qdrant store      |
+-------------------+--------------------------------+-------------------+
                    |                                |
                    v                                v
+------------------------------------+  +--------------------------------+
|       PostgreSQL / SQLite DB       |  |      Qdrant Vector Engine      |
| (Assets, Edges, Telemetry,         |  | (Local in-process / HTTP)      |
|  Incidents, Investigations,        |  | (Chunk vectors & metadata)     |
|  Simulations, Recommendations)     |  |                                |
+------------------------------------+  +--------------------------------+
```

---

## 3. Technology Stack & Key Choices

- **Language & Runtime**: Python 3.10+ (Backend), Node v24+ / Vite (Frontend)
- **Web Framework**: FastAPI, Pydantic v2, Uvicorn
- **Database / ORM**: SQLAlchemy 2.0 + Alembic (PostgreSQL with automatic local SQLite fallback for instant zero-dependency execution)
- **Vector Search**: Qdrant (`qdrant-client` supporting local disk / memory mode when Docker is absent, or remote Qdrant service)
- **Graph & ML**: NetworkX for topology algorithms; PyTorch & PyTorch Geometric for GNN modeling; Scikit-learn for baselines and calibration metrics
- **Workflow Orchestration**: LangGraph with typed state and deterministic fallback
- **Frontend**: React 18 / 19, TypeScript, Vite, Lucide icons, Canvas/SVG graph rendering, Recharts

---

## 4. Bounded Agent Safety & Reliability Guarantees
- **No Direct Actuation**: ForgeMind produces advisory recommendations only.
- **Read-Only Tools**: Agent nodes cannot alter factory assets or physical states.
- **Deterministic Fallback**: If an external LLM is not configured, a rule/template-based deterministic engine generates structured investigations and hypotheses without hallucination.
- **Ground Truth Citations**: Hypotheses only cite chunks retrieved by the Qdrant retrieval tool.
