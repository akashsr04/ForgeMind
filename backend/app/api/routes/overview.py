from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Asset, Incident, Simulation, TelemetryReading
from app.schemas.incidents import IncidentResponse

router = APIRouter(tags=["Overview"])


@router.get("/overview")
def get_factory_overview(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    total_assets = len(assets)
    operational_count = sum(1 for a in assets if a.status == "operational")
    degraded_count = sum(1 for a in assets if a.status == "degraded")
    offline_count = sum(1 for a in assets if a.status in ("offline", "maintenance"))

    open_incidents = (
        db.query(Incident)
        .filter(Incident.status.in_(["open", "investigating"]))
        .order_by(Incident.detected_at.desc())
        .all()
    )

    recent_simulations = (
        db.query(Simulation)
        .order_by(Simulation.created_at.desc())
        .limit(5)
        .all()
    )

    # Latest readings from motor
    motor_asset = next((a for a in assets if a.asset_type == "motor"), None)
    motor_telemetry = {}
    if motor_asset:
        recent_motor_readings = (
            db.query(TelemetryReading)
            .filter(TelemetryReading.asset_id == motor_asset.id)
            .order_by(TelemetryReading.observed_at.desc())
            .limit(10)
            .all()
        )
        for r in recent_motor_readings:
            if r.sensor_name not in motor_telemetry:
                motor_telemetry[r.sensor_name] = {
                    "value": r.value,
                    "unit": r.unit,
                    "observed_at": r.observed_at.isoformat(),
                }

    return {
        "factory_health": {
            "overall_status": "alert" if degraded_count > 0 or offline_count > 0 else "nominal",
            "total_assets": total_assets,
            "operational_count": operational_count,
            "degraded_count": degraded_count,
            "offline_count": offline_count,
            "availability_pct": round((operational_count / max(1, total_assets)) * 100.0, 1),
        },
        "active_incidents_count": len(open_incidents),
        "active_incidents": [IncidentResponse.model_validate(inc) for inc in open_incidents],
        "key_asset_telemetry": motor_telemetry,
        "recent_simulations_count": len(recent_simulations),
        "recent_simulations": [
            {
                "id": s.id,
                "scenario_type": s.scenario_type,
                "delta_throughput": s.baseline_result.get("throughput_units_per_hour", 300) - s.scenario_result.get("throughput_units_per_hour", 300),
                "delta_cost": s.scenario_result.get("estimated_financial_cost", 0),
                "created_at": s.created_at.isoformat(),
            }
            for s in recent_simulations
        ],
    }
