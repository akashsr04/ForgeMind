# ForgeMind --- Agentic Industrial Intelligence & Digital Twin

## Implementation Design and Build Specification for Antigravity

**Document type:** Product requirements + technical design + phased
implementation plan\
**Project name:** ForgeMind\
**Primary stack:** Python, FastAPI, PyTorch Geometric, LangGraph,
Qdrant, PostgreSQL, React\
**Project goal:** Build a locally runnable, demonstrable industrial
intelligence platform that models a factory's assets and dependencies,
detects anomalous machine behavior, investigates possible causes using
tool-using AI agents, retrieves evidence from technical documents,
estimates uncertainty, and tests maintenance actions in a simulated
digital twin.

------------------------------------------------------------------------

## 1. Instructions to the Coding Agent

Treat this document as the source of truth for product scope and
architecture.

1.  Inspect the existing repository before editing. Preserve working
    code and conventions where practical.
2.  Produce a short implementation plan and a task checklist before
    major changes. Keep the checklist updated as work is completed.
3.  Implement in small, runnable increments. After each phase, run
    relevant tests and report exact commands and outcomes.
4.  Prefer clear, typed, modular code over a monolithic implementation.
    Use dependency injection where it improves testability.
5.  Do not implement fake AI behavior disguised as real model output.
    Clearly label deterministic heuristics, synthetic data, mock
    integrations, and real model inference.
6.  The application must work without paid APIs or externally hosted
    LLMs. The core platform, demo data, graph model, retrieval,
    simulation, and dashboard must run locally. LLM integration must be
    optional and have a deterministic fallback.
7.  Do not add credentials, API keys, or real secrets to source control.
    Provide `.env.example`.
8.  Do not use destructive database resets or delete existing project
    files without explicit approval.
9.  Do not add features outside the defined scope until the MVP passes
    its acceptance criteria.
10. Avoid overengineering: no Kubernetes, microservices split, message
    broker, or elaborate enterprise framework for the MVP.
11. Document assumptions and any dependency/version choices. Pin or
    constrain dependencies in the appropriate manifest.
12. If a required capability is unavailable, implement a transparent
    minimal fallback and document the limitation instead of claiming
    full functionality.

### Required delivery behavior

-   First inspect the repository and summarize its current state.
-   Create/update `docs/IMPLEMENTATION_PLAN.md` with ordered phases and
    checkboxes.
-   Implement the MVP in phases.
-   Add automated tests as features are built.
-   Finish with setup instructions, demo instructions, architecture
    notes, known limitations, and a list of tests actually run.
-   Do not claim a test passed unless it was run and its result was
    observed.

------------------------------------------------------------------------

## 2. Product Vision

ForgeMind is a factory operations investigation workbench. It represents
a small simulated factory as a digital twin: machines, components,
production stations, sensors, and dependency relationships have a
current virtual state. When a machine shows suspicious readings, the
system creates an incident and helps an operator investigate it.

Example scenario:

> A motor's vibration has increased and its temperature is trending
> upward. ForgeMind identifies connected assets that could be affected,
> retrieves relevant maintenance instructions, estimates the likelihood
> and uncertainty of a fault, and compares candidate actions. The
> operator can simulate an inspection, derating the machine, or
> scheduling a repair and compare expected downtime and production
> impact before choosing an action.

ForgeMind is a **decision-support prototype**, not a certified
industrial safety system. It must not autonomously issue real
machine-control commands. Recommendations and simulations are advisory
and clearly labeled.

### Target users

-   Maintenance technician investigating a machine alert.
-   Factory operations engineer assessing potential production impact.
-   Engineering student or recruiter exploring graph ML, agentic
    workflows, retrieval, uncertainty, and simulation in one integrated
    application.

### Core value proposition

Connect machine telemetry, asset relationships, technical documentation,
predictive models, and what-if simulation in a traceable workflow. Every
generated recommendation should expose its supporting evidence,
assumptions, uncertainty, and simulated impact.

------------------------------------------------------------------------

## 3. MVP Scope

### Must have

1.  Seeded, reproducible demo factory with assets, dependency edges,
    sensor readings, maintenance history, and sample technical
    documents.
2.  React dashboard showing factory status, asset graph, active
    incidents, asset detail, and simulation comparisons.
3.  FastAPI REST API with validation and OpenAPI documentation.
4.  PostgreSQL persistence for assets, graph edges, telemetry,
    incidents, documents metadata, investigation runs, recommendations,
    and simulations.
5.  PyTorch Geometric model component that operates on a graph of
    factory assets and produces a documented anomaly/risk score or
    node-level prediction. Include a simple baseline for comparison.
6.  Uncertainty-aware output that distinguishes model score from
    calibrated probability. Include a practical uncertainty method and
    explicit limitations.
7.  Qdrant-based retrieval over seeded maintenance documents, with
    citations/metadata in retrieved evidence.
8.  LangGraph investigation workflow with explicit typed state and
    bounded tools.
