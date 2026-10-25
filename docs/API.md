# ForgeMind REST API Specification

**Prefix:** `/api/v1`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc` (ReDoc)

---

## 1. System Health & Overview

### `GET /health` or `GET /api/v1/health`
Checks application liveness and dependency connectivity.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "app": "ForgeMind",
  "environment": "development",
  "dependencies": {
    "database": "ok",
    "qdrant_vector_store": "ok"
  }
}
```

### `GET /api/v1/overview`
Provides high-level factory health, active incidents, telemetry highlights, and recent simulations.
- **Response `200 OK`**:
```json
{
  "factory_health": {
    "overall_status": "alert",
    "total_assets": 7,
    "operational_count": 6,
    "degraded_count": 1,
    "offline_count": 0,
    "availability_pct": 85.7
  },
  "active_incidents_count": 1,
  "active_incidents": [...],
  "key_asset_telemetry": {
    "vibration": { "value": 5.82, "unit": "mm/s", "observed_at": "..." },
    "temperature": { "value": 86.5, "unit": "deg_C", "observed_at": "..." }
  },
  "recent_simulations": [...]
}
```

---

## 2. Asset Topology & Telemetry

### `GET /api/v1/assets`
Returns list of all registered factory assets.
- **Query Parameters:** `asset_type` (optional), `status` (optional)

### `GET /api/v1/assets/{asset_id}`
Returns metadata, location, criticality, and specifications for a single asset.

### `GET /api/v1/assets/{asset_id}/neighbors`
Returns upstream and downstream connected assets and edge relationship types (`feeds`, `drives`, `cools`).

### `GET /api/v1/assets/{asset_id}/telemetry`
Returns timestamped sensor telemetry readings and statistical summaries (min, max, mean, std, anomaly flags).
- **Query Parameters:** `hours` (default 24)

### `GET /api/v1/factory/graph`
Returns full 2D topology representation with nodes, directed edges, criticality scores, and active incident associations.

---

## 3. Incident Management & Agentic Investigation

### `GET /api/v1/incidents`
Lists all factory operational incidents. Filter by `status` or `asset_id`.

### `POST /api/v1/incidents/demo-trigger`
Simulates an abrupt vibration spike and thermal runaway incident on Drive Motor M-101.
- **Request Body:**
```json
{
  "asset_id": "11111111-1111-1111-1111-111111111102",
  "scenario": "bearing_wear_overheating",
  "severity": "high"
}
```

### `POST /api/v1/incidents/{incident_id}/investigations`
Executes the bounded LangGraph agent workflow: collects context, summarizes telemetry, computes GNN risk & conformal intervals, retrieves Qdrant SOP chunks, synthesizes hypotheses, and ranks candidate actions.
- **Response `201 Created`**: Returns `StructuredInvestigation`.

---

## 4. Digital Twin Simulation & Recommendations

### `POST /api/v1/simulations`
Executes a deterministic what-if scenario.
- **Request Body:**
```json
{
  "target_asset_id": "11111111-1111-1111-1111-111111111102",
  "scenario_type": "derating",
  "duration_minutes": 60,
  "derating_factor": 0.5,
  "persist_result": true
}
```
- **Response `201 Created`**: Returns baseline vs intervention comparison, throughput delta, downtime hours, and downstream cascade path.

### `POST /api/v1/recommendations/rank`
Ranks candidate maintenance interventions using multi-factor decision analysis.
- **Formula:**
$$\text{Score} = w_{\text{risk}} \cdot \Delta R - w_{\text{downtime}} \cdot D - w_{\text{cost}} \cdot C - w_{\text{unc}} \cdot U$$

---

## 5. Maintenance RAG & ML Model Evaluation

### `GET /api/v1/documents`
Lists all ingested technical manuals and procedures.

### `POST /api/v1/documents/ingest-demo`
Idempotently chunks and embeds maintenance documents into Qdrant.

### `GET /api/v1/model/evaluation`
Returns model card metrics: AUROC, F1, Accuracy, Brier Calibration score, and Conformal Prediction intervals.
