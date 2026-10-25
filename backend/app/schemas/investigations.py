from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import RiskAssessment
from app.schemas.recommendations import ScoredActionResponse
from app.schemas.documents import DocumentChunkResponse


class Hypothesis(BaseModel):
    label: str
    supporting_evidence_refs: List[str] = Field(default_factory=list)
    counter_evidence: List[str] = Field(default_factory=list)
    status: str = Field(default="hypothesis_not_confirmed")  # hypothesis_not_confirmed, confirmed, rejected
    rationale: Optional[str] = None


class AuditEvent(BaseModel):
    timestamp: datetime
    step: str
    action: str
    outcome: str
    details: Optional[Dict[str, Any]] = None


class StructuredInvestigation(BaseModel):
    investigation_id: str
    incident_id: str
    status: str
    summary: str
    risk: RiskAssessment
    hypotheses: List[Hypothesis]
    recommendations: List[ScoredActionResponse]
    retrieved_evidence: List[DocumentChunkResponse] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    audit_events: List[AuditEvent] = Field(default_factory=list)
    safety_disclaimer: str = (
        "Advisory industrial intelligence output only. ForgeMind does not actuate "
        "or control physical machinery. Human operator verification required."
    )


class InvestigationCreateRequest(BaseModel):
    override_notes: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: str
    incident_id: str
    status: str
    workflow_version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    summary: Optional[str] = None
    structured_result: Optional[StructuredInvestigation] = None
    error_code: Optional[str] = None

    class Config:
        from_attributes = True