9.  Deterministic digital-twin simulator for what-if scenarios,
    including machine derating, asset outage, and repair/inspection
    actions.
10. Recommendation ranking that compares candidate actions using
    expected risk reduction, downtime, cost, and confidence/uncertainty.
11. Tests, seed scripts, Docker Compose for local dependencies,
    `.env.example`, and complete README.
12. A no-paid-API demo path.

### Explicitly out of scope for MVP

-   Connecting to real industrial controllers, PLCs, SCADA, or OT
    networks.
-   Autonomous actuation or sending commands to physical machines.
-   Production-grade fault diagnosis for any real factory.
-   Training on confidential company data.
-   Multi-tenant enterprise IAM, billing, Kubernetes, or distributed
    event streaming.
-   Claiming that synthetic demo data demonstrates real-world predictive
    accuracy.
-   A fully photorealistic 3D factory. A clear interactive 2D topology
    and scenario dashboard are sufficient.

------------------------------------------------------------------------

## 4. Main User Journeys

### Journey A --- Investigate an incident

1.  User opens dashboard and sees factory health and active incidents.
2.  User opens an incident generated from a telemetry anomaly or seeded
    demo event.
3.  User sees affected asset, recent sensor values, graph neighbors, and
    model output.
4.  User clicks **Investigate**.
5.  LangGraph workflow gathers telemetry summaries, graph context, model
    risk, and relevant Qdrant documents.
6.  The UI displays a structured investigation: hypotheses, evidence
    citations, uncertainty, missing information, and candidate next
    actions.
7.  User can inspect the evidence and rerun investigation after changing
    the incident context.

### Journey B --- Run a what-if simulation

1.  User opens a machine or incident and chooses a scenario: outage,
    derating, inspection, or repair.
2.  User configures scenario parameters, such as duration or severity.
3.  The simulator evaluates downstream dependencies, production
    capacity, expected downtime, and estimated cost using documented
    assumptions.
4.  UI compares baseline and scenario side by side.
5.  User can save the simulation and compare alternative actions.

### Journey C --- Inspect the factory graph

1.  User opens the factory topology view.
2.  Nodes represent assets; edges represent dependency, power, material
    flow, or production relationships.
3.  User filters by asset type, status, and incident association.
4.  Selecting a node opens asset details, connected neighbors,
    telemetry, incidents, and recommendations.

------------------------------------------------------------------------

## 5. Functional Requirements

### FR-1: Factory and asset registry

-   Store assets with `id`, `name`, `asset_type`, `location`,
    `criticality`, `status`, `metadata`, `created_at`, and `updated_at`.
-   Store directed or undirected relationships with `source_asset_id`,
    `target_asset_id`, `relationship_type`, `weight`, and metadata.
-   Validate that both endpoints exist and prevent duplicate
    relationships where applicable.
-   Seed a small factory, for example: raw material feeder, conveyor,
    motor, pump, CNC station, packaging line, and inspection station.
-   Keep all demo assets and values clearly marked as synthetic.

### FR-2: Telemetry and anomalies

-   Store timestamped sensor readings with asset, sensor name, numeric
    value, unit, and source.
-   Provide endpoints for time-window summaries and latest readings.
-   Include seeded sensor patterns for normal operation, drift,
    vibration increase, and overheating.
-   Anomaly detection must be reproducible. Start with transparent
    statistical thresholds or a baseline model; do not pretend synthetic
    labels are real field data.
-   Allow a demo incident to be triggered without needing live sensor
    ingestion.

### FR-3: Graph intelligence

-   Build a graph representation from persisted assets and
    relationships.
-   Use NetworkX or a simple adjacency traversal for graph utilities if
    helpful, but use PyTorch Geometric for the ML graph
    representation/model.
-   Define node features explicitly, e.g. asset-type encoding,
    criticality, normalized recent telemetry summaries, anomaly
    indicators, and missingness indicators.
-   Define edge types/attributes and explain any simplification used by
    the first model.
-   Include a reproducible train/evaluate or inference path with fixed
    seeds.
-   Provide a baseline such as logistic regression, random forest, or
    threshold scoring and report comparable metrics where labels exist.
-   Do not report metrics on training data as generalization
    performance.
-   If data is synthetic, clearly state that the model demonstrates
    pipeline mechanics, not validated industrial performance.

### FR-4: Uncertainty and confidence-aware behavior

-   API outputs must separate:
    -   `risk_score`: a model score on a documented scale.
    -   `estimated_probability`: present only if a defensible
        probability model and calibration process exist.
    -   `uncertainty`: a defined interval, dispersion estimate, or
        conformal prediction set.
    -   `confidence_level` or `reliability_status`: a human-readable
        status derived by documented rules.
-   Do not label a raw sigmoid/softmax output as calibrated confidence.
-   Use a validation split for calibration/uncertainty evaluation. For a
    classification model, consider calibration curves and Brier score;
    for regression, consider conformal prediction intervals and
    empirical coverage.
