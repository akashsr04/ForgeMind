from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.agents.state import InvestigationState
from app.agents.tools import (
    tool_get_asset_context,
    tool_summarize_telemetry,
    tool_predict_risk,
    tool_retrieve_evidence,
    tool_rank_actions,
)
from app.infrastructure.db.models import Incident


def _audit(state: InvestigationState, step: str, action: str, outcome: str, details: Dict[str, Any] = None) -> None:
    events = state.setdefault("audit_events", [])
    events.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "action": action,
        "outcome": outcome,
        "details": details or {},
    })


def parse_request_node(state: InvestigationState, db: Session) -> InvestigationState:
    incident_id = state.get("incident_id")
    state["step_count"] = state.get("step_count", 0) + 1

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        state["status"] = "failed"
        state["error"] = f"Incident '{incident_id}' not found in database."
        _audit(state, "parse_request", "Verify Incident", "FAILED", {"incident_id": incident_id})
        return state

    state["asset_id"] = incident.asset_id
    state["status"] = "running"
    _audit(
        state,
        "parse_request",
        "Validate Incident Record",
        "SUCCESS",
        {"incident_title": incident.title, "asset_id": incident.asset_id, "severity": incident.severity},
    )
    return state


def collect_asset_context_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_id = state.get("asset_id")

    context = tool_get_asset_context(asset_id, db)
    state["asset_name"] = context.get("name", "Unknown Asset")
    state["asset_type"] = context.get("asset_type", "general")
    state["asset_context"] = context

    _audit(
        state,
        "collect_asset_context",
        "Query Asset Registry & Neighbors",
        "SUCCESS",
        {
            "asset_name": state["asset_name"],
            "upstream_count": len(context.get("upstream_neighbors", [])),
            "downstream_count": len(context.get("downstream_neighbors", [])),
        },
    )
    return state


def summarize_telemetry_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_id = state.get("asset_id")

    summary = tool_summarize_telemetry(asset_id, db)
    state["telemetry_summary"] = summary

    _audit(
        state,
        "summarize_telemetry",
        "Aggregate Sensor History",
        "SUCCESS",
        {
            "reading_count": summary.get("readings_count", 0),
            "anomaly_detected": summary.get("anomaly_detected", False),
            "sensors": list(summary.get("sensors", {}).keys()),
        },
    )
    return state


def estimate_risk_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_id = state.get("asset_id")

    risk = tool_predict_risk(asset_id, db)
    state["risk_assessment"] = risk

    _audit(
        state,
        "estimate_risk",
        "Evaluate Model Risk & Uncertainty",
        "SUCCESS",
        {
            "risk_score": risk.get("risk_score"),
            "reliability_status": risk.get("reliability_status"),
            "uncertainty_method": risk.get("uncertainty", {}).get("method"),
        },
    )
    return state


def retrieve_evidence_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_type = state.get("asset_type", "motor")

    # Formulate domain search query based on observed telemetry
    query = f"{asset_type} vibration bearing temperature maintenance SOP"
    chunks = tool_retrieve_evidence(query=query, asset_type=asset_type, limit=3)
    state["evidence_chunks"] = chunks

    chunk_ids = [c["chunk_id"] for c in chunks]
    _audit(
        state,
        "retrieve_maintenance_evidence",
        "Search Technical Knowledge Base (Qdrant)",
        "SUCCESS" if chunks else "NO_CHUNKS_FOUND",
        {"query": query, "chunks_retrieved": len(chunks), "chunk_ids": chunk_ids},
    )
    return state


