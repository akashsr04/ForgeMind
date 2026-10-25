from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TelemetryReadingBase(BaseModel):
    asset_id: str
    sensor_name: str
    value: float
    unit: str
    observed_at: datetime
    source: str = "synthetic_sensor"


class TelemetryReadingCreate(TelemetryReadingBase):
    pass


class TelemetryReadingResponse(TelemetryReadingBase):
    id: str

    class Config:
        from_attributes = True


class SensorSummary(BaseModel):
    sensor_name: str
    unit: str
    current_value: float
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    reading_count: int
    is_anomalous: bool
    status_label: str  # "normal", "elevated", "critical_drift", "spike"


class AssetTelemetryResponse(BaseModel):
    asset_id: str
    window_hours: int
    readings: List[TelemetryReadingResponse]
    summaries: Dict[str, SensorSummary]
