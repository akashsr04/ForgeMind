from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class IncidentBase(BaseModel):
    asset_id: str
    title: str
    description: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    status: str = "open"  # open, investigating, mitigated, resolved
    trigger_type: str = "telemetry_anomaly"
    context_json: Dict[str, Any] = Field(default_factory=dict)
    is_synthetic: bool = True


class IncidentCreate(IncidentBase):
    pass


class IncidentResponse(IncidentBase):
    id: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentTriggerRequest(BaseModel):
    asset_id: Optional[str] = Field(default=None, description="Optional target asset ID. Defaults to the primary demo motor if omitted.")
    scenario: str = Field(default="bearing_wear_overheating", description="Demo anomaly scenario: 'bearing_wear_overheating', 'conveyor_jam', 'pump_cavitation'")
    severity: str = Field(default="high")