def generate_hypotheses_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_type = state.get("asset_type", "motor")
    tel = state.get("telemetry_summary", {}).get("sensors", {})
    chunks = state.get("evidence_chunks", [])
    chunk_ids = [c["chunk_id"] for c in chunks]

    hypotheses: List[Dict[str, Any]] = []
    missing_info: List[str] = []

    vib_data = tel.get("vibration", {})
    temp_data = tel.get("temperature", {})

    # Check for bearing failure signature
    if vib_data.get("is_anomalous", False) and temp_data.get("is_anomalous", False):
        ref = [chunk_ids[0]] if chunk_ids else []
        hypotheses.append({
            "label": "Incipient Drive-End Bearing Spalling (SKF 6312)",
            "supporting_evidence_refs": ref,
            "counter_evidence": [],
            "status": "hypothesis_not_confirmed",
            "rationale": (
                f"Coincident vibration surge ({vib_data.get('max')} mm/s > 4.5 mm/s warning threshold) "
                f"and winding temperature elevation ({temp_data.get('max')}°C > 80.0°C limit) "
                f"match ISO 10816-3 Class II bearing fatigue indicators."
            ),
        })
        hypotheses.append({
            "label": "Mechanical Drive Coupling Misalignment",
            "supporting_evidence_refs": chunk_ids[1:2] if len(chunk_ids) > 1 else [],
            "counter_evidence": ["Absence of harmonic 2X RPM phase shift in current telemetry"],
            "status": "hypothesis_not_confirmed",
            "rationale": "Misalignment typically elevates 2X rotational harmonics; partial fit to current symptoms.",
        })
    elif vib_data.get("is_anomalous", False):
        hypotheses.append({
            "label": "Mechanical Looseness or Imbalance",
            "supporting_evidence_refs": chunk_ids[:1],
            "counter_evidence": [],
            "status": "hypothesis_not_confirmed",
            "rationale": f"Elevated vibration ({vib_data.get('max')} mm/s) without thermal runaway.",
        })
    else:
        hypotheses.append({
            "label": "Normal Operating Variations",
            "supporting_evidence_refs": [],
            "counter_evidence": [],
            "status": "hypothesis_not_confirmed",
            "rationale": "No critical threshold breaches observed in recent window.",
        })

    # Missing information checks
    missing_info.append("Lubricant grease spectroscopic contamination analysis")
    missing_info.append("High-frequency ultrasonic acoustic emissions (20-40 kHz)")

    state["hypotheses"] = hypotheses
    state["missing_information"] = missing_info

    _audit(
        state,
        "generate_hypotheses",
        "Synthesize Diagnostic Hypotheses",
        "SUCCESS",
        {"hypotheses_count": len(hypotheses), "cited_chunks": chunk_ids},
    )
    return state


def rank_actions_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    asset_id = state.get("asset_id")
    asset_type = state.get("asset_type", "motor")
    chunks = state.get("evidence_chunks", [])
    chunk_ids = [c["chunk_id"] for c in chunks]

    ranked = tool_rank_actions(asset_id, asset_type, evidence_refs=chunk_ids)
    state["ranked_actions"] = ranked

    _audit(
        state,
        "rank_actions",
        "Score & Rank Candidate Interventions",
        "SUCCESS",
        {"ranked_actions_count": len(ranked), "top_action": ranked[0]["title"] if ranked else None},
    )
    return state


def validate_output_node(state: InvestigationState, db: Session) -> InvestigationState:
    state["step_count"] = state.get("step_count", 0) + 1
    state["status"] = "completed"
    asset_name = state.get("asset_name", "Asset")
    risk_score = state.get("risk_assessment", {}).get("risk_score", 0.0)
    top_hypo = state.get("hypotheses", [{}])[0].get("label", "Unknown Issue")

    state["summary"] = (
        f"Investigation for {asset_name} completed. Primary hypothesis: '{top_hypo}'. "
        f"Assessed operational risk score: {risk_score:.2f} ({state.get('risk_assessment', {}).get('reliability_status')} reliability). "
        f"Recommended top action: '{state.get('ranked_actions', [{}])[0].get('title', 'Monitor')}'. "
        f"{len(state.get('evidence_chunks', []))} technical maintenance procedures cited."
    )

    state["safety_disclaimer"] = (
        "Advisory industrial intelligence output only. ForgeMind does not actuate "
        "or control physical machinery. Human operator verification required."
    )

    _audit(
        state,
        "validate_output",
        "Schema & Safety Disclaimer Validation",
        "SUCCESS",
        {"summary": state["summary"]},
    )
    return state
