from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import UncertaintyDetail


class CandidateAction(BaseModel):
    action_type: str = Field(description="inspect, derate, repair, replace, monitor")
    title: str
    rationale: str
    estimated_risk_reduction: float = Field(ge=0.0, le=1.0, description="Estimated proportional reduction in operational risk")
    estimated_downtime_minutes: float = Field(ge=0.0)
    estimated_direct_cost: float = Field(ge=0.0)
    production_impact_score: float = Field(ge=0.0, le=1.0)
    uncertainty_level: str = Field(default="medium", description="low, medium, high")


class ActionScoreComponents(BaseModel):
    risk_reduction_term: float
    downtime_cost_term: float
    direct_cost_term: float
    production_loss_term: float
    uncertainty_penalty_term: float
    net_score: float


class ScoredActionResponse(BaseModel):
    action_type: str
    title: str
    rationale: str
    net_score: float
    score_components: ActionScoreComponents
    uncertainty_summary: Dict[str, Any]
    evidence_refs: List[str]
    is_advisory: bool = True


class ActionRankingRequest(BaseModel):
    asset_id: str
    incident_id: Optional[str] = None
    candidate_actions: Optional[List[CandidateAction]] = None
    weight_risk: float = Field(default=100.0)
    weight_downtime: float = Field(default=0.5)
    weight_direct_cost: float = Field(default=0.1)
    weight_uncertainty: float = Field(default=20.0)


class ActionRankingResponse(BaseModel):
    asset_id: str
    incident_id: Optional[str] = None
    ranked_actions: List[ScoredActionResponse]
    ranking_notes: List[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    id: str
    investigation_id: str
    action_type: str
    title: str
    rationale: Optional[str] = None
    score: float
    score_components: Dict[str, Any]
    uncertainty_summary: Dict[str, Any]
    evidence_refs: List[str]
    is_advisory: bool = True

    class Config:
        from_attributes = True