-   If sample count or data quality is inadequate, return
    `insufficient_evidence` or `low_reliability` rather than
    manufacturing certainty.
-   Show a short explanation of why confidence is low, such as missing
    sensor history, out-of-distribution feature values, sparse graph
    neighbors, or weak evidence.
-   Recommendations must be conservative when uncertainty is high.

### FR-5: Document ingestion and RAG

-   Seed a small, original demo corpus of maintenance procedures and
    equipment manuals written for the prototype. Do not scrape
    copyrighted manuals without permission.
-   Chunk documents with stable IDs and preserve metadata: title,
    section, asset type, document type, source, and chunk ID.
-   Embed using a local embedding model where practical; make the
    embedding model configurable. Do not require a paid embedding API.
-   Store vectors and payload metadata in Qdrant.
-   Search by incident, asset type, symptoms, and query text. Return
    source titles and chunk/section references.
-   The LLM must not invent citations. Only cite retrieved chunks
    actually returned by the retrieval tool.
-   If retrieval returns no useful evidence, say that no relevant
    document was found.
-   Provide an ingestion/reindex command and idempotent seed behavior.

### FR-6: Agentic investigation using LangGraph

Implement a bounded graph workflow with explicit typed state. Suggested
nodes: 1. `parse_request`: validate incident and requested
investigation. 2. `collect_asset_context`: fetch asset metadata and
graph neighborhood. 3. `summarize_telemetry`: obtain recent readings and
anomaly summaries. 4. `estimate_risk`: call the prediction/uncertainty
service. 5. `retrieve_maintenance_evidence`: query Qdrant. 6.
`generate_hypotheses`: produce candidate causes with evidence
references; if no LLM is configured, use a deterministic template-based
fallback. 7. `rank_actions`: evaluate approved candidate actions against
rules and simulation outputs. 8. `validate_output`: ensure output
schema, source references, uncertainty fields, and safety disclaimer are
present. 9. `END`: return structured investigation.

Requirements: - Use LangGraph for orchestration, not just a direct
sequence of unrelated LLM calls. - Define state with typed fields and
constrain node inputs/outputs. - Use bounded retries and a maximum step
count. - Tools must be read-only except for explicitly requested
creation of an investigation or simulation record. - Never allow
model-generated free text to become a database query or executable
command. - Do not let an agent call arbitrary shell commands or access
the filesystem. - Validate IDs and parameters in tool functions. - Keep
deterministic fallback behavior for missing LLM configuration or model
failure. - Return an audit trail showing workflow steps and tool
outcomes without exposing secrets or internal chain-of-thought. -
Explain recommendations with evidence and concise rationale, not hidden
reasoning traces.

### FR-7: Hybrid maintenance-action recommender

The system recommends actions, not products or routes. Candidate actions
may include inspect, monitor, reduce load, schedule maintenance, or
replace a component. - Generate candidates from a controlled catalog and
asset type. - Score each action using documented factors: estimated risk
reduction, downtime, direct cost, production impact, evidence relevance,
and uncertainty. - Begin with a transparent weighted ranker. Keep
weights in configuration and expose score components. - If sufficient
interaction data is later available, add a learning-to-rank or
preference-based component. Do not fabricate collaborative-filtering
data for the MVP. - Support cold start using rule/content features. -
Show why each action ranks where it does and what assumptions affect the
score. - A recommendation is advisory and must not initiate physical
maintenance or machine control.

### FR-8: Digital twin simulation

-   Implement a deterministic, discrete-event or time-step simulator for
    the seeded factory.
-   Model asset states, dependency propagation, machine availability,
    throughput/capacity, downtime, and scenario duration at a level
    appropriate for a demonstrator.
-   Include scenarios:
    -   One asset unavailable.
    -   One asset operating at reduced capacity.
    -   Planned inspection or repair with duration/cost assumptions.
    -   A downstream dependency affected by an upstream failure.
-   Compare baseline with intervention.
-   Return outputs such as projected production throughput, affected
    assets, simulated downtime, estimated cost, and assumptions.
-   Clearly label outputs as simulated estimates, not real-world
    forecasts.
-   Keep simulation logic separate from API routes and agent code.
-   Include unit tests for deterministic behavior and dependency
    propagation.

### FR-9: React dashboard

Required pages/views: 1. **Overview:** factory status, active incidents,
asset availability, recent telemetry, and recent simulations. 2.
**Factory Graph:** interactive 2D graph with selectable nodes, edge
types, filters, and legend. 3. **Asset Detail:** metadata, telemetry
timeline, neighbors, incidents, and recommendations. 4. **Incident
Investigation:** hypotheses, evidence citations, risk/uncertainty
indicators, missing evidence, and action rankings. 5. **Digital Twin
Lab:** configure scenario, run simulation, and compare baseline vs
scenario. 6. **Documents / Evidence:** inspect seeded document chunks
and source metadata. 7. **Model & Evaluation:** show model version,
dataset type, evaluation metrics, calibration/coverage results when
available, and caveats. - Provide loading, empty, error, and
low-confidence states. - Use clear accessible labels, keyboard-friendly
controls, responsive layouts, and readable charts. - Do not use
confidence colors as the only way to communicate status; pair them with
labels/icons/text. - Keep UI styling consistent and professional. Avoid
excessive animation and unnecessary visual effects. - Do not show fake
real-time data as live data. Clearly label seeded or simulated
telemetry.

