from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Asset, AssetEdge, TelemetryReading, Incident
from app.schemas.assets import (
    AssetResponse,
    AssetNeighborsResponse,
    NeighborAssetInfo,
    FactoryGraphResponse,
    FactoryGraphNode,
    FactoryGraphEdge,
)
from app.schemas.telemetry import (
    AssetTelemetryResponse,
    TelemetryReadingResponse,
    SensorSummary,
)
from app.core.errors import ResourceNotFoundException
import numpy as np

router = APIRouter(tags=["Assets & Graph"])


@router.get("/assets", response_model=List[AssetResponse])
def list_assets(
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Asset)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    return query.order_by(Asset.name.asc()).all()


@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ResourceNotFoundException("Asset", asset_id)
    return asset


@router.get("/assets/{asset_id}/neighbors", response_model=AssetNeighborsResponse)
def get_asset_neighbors(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ResourceNotFoundException("Asset", asset_id)

    outgoing = db.query(AssetEdge).filter(AssetEdge.source_asset_id == asset_id).all()
    incoming = db.query(AssetEdge).filter(AssetEdge.target_asset_id == asset_id).all()

    neighbors: List[NeighborAssetInfo] = []

    for edge in outgoing:
        target = db.query(Asset).filter(Asset.id == edge.target_asset_id).first()
        if target:
            neighbors.append(
                NeighborAssetInfo(
                    asset=AssetResponse.model_validate(target),
                    relationship_type=edge.relationship_type,
                    direction="downstream",
                    weight=edge.weight,
                )
            )

    for edge in incoming:
        source = db.query(Asset).filter(Asset.id == edge.source_asset_id).first()
        if source:
            neighbors.append(
                NeighborAssetInfo(
                    asset=AssetResponse.model_validate(source),
                    relationship_type=edge.relationship_type,
                    direction="upstream",
                    weight=edge.weight,
                )
            )

    return AssetNeighborsResponse(asset_id=asset_id, neighbors=neighbors)


@router.get("/assets/{asset_id}/telemetry", response_model=AssetTelemetryResponse)
def get_asset_telemetry(
    asset_id: str,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ResourceNotFoundException("Asset", asset_id)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    readings = (
        db.query(TelemetryReading)
        .filter(TelemetryReading.asset_id == asset_id, TelemetryReading.observed_at >= cutoff)
        .order_by(TelemetryReading.observed_at.asc())
        .all()
    )

    # Compute sensor summaries
    by_sensor: dict = {}
    for r in readings:
        by_sensor.setdefault(r.sensor_name, {"unit": r.unit, "vals": []})["vals"].append(r.value)

    summaries = {}
    for s_name, data in by_sensor.items():
        vals = data["vals"]
        min_v = float(np.min(vals))
        max_v = float(np.max(vals))
        mean_v = float(np.mean(vals))
        std_v = float(np.std(vals))
        cur_v = vals[-1]

        is_anom = False
        label = "normal"
        if s_name == "vibration" and max_v > 4.5:
            is_anom = True
            label = "critical_drift" if cur_v > 5.0 else "elevated"
        elif s_name == "temperature" and max_v > 80.0:
            is_anom = True
            label = "spike" if cur_v > 85.0 else "elevated"

        summaries[s_name] = SensorSummary(
            sensor_name=s_name,
            unit=data["unit"],
            current_value=round(cur_v, 2),
            min_value=round(min_v, 2),
            max_value=round(max_v, 2),
            mean_value=round(mean_v, 2),
            std_value=round(std_v, 2),
            reading_count=len(vals),
            is_anomalous=is_anom,
            status_label=label,
        )

    return AssetTelemetryResponse(
        asset_id=asset_id,
        window_hours=hours,
        readings=[TelemetryReadingResponse.model_validate(r) for r in readings],
        summaries=summaries,
    )


@router.get("/factory/graph", response_model=FactoryGraphResponse)
def get_factory_graph(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    edges = db.query(AssetEdge).all()

    nodes: List[FactoryGraphNode] = []
    operational_count = 0
    degraded_count = 0
    offline_count = 0

    for a in assets:
        inc_count = (
            db.query(Incident)
            .filter(Incident.asset_id == a.id, Incident.status.in_(["open", "investigating"]))
            .count()
        )
        if a.status == "operational":
            operational_count += 1
        elif a.status == "degraded":
            degraded_count += 1
        else:
            offline_count += 1

        risk = 0.85 if a.status == "degraded" else (0.15 if a.status == "operational" else 0.95)

        nodes.append(
            FactoryGraphNode(
                id=a.id,
                name=a.name,
                asset_type=a.asset_type,
                location=a.location,
                criticality=a.criticality,
                status=a.status,
                active_incidents_count=inc_count,
                current_risk_score=risk,
                metadata=a.metadata_json or {},
            )
        )

    graph_edges = [
        FactoryGraphEdge(
            id=e.id,
            source=e.source_asset_id,
            target=e.target_asset_id,
            relationship_type=e.relationship_type,
            weight=e.weight,
        )
        for e in edges
    ]

    return FactoryGraphResponse(
        nodes=nodes,
        edges=graph_edges,
        total_assets=len(assets),
        operational_count=operational_count,
        degraded_count=degraded_count,
        offline_count=offline_count,
    )
