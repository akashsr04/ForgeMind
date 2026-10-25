import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.agents.state import InvestigationState
from app.agents.nodes import (
    parse_request_node,
    collect_asset_context_node,
    summarize_telemetry_node,
    estimate_risk_node,
    retrieve_evidence_node,
    generate_hypotheses_node,
    rank_actions_node,
    validate_output_node,
)
from app.infrastructure.db.models import Investigation, Recommendation
from app.schemas.investigations import StructuredInvestigation, Hypothesis, AuditEvent
from app.schemas.recommendations import ScoredActionResponse
from app.schemas.documents import DocumentChunkResponse
from app.schemas.common import RiskAssessment
from app.core.logging import logger

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def build_investigation_workflow():
    """
    Constructs the bounded LangGraph state graph.
    """
    if LANGGRAPH_AVAILABLE:
        workflow = StateGraph(InvestigationState)
        workflow.add_node("parse_request", lambda s: parse_request_node(s, s["_db"]))
        workflow.add_node("collect_asset_context", lambda s: collect_asset_context_node(s, s["_db"]))
        workflow.add_node("summarize_telemetry", lambda s: summarize_telemetry_node(s, s["_db"]))
        workflow.add_node("estimate_risk", lambda s: estimate_risk_node(s, s["_db"]))
        workflow.add_node("retrieve_evidence", lambda s: retrieve_evidence_node(s, s["_db"]))
        workflow.add_node("generate_hypotheses", lambda s: generate_hypotheses_node(s, s["_db"]))
        workflow.add_node("rank_actions", lambda s: rank_actions_node(s, s["_db"]))
        workflow.add_node("validate_output", lambda s: validate_output_node(s, s["_db"]))

        workflow.set_entry_point("parse_request")
        workflow.add_edge("parse_request", "collect_asset_context")
        workflow.add_edge("collect_asset_context", "summarize_telemetry")
        workflow.add_edge("summarize_telemetry", "estimate_risk")
        workflow.add_edge("estimate_risk", "retrieve_evidence")
        workflow.add_edge("retrieve_evidence", "generate_hypotheses")
        workflow.add_edge("generate_hypotheses", "rank_actions")
        workflow.add_edge("rank_actions", "validate_output")
        workflow.add_edge("validate_output", END)
        return workflow.compile()
    return None


def run_investigation_pipeline(incident_id: str, db: Session) -> StructuredInvestigation:
    """
    Executes the bounded multi-step investigation workflow, records audit events,
    persists results to the database, and returns the validated structured result.
    """
    investigation_id = str(uuid.uuid4())
    logger.info(f"Starting investigation {investigation_id} for incident {incident_id}...")

    state: InvestigationState = {
        "investigation_id": investigation_id,
        "incident_id": incident_id,
        "step_count": 0,
        "status": "pending",
        "audit_events": [],
    }

    # Bounded sequential execution
    pipeline_steps = [
        ("parse_request", parse_request_node),
        ("collect_asset_context", collect_asset_context_node),
        ("summarize_telemetry", summarize_telemetry_node),
        ("estimate_risk", estimate_risk_node),
        ("retrieve_evidence", retrieve_evidence_node),
        ("generate_hypotheses", generate_hypotheses_node),
        ("rank_actions", rank_actions_node),
        ("validate_output", validate_output_node),
    ]

    for step_name, node_func in pipeline_steps:
        try:
            state = node_func(state, db)
            if state.get("status") == "failed":
                logger.error(f"Investigation failed at step {step_name}: {state.get('error')}")
                break
        except Exception as e:
            logger.exception(f"Unhandled exception in investigation step {step_name}: {e}")
            state["status"] = "failed"
            state["error"] = str(e)
            break

    # Construct typed Pydantic result
    audit_objs = [
        AuditEvent(
            timestamp=datetime.fromisoformat(ev["timestamp"]),
            step=ev["step"],
            action=ev["action"],
            outcome=ev["outcome"],
            details=ev.get("details"),
        )
        for ev in state.get("audit_events", [])
    ]

    evidence_objs = [
        DocumentChunkResponse(
            chunk_id=c["chunk_id"],
            document_id=c.get("document_id", ""),
            title=c["title"],
            section=c["section"],
            asset_type=c["asset_type"],
            content=c["content"],
            similarity_score=c.get("similarity_score"),
            metadata=c.get("metadata", {}),
        )
        for c in state.get("evidence_chunks", [])
    ]

    hypo_objs = [
        Hypothesis(
            label=h["label"],
            supporting_evidence_refs=h.get("supporting_evidence_refs", []),
            counter_evidence=h.get("counter_evidence", []),
            status=h.get("status", "hypothesis_not_confirmed"),
            rationale=h.get("rationale"),
        )
        for h in state.get("hypotheses", [])
    ]

    action_objs = [
        ScoredActionResponse(**a)
        for a in state.get("ranked_actions", [])
    ]

    risk_obj = RiskAssessment(**state.get("risk_assessment", {
        "risk_score": 0.5,
        "reliability_status": "low",
        "uncertainty": {"method": "fallback", "limitations": ["Investigation pipeline incomplete"]},
    }))

    structured = StructuredInvestigation(
        investigation_id=investigation_id,
        incident_id=incident_id,
        status=state.get("status", "completed"),
        summary=state.get("summary", "Investigation completed."),
        risk=risk_obj,
        hypotheses=hypo_objs,
        recommendations=action_objs,
        retrieved_evidence=evidence_objs,
        missing_information=state.get("missing_information", []),
        audit_events=audit_objs,
        safety_disclaimer=state.get("safety_disclaimer", ""),
    )

    # Persist in DB
    try:
        inv_record = Investigation(
            id=investigation_id,
            incident_id=incident_id,
            status=state.get("status", "completed"),
            workflow_version="1.0.0",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            summary=state.get("summary"),
            structured_result=structured.model_dump(mode="json"),
            error_code=state.get("error"),
        )
        db.add(inv_record)

        for act in action_objs:
            rec_record = Recommendation(
                investigation_id=investigation_id,
                action_type=act.action_type,
                title=act.title,
                rationale=act.rationale,
                score=act.net_score,
                score_components=act.score_components.model_dump(mode="json"),
                uncertainty_summary=act.uncertainty_summary,
                evidence_refs=act.evidence_refs,
                is_advisory=True,
            )
            db.add(rec_record)

        db.commit()
        logger.info(f"Investigation {investigation_id} persisted to database.")
    except Exception as e:
        logger.error(f"Failed to persist investigation: {e}")
        db.rollback()

    return structured