------------------------------------------------------------------------

## 6. Proposed Architecture

Use a modular monolith for the MVP. One FastAPI service contains domain
modules; PostgreSQL and Qdrant are separate local services. The React
app communicates through the REST API.

``` text
React + TypeScript Dashboard
          |
          | HTTP / JSON
          v
FastAPI Application
  |       |          |             |
  |       |          |             +--> LangGraph Investigation Workflow
  |       |          |                         |
  |       |          |                         +--> Telemetry / Asset Tools
  |       |          |                         +--> Graph ML / Risk Tools
  |       |          |                         +--> Qdrant Retrieval Tool
  |       |          |                         +--> Simulation / Ranking Tools
  |       |          |
  |       |          +--> Digital Twin Domain
  |       +--> PyTorch Geometric Model Service
  +--> PostgreSQL / SQLAlchemy
          |
          +--> Assets, edges, telemetry, incidents,
               documents metadata, investigations,
               recommendations, simulations

Qdrant <--- locally generated embeddings + document chunks
```

### Architectural boundaries

-   **API layer:** HTTP schemas, request validation, response
    formatting, dependency wiring.
-   **Domain layer:** asset rules, incident lifecycle, action catalog,
    ranking rules, simulation contracts.
-   **Application layer:** use cases such as investigate incident, run
    simulation, ingest documents.
-   **Infrastructure layer:** SQLAlchemy repositories, Qdrant adapter,
    embedding adapter, model loader, optional LLM adapter.
-   **ML layer:** feature construction, PyG model, training/evaluation
    scripts, inference, uncertainty/calibration utilities.
-   **Agent layer:** LangGraph state, nodes, tool adapters, output
    validation, audit events.
-   **Frontend:** typed API client, pages, graph visualization, charts,
    reusable components.

Avoid circular dependencies. Domain logic must not import FastAPI,
React, LangGraph, or database-specific classes.

------------------------------------------------------------------------

## 7. Repository Structure

Use this as the preferred structure; adapt only when the existing
repository has a sound convention.

``` text
forgemind/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── API.md
│   ├── MODEL_CARD.md
│   ├── DATA_AND_SIMULATION.md
│   └── ADR/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── errors.py
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   ├── schemas/
│   │   ├── domain/
│   │   │   ├── assets/
│   │   │   ├── incidents/
│   │   │   ├── recommendations/
│   │   │   └── simulation/
│   │   ├── application/
│   │   │   └── use_cases/
│   │   ├── infrastructure/
│   │   │   ├── db/
│   │   │   ├── qdrant/
│   │   │   ├── embeddings/
│   │   │   └── llm/
│   │   ├── ml/
│   │   │   ├── graph_builder.py
│   │   │   ├── features.py
│   │   │   ├── models/
│   │   │   ├── inference.py
│   │   │   ├── uncertainty.py
│   │   │   └── evaluation.py
│   │   ├── agents/
│   │   │   ├── state.py
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   ├── tools.py
│   │   │   └── output_validation.py
│   │   ├── rag/
│   │   │   ├── chunking.py
│   │   │   ├── ingestion.py
│   │   │   └── retrieval.py
│   │   ├── simulation/
│   │   │   ├── engine.py
│   │   │   ├── scenarios.py
│   │   │   └── metrics.py
│   │   └── seed/
│   │       ├── demo_factory.py
│   │       └── demo_documents/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── contract/
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── app/
│       ├── api/
│       ├── components/
│       ├── features/
│       │   ├── overview/
│       │   ├── factory-graph/
│       │   ├── assets/
│       │   ├── incidents/
│       │   ├── simulation/
│       │   ├── evidence/
│       │   └── evaluation/
│       ├── hooks/
│       ├── types/
│       └── main.tsx
└── scripts/
    ├── dev.sh
    └── seed_demo.py
```

------------------------------------------------------------------------

## 8. Data Model

Use PostgreSQL as the source of truth for structured application data.
Use Qdrant only for vector search and its associated payload metadata.
Avoid storing the only copy of important business state in Qdrant.

### Core tables

#### `assets`

-   `id`: UUID primary key
-   `name`: text, required
-   `asset_type`: text, required
-   `location`: text or JSON
-   `criticality`: numeric or bounded enum
-   `status`: enum/text (`operational`, `degraded`, `offline`,
    `maintenance`)
-   `metadata`: JSONB
-   timestamps

#### `asset_edges`

-   `id`: UUID primary key
-   `source_asset_id`, `target_asset_id`: foreign keys to assets
-   `relationship_type`: e.g. `feeds`, `drives`, `depends_on`,
    `located_near`
