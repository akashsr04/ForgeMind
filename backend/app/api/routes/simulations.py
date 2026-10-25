import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Simulation, Asset, AssetEdge
from app.schemas.simulations import SimulationRequest, SimulationResponse
from app.simulation.engine import DigitalTwinEngine
from app.core.errors import ResourceNotFoundException

router = APIRouter(tags=["Digital Twin Simulation"])


@router.post("/simulations", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def run_simulation(
    req: SimulationRequest,
    db: Session = Depends(get_db),
):
    target_asset = db.query(Asset).filter(Asset.id == req.target_asset_id).first()
    if not target_asset:
        raise ResourceNotFoundException("Asset", req.target_asset_id)

    assets = db.query(Asset).all()
    edges = db.query(AssetEdge).all()

    engine = DigitalTwinEngine(assets=assets, edges=edges)
    sim_res = engine.run_simulation(
        target_asset_id=req.target_asset_id,
        scenario_type=req.scenario_type,
        duration_minutes=req.duration_minutes,
        derating_factor=req.derating_factor or 0.5,
        repair_cost_estimate=req.repair_cost_estimate or 500.0,
        incident_id=req.incident_id,
    )

    if req.persist_result:
        sim_id = str(uuid.uuid4())
        sim_res.id = sim_id
        sim_res.created_at = datetime.now(timezone.utc)

        db_sim = Simulation(
            id=sim_id,
            incident_id=req.incident_id,
            scenario_type=req.scenario_type,
            parameters=req.model_dump(mode="json"),
            baseline_result=sim_res.baseline.model_dump(mode="json"),
            scenario_result=sim_res.scenario.model_dump(mode="json"),
            assumptions={"notes": sim_res.assumptions},
            created_at=sim_res.created_at,
            is_synthetic=True,
        )
        db.add(db_sim)
        db.commit()

    return sim_res


@router.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str, db: Session = Depends(get_db)):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise ResourceNotFoundException("Simulation", simulation_id)

    target_id = sim.parameters.get("target_asset_id", "")
    duration = sim.parameters.get("duration_minutes", 60.0)

    delta_thr = sim.scenario_result.get("throughput_units_per_hour", 0) - sim.baseline_result.get("throughput_units_per_hour", 300)
    delta_cost = sim.scenario_result.get("estimated_financial_cost", 0) - sim.baseline_result.get("estimated_financial_cost", 0)
    delta_dt = sim.scenario_result.get("estimated_downtime_hours", 0) - sim.baseline_result.get("estimated_downtime_hours", 0)

    return SimulationResponse(
        id=sim.id,
        incident_id=sim.incident_id,
        target_asset_id=target_id,
        scenario_type=sim.scenario_type,
        duration_minutes=duration,
        baseline=sim.baseline_result,
        scenario=sim.scenario_result,
        delta_throughput=round(delta_thr, 1),
        delta_cost=round(delta_cost, 2),
        delta_downtime_hours=round(delta_dt, 2),
        affected_asset_ids=[target_id],
        propagation_path=[f"Asset {target_id}"],
        assumptions=sim.assumptions.get("notes", []),
        is_synthetic=sim.is_synthetic,
        created_at=sim.created_at,
    )
