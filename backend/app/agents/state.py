from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class InvestigationState(TypedDict, total=False):
    investigation_id: str
    incident_id: str
    asset_id: str
    asset_name: str
    asset_type: str
    asset_context: Dict[str, Any]
    telemetry_summary: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    evidence_chunks: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    ranked_actions: List[Dict[str, Any]]
    missing_information: List[str]
    audit_events: List[Dict[str, Any]]
    step_count: int
    status: str
    summary: str
    error: Optional[str]
    safety_disclaimer: str