-   `weight`: numeric
-   `metadata`: JSONB
-   unique constraint appropriate to edge direction/type

#### `telemetry_readings`

-   `id`: UUID primary key
-   `asset_id`: foreign key
-   `sensor_name`, `value`, `unit`, `observed_at`, `source`
-   indexes on `(asset_id, observed_at)` and
    `(sensor_name, observed_at)`

#### `incidents`

-   `id`: UUID primary key
-   `asset_id`: foreign key
-   `title`, `description`, `severity`, `status`
-   `trigger_type`, `detected_at`, `resolved_at`
-   `context`: JSONB
-   `is_synthetic`: boolean

#### `documents`

-   `id`: UUID primary key
-   `title`, `document_type`, `asset_type`, `source_label`, `version`
-   `created_at`, `is_demo`

#### `investigations`

-   `id`: UUID primary key
-   `incident_id`: foreign key
-   `status`, `workflow_version`, `started_at`, `completed_at`
-   `summary`, `structured_result`: JSONB
-   `error_code` when applicable

#### `recommendations`

-   `id`: UUID primary key
-   `investigation_id`: foreign key
-   `action_type`, `title`, `rationale`
-   `score`, `score_components`: JSONB
-   `uncertainty_summary`, `evidence_refs`: JSONB
-   `is_advisory`: boolean, default true

#### `simulations`

-   `id`: UUID primary key
-   `incident_id`: optional foreign key
-   `scenario_type`, `parameters`: JSONB
-   `baseline_result`, `scenario_result`: JSONB
-   `assumptions`: JSONB
-   `created_at`, `is_synthetic`: boolean

Use Alembic migrations. Define indexes and foreign-key constraints.
Store timestamps in UTC. Avoid unvalidated free-form JSON where a typed
schema is appropriate.

------------------------------------------------------------------------

## 9. API Design

Use `/api/v1` prefix, Pydantic request/response schemas, consistent
error responses, and generated OpenAPI docs.

Suggested endpoints:

``` text
GET    /api/v1/health
GET    /api/v1/overview
GET    /api/v1/assets
GET    /api/v1/assets/{asset_id}
GET    /api/v1/assets/{asset_id}/neighbors
GET    /api/v1/assets/{asset_id}/telemetry
GET    /api/v1/factory/graph
GET    /api/v1/incidents
GET    /api/v1/incidents/{incident_id}
POST   /api/v1/incidents/demo-trigger
POST   /api/v1/incidents/{incident_id}/investigations
GET    /api/v1/investigations/{investigation_id}
GET    /api/v1/documents
POST   /api/v1/documents/ingest-demo
POST   /api/v1/simulations
GET    /api/v1/simulations/{simulation_id}
POST   /api/v1/recommendations/rank
GET    /api/v1/model/evaluation
```

### API behavior

-   `GET /health` should verify application liveness; optionally expose
    dependency readiness separately.
-   Use pagination for list endpoints where needed.
-   Return 404 for unknown resources, 422 for invalid request payloads,
    and safe 500 errors without leaking stack traces.
-   Use typed response schemas for graph nodes/edges, incidents,
    investigation output, uncertainty summaries, and simulation results.
-   Investigation creation should return an ID and status; synchronous
    execution is acceptable for the initial small demo if documented. Do
    not introduce a task queue unless actual requirements justify it.
-   Include request IDs in logs and safe error responses.
-   Add CORS configuration through environment variables for local
    frontend development.
-   No authentication is required for the local single-user MVP, but
    structure dependencies so auth can be added later. Do not expose it
    publicly without appropriate access control.

### Example investigation response contract

``` json
{
  "investigation_id": "uuid",
  "incident_id": "uuid",
  "status": "completed",
  "summary": "Elevated vibration and temperature warrant inspection.",
  "risk": {
    "risk_score": 0.72,
    "estimated_probability": null,
    "reliability_status": "medium",
    "uncertainty": {
      "method": "documented_method_name_or_heuristic",
      "lower": null,
      "upper": null,
      "limitations": ["Synthetic demo data; not calibrated on real factory data."]
    }
  },
  "hypotheses": [
    {
      "label": "Possible bearing wear",
      "supporting_evidence_refs": ["chunk-id"],
      "counter_evidence": [],
      "status": "hypothesis_not_confirmed"
    }
  ],
  "recommendations": [],
  "missing_information": [],
  "audit_events": []
}
```

This is an illustrative schema, not a fixed output to hard-code.
Implement and validate real schemas in Pydantic. A `risk_score` must not
be silently presented as a probability.

------------------------------------------------------------------------

## 10. ML Design

### Dataset strategy

The MVP should be runnable without private industrial data. Generate a
seeded synthetic factory dataset with documented rules and scenarios.
Keep generation deterministic with a configurable random seed. If
suitable public predictive-maintenance datasets are later added, record
their license, provenance, feature mapping, and train/test protocol.

