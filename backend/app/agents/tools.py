from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.infrastructure.db.models import Asset, AssetEdge, TelemetryReading, Incident
from app.rag.retrieval import retrieve_maintenance_evidence
from app.ml.features import extract_node_features
from app.ml.uncertainty import assess_uncertainty_and_reliability
from app.ml.models.baseline import BaselineRiskPredictor
from app.domain.recommendations.ranker import rank_candidate_actions
from app.schemas.recommendations import ActionRankingRequest
from app.core.logging import logger

_baseline_model = BaselineRiskPredictor()


def tool_get_asset_context(asset_id: str, db: Session) -> Dict[str, Any]:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return {"error": f"Asset {asset_id} not found"}

    # Find upstream and downstream neighbors
    outgoing = db.query(AssetEdge).filter(AssetEdge.source_asset_id == asset_id).all()
    incoming = db.query(AssetEdge).filter(AssetEdge.target_asset_id == asset_id).all()

    downstream_info = []
    for edge in outgoing:
        target = db.query(Asset).filter(Asset.id == edge.target_asset_id).first()
        if target:
            downstream_info.append({"asset_id": target.id, "name": target.name, "relationship": edge.relationship_type})

    upstream_info = []
    for edge in incoming:
        source = db.query(Asset).filter(Asset.id == edge.source_asset_id).first()
        if source:
            upstream_info.append({"asset_id": source.id, "name": source.name, "relationship": edge.relationship_type})

    return {
        "id": asset.id,
        "name": asset.name,
        "asset_type": asset.asset_type,
        "criticality": asset.criticality,
        "status": asset.status,
        "location": asset.location,
        "metadata": asset.metadata_json or {},
        "upstream_neighbors": upstream_info,
        "downstream_neighbors": downstream_info,
    }


def tool_summarize_telemetry(asset_id: str, db: Session, limit: int = 50) -> Dict[str, Any]:
    readings = (
        db.query(TelemetryReading)
        .filter(TelemetryReading.asset_id == asset_id)
        .order_by(TelemetryReading.observed_at.desc())
        .limit(limit)
        .all()
    )

    if not readings:
        return {
            "has_data": False,
            "readings_count": 0,
            "sensors": {},
            "anomaly_detected": False,
        }

    sensors: Dict[str, Dict[str, Any]] = {}
    for r in readings:
        name = r.sensor_name
        if name not in sensors:
            sensors[name] = {"values": [], "unit": r.unit, "latest": r.value}
        sensors[name]["values"].append(r.value)

    summary: Dict[str, Any] = {}
    anomaly_detected = False

    for name, data in sensors.items():
        vals = data["values"]
        mean_v = float(np.mean(vals))
        max_v = float(np.max(vals))
        std_v = float(np.std(vals))
        is_anom = False

        if name == "vibration" and max_v > 4.5:
            is_anom = True
            anomaly_detected = True
        elif name == "temperature" and max_v > 80.0:
            is_anom = True
            anomaly_detected = True

        summary[name] = {
            "unit": data["unit"],
            "latest": round(data["latest"], 3),
            "mean": round(mean_v, 3),
            "max": round(max_v, 3),
            "std": round(std_v, 3),
            "count": len(vals),
            "is_anomalous": is_anom,
        }

    return {
        "has_data": True,
        "readings_count": len(readings),
        "sensors": summary,
        "anomaly_detected": anomaly_detected,
    }


def tool_predict_risk(asset_id: str, db: Session) -> Dict[str, Any]:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return {"error": "Asset not found"}

    readings = (
        db.query(TelemetryReading)
        .filter(TelemetryReading.asset_id == asset_id)
        .order_by(TelemetryReading.observed_at.desc())
        .limit(50)
        .all()
    )

    node_features = extract_node_features(asset, readings)
    raw_score = _baseline_model.predict_risk(node_features)

    # Count neighbors
    edge_count = (
        db.query(AssetEdge)
        .filter((AssetEdge.source_asset_id == asset_id) | (AssetEdge.target_asset_id == asset_id))
        .count()
    )

    assessment = assess_uncertainty_and_reliability(
        risk_score=raw_score,
        node_features=node_features,
        calibration_residuals=None,
        neighbor_count=edge_count,
    )

    return assessment.model_dump()


def tool_retrieve_evidence(query: str, asset_type: str, limit: int = 3) -> List[Dict[str, Any]]:
    chunks = retrieve_maintenance_evidence(query_text=query, asset_type=asset_type, limit=limit)
    return [c.model_dump() for c in chunks]


def tool_rank_actions(asset_id: str, asset_type: str, evidence_refs: List[str]) -> List[Dict[str, Any]]:
    req = ActionRankingRequest(
        asset_id=asset_id,
        weight_risk=100.0,
        weight_downtime=0.5,
        weight_direct_cost=0.1,
        weight_uncertainty=20.0,
    )
    ranking_res = rank_candidate_actions(asset_type, req, evidence_refs=evidence_refs)
    return [a.model_dump() for a in ranking_res.ranked_actions]
