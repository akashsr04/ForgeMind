import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.db.session import SessionLocal, init_db
from app.seed.demo_factory import seed_demo_factory
from app.rag.ingestion import ingest_demo_documents


@pytest.fixture(scope="module")
def client():
    init_db()
    db = SessionLocal()
    seed_demo_factory(db)
    ingest_demo_documents(db)
    db.close()

    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("ok", "degraded")
    assert "dependencies" in data


def test_overview_endpoint(client):
    res = client.get("/api/v1/overview")
    assert res.status_code == 200
    data = res.json()
    assert "factory_health" in data
    assert data["factory_health"]["total_assets"] >= 7
    assert data["active_incidents_count"] >= 1


def test_factory_graph_endpoint(client):
    res = client.get("/api/v1/factory/graph")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) >= 7
    assert len(data["edges"]) >= 7
    # Verify node properties
    first_node = data["nodes"][0]
    assert "id" in first_node
    assert "criticality" in first_node
    assert "current_risk_score" in first_node


def test_asset_telemetry_endpoint(client):
    # Motor M-101
    motor_id = "11111111-1111-1111-1111-111111111102"
    res = client.get(f"/api/v1/assets/{motor_id}/telemetry?hours=24")
    assert res.status_code == 200
    data = res.json()
    assert len(data["readings"]) > 0
    assert "vibration" in data["summaries"]
    assert "temperature" in data["summaries"]
    assert data["summaries"]["vibration"]["is_anomalous"] is True


def test_simulation_endpoint(client):
    motor_id = "11111111-1111-1111-1111-111111111102"
    payload = {
        "target_asset_id": motor_id,
        "scenario_type": "derating",
        "duration_minutes": 60.0,
        "derating_factor": 0.5,
        "persist_result": True,
    }
    res = client.post("/api/v1/simulations", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["scenario_type"] == "derating"
    assert data["baseline"]["throughput_units_per_hour"] == 300.0
    assert data["scenario"]["throughput_units_per_hour"] == 160.0
    assert len(data["affected_asset_ids"]) >= 1


def test_recommendations_rank_endpoint(client):
    motor_id = "11111111-1111-1111-1111-111111111102"
    payload = {
        "asset_id": motor_id,
        "weight_risk": 100.0,
        "weight_downtime": 0.5,
        "weight_direct_cost": 0.1,
        "weight_uncertainty": 20.0,
    }
    res = client.post("/api/v1/recommendations/rank", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["ranked_actions"]) >= 3
    assert data["ranked_actions"][0]["net_score"] >= data["ranked_actions"][1]["net_score"]


def test_model_evaluation_endpoint(client):
    res = client.get("/api/v1/model/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "baseline_model" in data
    assert "gnn_model" in data
    assert "uncertainty_evaluation" in data
    assert data["gnn_model"]["auroc"] >= 0.85
    assert data["uncertainty_evaluation"]["nominal_coverage_target"] == 0.90


def test_end_to_end_investigation_workflow(client):
    # Retrieve canonical demo incident
    incidents_res = client.get("/api/v1/incidents")
    assert incidents_res.status_code == 200
    incidents = incidents_res.json()
    assert len(incidents) > 0

    target_inc = incidents[0]
    inc_id = target_inc["id"]

    # Trigger investigation
    inv_res = client.post(f"/api/v1/incidents/{inc_id}/investigations")
    assert inv_res.status_code == 201
    inv_data = inv_res.json()

    # Validate Section 9 & Section 15 acceptance criteria:
    # 1. Status is completed
    assert inv_data["status"] == "completed"
    # 2. Risk score and honest reliability
    assert "risk" in inv_data
    assert 0.0 <= inv_data["risk"]["risk_score"] <= 1.0
    assert inv_data["risk"]["reliability_status"] in ("high", "medium", "low", "insufficient_evidence")
    assert len(inv_data["risk"]["uncertainty"]["limitations"]) > 0
    # 3. Hypotheses with evidence references
    assert len(inv_data["hypotheses"]) >= 1
    # 4. Retrieved evidence chunks
    assert len(inv_data["retrieved_evidence"]) >= 1
    # 5. Ranked candidate actions
    assert len(inv_data["recommendations"]) >= 2
    # 6. Safety disclaimer present
    assert "Advisory industrial intelligence output only" in inv_data["safety_disclaimer"]
    # 7. Audit events present
    assert len(inv_data["audit_events"]) >= 6
