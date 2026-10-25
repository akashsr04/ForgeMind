from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    name: str = Field(..., max_length=255)
    asset_type: str = Field(..., max_length=100)
    location: Optional[str] = Field(default=None, max_length=255)
    criticality: float = Field(default=1.0, ge=1.0, le=5.0)
    status: str = Field(default="operational")
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    pass


class AssetResponse(AssetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetEdgeBase(BaseModel):
    source_asset_id: str
    target_asset_id: str
    relationship_type: str
    weight: float = Field(default=1.0)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class AssetEdgeCreate(AssetEdgeBase):
    pass


class AssetEdgeResponse(AssetEdgeBase):
    id: str

    class Config:
        from_attributes = True


class NeighborAssetInfo(BaseModel):
    asset: AssetResponse
    relationship_type: str
    direction: str  # "upstream" or "downstream"
    weight: float


class AssetNeighborsResponse(BaseModel):
    asset_id: str
    neighbors: List[NeighborAssetInfo]


class FactoryGraphNode(BaseModel):
    id: str
    name: str
    asset_type: str
    location: Optional[str] = None
    criticality: float
    status: str
    active_incidents_count: int = 0
    current_risk_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FactoryGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    weight: float


class FactoryGraphResponse(BaseModel):
    nodes: List[FactoryGraphNode]
    edges: List[FactoryGraphEdge]
    total_assets: int
    operational_count: int
    degraded_count: int
    offline_count: int