Synthetic data should include: - Normal operation. - Gradual sensor
drift. - Abrupt vibration/temperature increase. - Missing or delayed
readings. - An upstream asset failure affecting dependent assets. -
Maintenance intervention and recovery. - A few examples with ambiguous
or conflicting indicators.

Avoid leakage: do not put the synthetic failure label or future outcome
directly into input features. Split by time, asset, or scenario where
appropriate, rather than randomly splitting nearly identical adjacent
records across train and test.

### Graph construction

-   Each asset is a graph node.
-   Edges encode operational or dependency relationships.
-   Node features include asset class, criticality, sensor summary
    statistics, anomaly indicators, and missingness.
-   Preserve edge direction/relationship types where the model supports
    them; otherwise document the simplification.
-   Normalize numerical features using training-only statistics.
-   Save feature schema and model version with trained artifacts.

### Model plan

1.  Implement a transparent threshold/feature baseline.
2.  Implement a small PyTorch Geometric graph model suitable for the
    seeded graph.
3.  Train and evaluate using reproducible scripts.
4.  Compare the model against the baseline on a held-out set.
5.  Save model artifact and metadata, including feature schema, random
    seed, data version, and evaluation metrics.
6.  Make inference fail clearly if the model artifact or expected
    features are missing; allow a documented baseline fallback.

Do not train a large model merely to include a GNN in the tech stack.
The graph model must be compared with a reasonable baseline and its
benefit assessed.

### Uncertainty strategy

Choose a method appropriate to the task and available data: - For
regression, conformal prediction intervals can provide empirical
coverage under stated exchangeability assumptions. - For classification,
use calibration methods and report Brier score/calibration curves; a
conformal prediction set may be added if justified. - If a valid
calibration dataset is unavailable, show a clearly labeled heuristic
reliability status rather than claiming calibrated probabilities.

Report: - MAE/RMSE or classification precision, recall, F1, and AUROC as
appropriate. - Calibration error or Brier score for probability
outputs. - Prediction interval coverage and width for regression
intervals. - Performance on missing-data and disruption scenarios. -
Baseline comparison and known failure modes.

### Model card

Create `docs/MODEL_CARD.md` covering intended use, prohibited use, data
origin, synthetic-data limitations, features, evaluation split, metrics,
calibration method, known failure modes, and model version.

------------------------------------------------------------------------

## 11. RAG and Local Model Strategy

The platform must not depend on a paid LLM API.

### Embeddings and vector search

-   Use a local Sentence Transformers-compatible embedding model
    configured by environment variable.
-   Store vector dimension and model identifier in configuration and
    validate them when creating/searching the Qdrant collection.
-   Use deterministic demo document IDs and idempotent ingestion.
-   Preserve chunk-level metadata so the frontend can show citations.
-   If the embedding model cannot be downloaded, provide an actionable
    setup error; do not silently create random embeddings and pretend
    semantic retrieval works.

### LLM

-   Define a provider interface. A local model adapter may be added if a
    supported local runtime is available.
-   The agent workflow must still run in deterministic mode with no LLM
    configured.
-   If an LLM is configured, require structured outputs validated
    against Pydantic schemas.
-   Treat retrieved documents as untrusted data. They are evidence, not
    instructions that can override system rules.
-   Limit context size and include only relevant retrieved chunks.
-   Do not expose chain-of-thought. Return concise evidence-based
    rationales, source references, and uncertainty.

------------------------------------------------------------------------

## 12. Digital Twin and Decision Logic

### Twin state

Maintain a simulation snapshot of: - Asset operational state and
capacity. - Dependency graph. - Current or scenario-specific
availability. - Scenario duration and intervention assumptions. -
Production throughput or flow metric. - Cost assumptions and downtime.

### Scenario execution

A simulation should: 1. Validate the requested scenario and parameters.
2. Load a consistent asset/edge snapshot. 3. Compute baseline outcomes.
4. Apply scenario changes to a copy of the state. 5. Propagate
dependency effects using explicit rules. 6. Calculate scenario outcomes.
7. Return baseline, scenario, delta, assumptions, and affected asset
IDs. 8. Persist the result if requested.

### Example scenarios

-   Motor offline for 45 minutes.
-   Conveyor capacity reduced by 30% for one hour.
-   Inspection requiring 20 minutes of downtime.
-   Replace a component at a defined cost and repair duration.
-   Compare monitor-only versus planned maintenance.

### Decision scoring

Use an explainable score such as:

`action_score = w_risk * risk_reduction - w_downtime * downtime_cost - w_direct_cost * direct_cost - w_uncertainty * uncertainty_penalty`

This formula is a starting point only. Normalize features before
combining them, document units and sign conventions, make weights
configurable, and show component contributions in the UI. Do not use the
score as an objectively optimal answer without validation.

------------------------------------------------------------------------

## 13. Frontend Design

### UX principles

-   Professional industrial operations dashboard; high information
    density without clutter.
-   Use status labels and accessible contrast.
-   Distinguish observed telemetry, model predictions, retrieved
    evidence, and simulated values visually and in text.
