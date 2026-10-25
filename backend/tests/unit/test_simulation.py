import pytest
from app.infrastructure.db.session import SessionLocal, init_db
from app.infrastructure.db.models import Asset, AssetEdge
from app.simulation.engine import DigitalTwinEngine


@pytest.fixture(scope="module")
def twin_engine():
    init_db()
    db = SessionLocal()
    assets = db.query(Asset).all()
    edges = db.query(AssetEdge).all()
    db.close()
    return DigitalTwinEngine(assets, edges)


def test_simulation_baseline_throughput(twin_engine):
    # Baseline with no interventions should achieve nominal 300 units/hr
    caps = {a_id: 1.0 for a_id in twin_engine.assets}
    metrics, bottlenecks = twin_engine.compute_factory_metrics(caps, duration_hours=1.0)
    assert metrics.throughput_units_per_hour == 300.0
    assert metrics.total_factory_capacity_pct == 100.0
    assert metrics.estimated_downtime_hours == 0.0
    assert "Precision CNC Station CNC-301" in bottlenecks


def test_simulation_motor_outage_propagation(twin_engine):
    # Motor M-101 outage should stop Conveyor C-101 and starve the line
    motor_id = "11111111-1111-1111-1111-111111111102"
    res = twin_engine.run_simulation(
        target_asset_id=motor_id,
        scenario_type="outage",
        duration_minutes=60.0,
    )
    assert res.scenario.throughput_units_per_hour == 0.0
    assert res.scenario.total_factory_capacity_pct == 0.0
    assert res.delta_throughput == -300.0
    assert res.scenario.estimated_downtime_hours == 1.0
    # Downstream conveyor and CNC should be marked in affected assets
    assert "11111111-1111-1111-1111-111111111103" in res.affected_asset_ids


def test_simulation_motor_derating(twin_engine):
    # Derating motor to 50% should reduce line throughput proportionally
    motor_id = "11111111-1111-1111-1111-111111111102"
    res = twin_engine.run_simulation(
        target_asset_id=motor_id,
        scenario_type="derating",
        duration_minutes=60.0,
        derating_factor=0.5,
    )
    # 50% of 320 = 160 units/hr
    assert res.scenario.throughput_units_per_hour == 160.0
    assert res.scenario.total_factory_capacity_pct == round((160.0 / 300.0) * 100.0, 1)
    assert res.scenario.estimated_downtime_hours > 0.0
