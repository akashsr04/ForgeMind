from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UncertaintyDetail(BaseModel):
    method: str = Field(description="Documented method name or heuristic, e.g. 'conformal_prediction', 'calibration_brier', 'heuristic_dispersion'")
    lower: Optional[float] = Field(default=None, description="Lower confidence or credible interval bound")
    upper: Optional[float] = Field(default=None, description="Upper confidence or credible interval bound")
    limitations: List[str] = Field(default_factory=list, description="Explicit stated limitations of the estimate")


class RiskAssessment(BaseModel):
    risk_score: float = Field(ge=0.0, le=1.0, description="Model anomaly or risk score on [0, 1]")
    estimated_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Calibrated failure probability, or null if uncalibrated")
    reliability_status: str = Field(description="Human-readable status: 'high', 'medium', 'low', 'insufficient_evidence'")
    uncertainty: UncertaintyDetail
    explanation: Optional[str] = Field(default=None, description="Short human-readable rationale for reliability status")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