-   Always show data timestamp and whether data is synthetic/demo.
-   Display uncertainty with labels and ranges, not just a
    green/yellow/red badge.
-   Avoid presenting a generated hypothesis as a confirmed fault.
-   Provide a clear empty state when no incidents or evidence exist.

### Main dashboard layout

-   Left navigation: Overview, Factory Graph, Incidents, Digital Twin,
    Evidence, Model Evaluation.
-   Overview cards: assets operational, degraded/offline assets, active
    incidents, recent simulations.
-   Factory topology panel with node/edge legend and filters.
-   Incident list with severity, asset, time, status, and reliability
    indicator.
-   Recent simulation comparisons.

### Investigation page

Sections: 1. Incident summary and observed symptoms. 2. Asset and
dependency context. 3. Risk score, uncertainty method, and reliability
explanation. 4. Hypotheses with supporting/counter evidence. 5.
Retrieved evidence with document title and section/chunk reference. 6.
Ranked actions with score breakdown and simulation impact. 7. Missing
information and recommended follow-up checks. 8. Audit timeline of
workflow steps and tool outcomes.

### Digital Twin Lab

-   Select incident or asset.
-   Choose scenario and set parameters.
-   Run simulation.
-   Compare baseline and scenario metrics.
-   List affected assets and show the topology impact.
-   Display simulation assumptions and synthetic-data disclaimer.

### Frontend implementation guidance

-   Use React + TypeScript with Vite.
-   Use a consistent component library or simple custom components; do
    not add multiple UI frameworks.
-   Use a graph visualization library compatible with React for the
    topology.
-   Use a charting library for telemetry timelines and comparisons.
-   Keep API calls in a typed client module.
-   Add loading/error states and avoid duplicating business logic in the
    frontend.
-   Use environment variables for the API base URL.
-   Add a small set of frontend tests for critical views and API error
    states if feasible.

------------------------------------------------------------------------

## 14. Local Development and Configuration

### Suggested environment variables

``` dotenv
APP_ENV=development
APP_NAME=ForgeMind
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://forgemind:forgemind@localhost:5432/forgemind
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=forgemind_maintenance
FRONTEND_ORIGIN=http://localhost:5173
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
LLM_PROVIDER=none
LLM_BASE_URL=
LLM_MODEL=
RANDOM_SEED=42
DEMO_MODE=true
```

Use safe local-only defaults in development. Explain how to override
them. Do not put production secrets in this file.

### Docker Compose

Provide services for PostgreSQL and Qdrant. The backend and frontend may
run locally during development, or be included as optional services once
their Dockerfiles are reliable. Add health checks and named volumes. Do
not expose databases publicly in deployment examples.

### Expected local workflow

Document commands appropriate to the chosen package managers: 1. Copy
`.env.example` to `.env`. 2. Start PostgreSQL and Qdrant. 3. Install
backend dependencies. 4. Run migrations. 5. Seed demo factory and
documents. 6. Run model setup/training or load the included small demo
artifact. 7. Start FastAPI. 8. Install frontend dependencies and start
React. 9. Open the dashboard and run the included demo incident.

The exact commands must match the manifests actually created. Do not
document commands that have not been verified.

------------------------------------------------------------------------

## 15. Testing Strategy

### Backend unit tests

-   Asset and edge validation.
-   Graph neighborhood and dependency propagation.
-   Telemetry aggregation and anomaly rules.
-   Feature construction and normalization.
-   Risk output schema and low-evidence behavior.
-   Uncertainty interval/calibration utility behavior.
-   Action scoring and weight configuration.
-   Simulator determinism and scenario deltas.
-   RAG chunk metadata and empty-retrieval behavior.
-   Agent output validation and tool parameter validation.

### Integration tests

-   API reads seeded assets and graph.
-   Incident creation and retrieval.
-   Investigation completes in deterministic mode without an LLM.
-   Qdrant retrieval returns valid source metadata.
-   Simulation persists and can be retrieved.
-   PostgreSQL migrations and repositories behave as expected.

### Frontend checks

-   Overview renders empty/loading/error and seeded states.
-   Selecting an asset opens its detail view.
-   Incident investigation shows evidence and uncertainty.
-   Simulation form validates parameters and compares results.
-   Evidence citations are navigable/inspectable.

### End-to-end acceptance scenario

A seeded vibration/temperature incident on a motor must: 1. Be visible
in the incident list. 2. Open to an asset with telemetry and graph
neighbors. 3. Produce a structured investigation without a paid API. 4.
Retrieve at least one relevant demo maintenance document, or explicitly
state that none was found. 5. Show a model score and an honest
reliability/uncertainty status. 6. Rank at least two candidate actions
with visible scoring components. 7. Run a scenario and display baseline
versus simulated impact. 8. Preserve a traceable
investigation/simulation record in PostgreSQL.

------------------------------------------------------------------------

## 16. Security, Reliability, and Safety

-   No real machine-control interface or actuation in this project.
-   Treat all recommendations as advisory.
-   Validate all IDs, enum values, numeric ranges, and scenario
    parameters.
