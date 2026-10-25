# ForgeMind Implementation Plan & Checklist

Based on the [ForgeMind Design and Build Specification](../ForgeMind_Design.md).

## Phase 0: Repository Inspection and Plan
- [x] Inspect repository, current dependencies, and existing implementation (clean directory with `ForgeMind_Design.md`).
- [x] Identify environment capabilities (Python 3.10, Node v24, npm 11).
- [x] Create initial documentation (`docs/IMPLEMENTATION_PLAN.md`, `docs/ARCHITECTURE.md`).
- [x] Align on core architecture and local zero-cost/deterministic fallback requirements.

## Phase 1: Foundation and Persistence
- [x] Set up backend directory structure (`backend/pyproject.toml`, `backend/requirements.txt`, `.env.example`, `app/main.py`).
- [x] Implement database models (`assets`, `asset_edges`, `telemetry_readings`, `incidents`, `documents`, `investigations`, `recommendations`, `simulations`) with SQLite / PostgreSQL support (support zero-friction local SQLite fallback while keeping PostgreSQL + psycopg compatible).
- [x] Set up database schema initialization and session management (`app/infrastructure/db/session.py`).
- [x] Add FastAPI application with `/api/v1/health` and structured error handling.
- [x] Add `docker-compose.yml` for PostgreSQL and Qdrant.
- [x] Add deterministic demo factory seed script (`app/seed/demo_factory.py`, `scripts/seed_demo.py`).
- [x] Test migration, seed idempotency, and verify `/api/v1/assets` and `/api/v1/health`.

## Phase 2: Graph and Telemetry
- [x] Implement asset graph query and neighborhood traversal (`GET /api/v1/factory/graph`, `GET /api/v1/assets/{id}/neighbors`).
- [x] Add telemetry schema, seeded sensor patterns (normal, vibration spike, temperature drift), and summary endpoints (`GET /api/v1/assets/{id}/telemetry`).
- [x] Implement deterministic anomaly detection rule and demo incident trigger endpoint (`POST /api/v1/incidents/demo-trigger`).
- [x] Unit & integration tests for graph traversal and telemetry aggregation.

## Phase 3: ML Baseline and Graph Neural Network (PyTorch Geometric)
- [x] Implement graph feature construction (`ml/features.py`, `ml/graph_builder.py`).
- [x] Implement transparent statistical/heuristic baseline predictor (`ml/models/baseline.py`).
- [x] Implement spectral GNN model (2-layer Kipf-Welling GCN) with reproducible training & evaluation script on synthetic factory data (`ml/models/gnn.py`, `ml/evaluation.py`).
- [x] Implement inference interface with clear fallbacks.
- [x] Implement uncertainty/reliability quantification (Brier calibration score, Split-Conformal prediction intervals, and transparent heuristic dispersion `ml/uncertainty.py`).
- [x] Create `docs/MODEL_CARD.md`.

## Phase 4: Maintenance RAG with Qdrant
- [x] Author original demo equipment maintenance manuals (motor, pump, conveyor, CNC in `app/seed/demo_documents/`).
- [x] Implement document chunking with metadata (title, section, asset type, chunk ID in `app/rag/chunking.py`).
- [x] Implement embedding pipeline (local Sentence-Transformers / fast local dense projection fallback) and Qdrant vector store adapter with in-memory / local Qdrant support (`app/infrastructure/qdrant/client.py`, `app/infrastructure/embeddings/embedder.py`).
- [x] Implement retrieval service with source citations (`app/rag/retrieval.py`).
- [x] Tests for retrieval citations, empty search handling, and reindexing idempotency (`tests/unit/test_rag.py`).

## Phase 5: Digital Twin Simulation & Action Recommender
- [x] Implement deterministic digital twin simulator (`simulation/engine.py`) with baseline vs scenario comparison.
- [x] Implement candidate maintenance action catalog (`inspect`, `derate`, `repair`, `replace`, `monitor`).
- [x] Implement weighted, transparent action ranker factoring risk reduction, downtime, direct cost, and uncertainty penalty (`app/domain/recommendations/ranker.py`).
- [x] Unit tests for dependency failure propagation, cost/downtime formulas, and ranking logic (`tests/unit/test_simulation.py`, `tests/unit/test_recommendations.py`).

## Phase 6: LangGraph Investigation Workflow
- [x] Define typed LangGraph state (`InvestigationState` in `app/agents/state.py`).
- [x] Implement bounded workflow nodes (`collect_asset_context`, `summarize_telemetry`, `estimate_risk`, `retrieve_maintenance_evidence`, `generate_hypotheses`, `rank_actions`, `validate_output` in `app/agents/nodes.py`).
- [x] Wire deterministic template fallback (zero external paid API dependency in `app/agents/graph.py`).
- [x] Expose endpoint `POST /api/v1/incidents/{incident_id}/investigations` with structured audit trail and evidence citations.
- [x] Integration tests verifying deterministic investigation execution (`tests/integration/test_api_endpoints.py`).

## Phase 7: React Dashboard
- [x] Scaffold Vite + React + TypeScript application with ultra-premium industrial dark theme (`frontend/`).
- [x] Build typed API client for ForgeMind backend (`frontend/src/api/client.ts`).
- [x] Implement Navigation & Overview dashboard (factory health, incidents, quick stats in `OverviewView.tsx`).
- [x] Implement Interactive Factory Topology Graph (2D node-edge visualizer with status filters in `FactoryGraphView.tsx`).
- [x] Implement Asset Detail view (telemetry charts, graph neighbors, active alerts in `AssetDetailModal.tsx`).
- [x] Implement Incident Investigation view (symptoms, hypotheses, evidence cards with citations, action comparisons, audit trail in `IncidentInvestigationView.tsx`).
- [x] Implement Digital Twin Lab (scenario builder, baseline vs intervention comparison metrics in `DigitalTwinLabView.tsx`).
- [x] Implement Evidence Browser (`EvidenceView.tsx`) & Model Evaluation view (`ModelEvaluationView.tsx`).

## Phase 8: Integration, End-to-End Acceptance & Documentation
- [x] Run full test suite: 15 backend tests passed (`pytest`).
- [x] Run frontend build check: Vite production build passed in 9.74s.
- [x] Run End-to-End Acceptance Scenario (seeded motor incident → investigate → retrieve doc citations → risk/uncertainty → action ranker → digital twin simulation).
- [x] Complete documentation: `README.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/MODEL_CARD.md`, `docs/DATA_AND_SIMULATION.md`.
- [x] Verify local run instructions and zero-paid-API reproducible experience.
