from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    incident_id: Optional[str] = None
    target_asset_id: str
    scenario_type: str = Field(..., description="outage, derating, inspection, repair")
    duration_minutes: float = Field(default=60.0, ge=1.0)
    derating_factor: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Used if scenario_type is derating (e.g. 0.5 = 50% capacity)")
    repair_cost_estimate: Optional[float] = Field(default=500.0, ge=0.0)
    persist_result: bool = Field(default=True)


class MetricSnapshot(BaseModel):
    throughput_units_per_hour: float
    total_factory_capacity_pct: float
    active_bottlenecks: List[str]
    estimated_downtime_hours: float
    estimated_financial_cost: float


class SimulationResponse(BaseModel):
    id: Optional[str] = None
    incident_id: Optional[str] = None
    target_asset_id: str
    scenario_type: str
    duration_minutes: float
    baseline: MetricSnapshot
    scenario: MetricSnapshot
    delta_throughput: float
    delta_cost: float
    delta_downtime_hours: float
    affected_asset_ids: List[str]
    propagation_path: List[str]
    assumptions: List[str]
    is_synthetic: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
