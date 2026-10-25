import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Incident, Asset, TelemetryReading
from app.schemas.incidents import IncidentResponse, IncidentCreate, IncidentTriggerRequest
from app.schemas.investigations import StructuredInvestigation, InvestigationResponse
from app.agents.graph import run_investigation_pipeline
from app.core.errors import ResourceNotFoundException

router = APIRouter(tags=["Incidents"])


@router.get("/incidents", response_model=List[IncidentResponse])
def list_incidents(
    status: Optional[str] = None,
    asset_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if asset_id:
        query = query.filter(Incident.asset_id == asset_id)
    return query.order_by(Incident.detected_at.desc()).all()


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise ResourceNotFoundException("Incident", incident_id)
    return inc


@router.post("/incidents/demo-trigger", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def trigger_demo_incident(
    req: IncidentTriggerRequest,
    db: Session = Depends(get_db),
):
    # Default to primary motor if asset_id omitted
    asset_id = req.asset_id or "11111111-1111-1111-1111-111111111102"
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise ResourceNotFoundException("Asset", asset_id)

    # Mark asset degraded
    asset.status = "degraded"
    now = datetime.now(timezone.utc)

    # Inject triggering sensor telemetry readings
    vib_reading = TelemetryReading(
        asset_id=asset_id,
        sensor_name="vibration",
        value=5.85,
        unit="mm/s",
        observed_at=now,
        source="demo_trigger",
    )
    temp_reading = TelemetryReading(
        asset_id=asset_id,
        sensor_name="temperature",
        value=86.8,
        unit="deg_C",
        observed_at=now,
        source="demo_trigger",
    )
    db.add_all([vib_reading, temp_reading])

    incident = Incident(
        id=str(uuid.uuid4()),
        asset_id=asset_id,
        title=f"Critical Telemetry Anomaly Detected on {asset.name}",
        description=(
            f"Vibration telemetry escalated to 5.85 mm/s (warning limit 4.5 mm/s) accompanied by "
            f"thermal surge to 86.8°C. Immediate diagnostic investigation required to prevent stoppage."
        ),
        severity=req.severity,
        status="open",
        trigger_type="telemetry_anomaly",
        detected_at=now,
        context_json={
            "scenario": req.scenario,
            "vibration_peak": 5.85,
            "temperature_peak": 86.8,
            "simulated_trigger": True,
        },
        is_synthetic=True,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/incidents/{incident_id}/investigations", response_model=StructuredInvestigation, status_code=status.HTTP_201_CREATED)
def trigger_incident_investigation(
    incident_id: str,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise ResourceNotFoundException("Incident", incident_id)

    incident.status = "investigating"
    db.commit()

    structured_result = run_investigation_pipeline(incident_id=incident_id, db=db)
    return structured_result