-   Apply request size limits to document ingestion.
-   Avoid arbitrary file paths and shell execution from user or LLM
    input.
-   Use parameterized database access through SQLAlchemy.
-   Do not log credentials, raw secrets, or unnecessary sensitive
    content.
-   Treat retrieved documents and telemetry text as untrusted input.
-   Add bounded agent execution and graceful timeouts.
-   Use safe error messages; keep detailed diagnostics in local logs.
-   Handle unavailable PostgreSQL/Qdrant/model services with clear
    health and error states.
-   Keep data provenance and synthetic-data labels visible.
-   No claims of real-world predictive performance without suitable
    real-world validation.

------------------------------------------------------------------------

## 17. Implementation Plan and Milestones

Create `docs/IMPLEMENTATION_PLAN.md` with this checklist and update it
as work progresses.

### Phase 0 --- Repository inspection and plan

-   [ ] Inspect repository, current dependencies, and existing
    implementation.
-   [ ] Identify conventions and risks; do not overwrite useful work.
-   [ ] Write implementation plan and architecture notes.
-   [ ] Confirm scope and acceptance criteria.

### Phase 1 --- Foundation and persistence

-   [ ] Set up backend project and configuration.
-   [ ] Add PostgreSQL connection, SQLAlchemy models, and Alembic
    migrations.
-   [ ] Add FastAPI health endpoint and structured error handling.
-   [ ] Add Docker Compose for PostgreSQL and Qdrant.
-   [ ] Add deterministic demo factory seed script.
-   [ ] Test migration, seed idempotency, and core asset endpoints.

### Phase 2 --- Graph and telemetry

-   [ ] Implement asset graph query and neighborhood traversal.
-   [ ] Add telemetry schema, seeded patterns, and aggregation
    endpoints.
-   [ ] Implement deterministic anomaly/incident generation.
-   [ ] Add unit and integration tests.

### Phase 3 --- ML baseline and GNN

-   [ ] Implement graph feature construction.
-   [ ] Implement baseline predictor.
-   [ ] Implement PyTorch Geometric model and reproducible
    training/evaluation script.
-   [ ] Add inference interface and model metadata.
-   [ ] Add uncertainty/reliability output with honest limitations.
-   [ ] Document metrics and data limitations in model card.

### Phase 4 --- RAG

-   [ ] Create original demo maintenance documents.
-   [ ] Implement chunking, metadata, local embeddings, and Qdrant
    ingestion.
-   [ ] Implement retrieval service with source references.
-   [ ] Test relevant retrieval, empty results, and idempotent
    reindexing.

### Phase 5 --- Digital twin and recommendations

-   [ ] Implement deterministic simulator.
-   [ ] Add baseline and scenario comparison schemas.
-   [ ] Implement controlled candidate-action catalog.
-   [ ] Implement transparent weighted action ranking.
-   [ ] Test dependency propagation, deterministic output, and scoring.

### Phase 6 --- LangGraph investigation workflow

-   [ ] Define typed workflow state.
-   [ ] Implement bounded graph nodes and validated tools.
-   [ ] Connect telemetry, graph, model, RAG, ranking, and simulation
    services.
-   [ ] Implement deterministic fallback with no LLM configured.
-   [ ] Add output validation and audit events.
-   [ ] Test full incident investigation.

### Phase 7 --- React dashboard

-   [ ] Set up React + TypeScript frontend and typed API client.
-   [ ] Implement overview and incident list.
-   [ ] Implement interactive factory graph and asset details.
-   [ ] Implement investigation/evidence view.
-   [ ] Implement digital twin scenario comparison.
-   [ ] Implement model evaluation view and status/error states.

### Phase 8 --- Integration and documentation

-   [ ] Run backend unit, integration, and contract tests.
-   [ ] Run frontend checks/build.
-   [ ] Run the end-to-end acceptance scenario.
-   [ ] Verify a clean local setup from README.
-   [ ] Document API, architecture, data provenance, model limitations,
    and demo workflow.
-   [ ] Record remaining limitations and only claim tests actually run.

### Definition of done

The MVP is complete only when the acceptance scenario in Section 15
passes in deterministic, no-paid-API mode, the dashboard is usable,
setup instructions are reproducible, and the model's uncertainty/data
limitations are visible.

------------------------------------------------------------------------

## 18. Final Guidance to Antigravity

Prioritize a working vertical slice over broad scaffolding. The first
demonstrable end-to-end path should be:

**Seed factory → view graph and telemetry → trigger demo incident →
investigate with deterministic LangGraph workflow → retrieve maintenance
evidence from Qdrant → calculate risk/reliability → rank actions →
simulate an intervention → compare results in React.**

Only after that path works should the GNN sophistication, optional local
LLM, and additional UI polish be expanded.

Do not generate the entire repository in one unreviewed step. Build,
run, test, and document each phase. Keep the project understandable
enough that a student can explain every architectural decision and
defend each evaluation metric in a technical interview.
