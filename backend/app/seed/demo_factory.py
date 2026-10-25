import uuid
from datetime import datetime, timedelta, timezone
import random
from sqlalchemy.orm import Session
from app.infrastructure.db.models import (
    Asset,
    AssetEdge,
    TelemetryReading,
    Incident,
)
from app.core.logging import logger

# Deterministic UUIDs for demo assets to allow idempotent reseeding
DEMO_ASSETS = [
    {
        "id": "11111111-1111-1111-1111-111111111101",
        "name": "Raw Material Feeder F-01",
        "asset_type": "feeder",
        "location": "Bay A - Infeed",
        "criticality": 3.0,
        "status": "operational",
        "metadata_json": {
            "capacity_kg_h": 500,
            "nominal_throughput": 350,
            "manufacturer": "InduFeed Systems",
            "model": "IFS-500X",
            "installed_year": 2022,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111102",
        "name": "Drive Motor M-101",
        "asset_type": "motor",
        "location": "Bay A - Conveyor Drive Unit",
        "criticality": 4.5,
        "status": "degraded",  # Demo incident asset
        "metadata_json": {
            "rated_power_kw": 22.0,
            "rated_rpm": 1780,
            "bearing_type": "SKF-6312-DeepGroove",
            "manufacturer": "Vortex Drive Corp",
            "model": "VD-22K-IE4",
            "installed_year": 2021,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111103",
        "name": "Main Infeed Conveyor C-101",
        "asset_type": "conveyor",
        "location": "Bay A - Main Line",
        "criticality": 4.0,
        "status": "operational",
        "metadata_json": {
            "belt_length_m": 45.0,
            "belt_width_mm": 800,
            "nominal_speed_mps": 1.2,
            "manufacturer": "FlexFlow Conveying",
            "model": "FFC-800",
            "installed_year": 2021,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111104",
        "name": "Coolant Circulation Pump P-201",
        "asset_type": "pump",
        "location": "Bay B - Auxiliary Utilities",
        "criticality": 3.5,
        "status": "operational",
        "metadata_json": {
            "rated_flow_lpm": 60.0,
            "rated_pressure_bar": 5.5,
            "manufacturer": "HydraMech Fluidics",
            "model": "HM-60P",
            "installed_year": 2023,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111105",
        "name": "Precision CNC Station CNC-301",
        "asset_type": "cnc",
        "location": "Bay B - Machining Cell",
        "criticality": 5.0,
        "status": "operational",
        "metadata_json": {
            "max_spindle_rpm": 12000,
            "tool_slots": 24,
            "manufacturer": "Apex Precision Machinery",
            "model": "APX-5AX-300",
            "installed_year": 2020,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111106",
        "name": "Optical Quality Inspection INS-401",
        "asset_type": "inspection",
        "location": "Bay C - QA Testing",
        "criticality": 3.8,
        "status": "operational",
        "metadata_json": {
            "camera_resolution_mp": 24,
            "inspection_rate_ppm": 60,
            "manufacturer": "OptiVision Tech",
            "model": "OVT-4K-AI",
            "installed_year": 2023,
        },
    },
    {
        "id": "11111111-1111-1111-1111-111111111107",
        "name": "Robotic Packaging Cell PKG-501",
        "asset_type": "packaging",
        "location": "Bay C - End of Line",
        "criticality": 4.2,
        "status": "operational",
        "metadata_json": {
            "payload_capacity_kg": 25.0,
            "cycle_time_sec": 1.4,
            "manufacturer": "RoboPack Automation",
            "model": "RPA-25Delta",
            "installed_year": 2022,
        },
    },
]

DEMO_EDGES = [
    # Feeder feeds Conveyor
    {
        "source": "11111111-1111-1111-1111-111111111101",
        "target": "11111111-1111-1111-1111-111111111103",
        "relationship_type": "feeds",
        "weight": 1.0,
        "metadata_json": {"material": "aluminum_billets", "flow_capacity_kg_h": 400},
    },
    # Motor drives Conveyor
    {
        "source": "11111111-1111-1111-1111-111111111102",
        "target": "11111111-1111-1111-1111-111111111103",
        "relationship_type": "drives",
        "weight": 1.0,
        "metadata_json": {"coupling": "direct_shaft", "gear_ratio": 12.5},
    },
    # Coolant pump cools Motor
    {
        "source": "11111111-1111-1111-1111-111111111104",
        "target": "11111111-1111-1111-1111-111111111102",
        "relationship_type": "cools",
        "weight": 0.8,
        "metadata_json": {"loop": "secondary_glycol", "nominal_flow_lpm": 15},
    },
    # Coolant pump cools CNC Station
    {
        "source": "11111111-1111-1111-1111-111111111104",
        "target": "11111111-1111-1111-1111-111111111105",
        "relationship_type": "cools",
        "weight": 0.9,
        "metadata_json": {"loop": "primary_spindle_flood", "nominal_flow_lpm": 35},
    },
    # Conveyor feeds CNC Station
    {
        "source": "11111111-1111-1111-1111-111111111103",
        "target": "11111111-1111-1111-1111-111111111105",
        "relationship_type": "feeds",
        "weight": 1.0,
        "metadata_json": {"transfer": "pneumatic_transfer_table"},
    },
    # CNC Station feeds Inspection
    {
        "source": "11111111-1111-1111-1111-111111111105",
        "target": "11111111-1111-1111-1111-111111111106",
        "relationship_type": "feeds",
        "weight": 1.0,
        "metadata_json": {"transfer": "gravity_chute"},
    },
    # Inspection feeds Packaging
    {
        "source": "11111111-1111-1111-1111-111111111106",
        "target": "11111111-1111-1111-1111-111111111107",
        "relationship_type": "feeds",
        "weight": 1.0,
        "metadata_json": {"transfer": "diverter_belt"},
    },
]

DEMO_INCIDENT_ID = "22222222-2222-2222-2222-222222222201"


def seed_demo_factory(db: Session, random_seed: int = 42) -> None:
    random.seed(random_seed)
    logger.info("Seeding demo factory assets and dependency edges...")

    # 1. Upsert Assets
    for asset_data in DEMO_ASSETS:
        existing = db.query(Asset).filter(Asset.id == asset_data["id"]).first()
        if existing:
            for k, v in asset_data.items():
                setattr(existing, k, v)
        else:
            db.add(Asset(**asset_data))
    db.commit()

    # 2. Upsert Edges
    for edge_data in DEMO_EDGES:
        existing = (
            db.query(AssetEdge)
            .filter(
                AssetEdge.source_asset_id == edge_data["source"],
                AssetEdge.target_asset_id == edge_data["target"],
                AssetEdge.relationship_type == edge_data["relationship_type"],
            )
            .first()
        )
        if not existing:
            db.add(
                AssetEdge(
                    source_asset_id=edge_data["source"],
                    target_asset_id=edge_data["target"],
                    relationship_type=edge_data["relationship_type"],
                    weight=edge_data["weight"],
                    metadata_json=edge_data["metadata_json"],
                )
            )
    db.commit()

    # 3. Seed Telemetry History (Last 24 hours in 30-minute intervals)
    now = datetime.now(timezone.utc)
    motor_id = "11111111-1111-1111-1111-111111111102"
    pump_id = "11111111-1111-1111-1111-111111111104"
    conveyor_id = "11111111-1111-1111-1111-111111111103"
    cnc_id = "11111111-1111-1111-1111-111111111105"

    existing_readings_count = db.query(TelemetryReading).count()
    if existing_readings_count < 100:
        logger.info("Generating synthetic telemetry timeline...")
        readings = []
        for step in range(48, 0, -1):
            ts = now - timedelta(minutes=step * 30)

            # Motor M-101: Baseline normal operation transitioning to vibration spike & heat drift in last 4 hours (last 8 steps)
            if step <= 8:
                # Anomaly phase: vibration increases from 2.5 to 5.8 mm/s, temp drifts to 86 C
                factor = (9 - step) / 8.0
                vib = 2.1 + factor * 3.7 + random.gauss(0, 0.2)
                temp = 62.0 + factor * 24.5 + random.gauss(0, 0.4)
                power = 15.2 + factor * 3.8 + random.gauss(0, 0.3)
            else:
                # Normal baseline phase
                vib = 2.1 + random.gauss(0, 0.15)
                temp = 62.0 + random.gauss(0, 0.5)
                power = 15.2 + random.gauss(0, 0.2)

            readings.append(TelemetryReading(asset_id=motor_id, sensor_name="vibration", value=round(max(0.1, vib), 3), unit="mm/s", observed_at=ts, source="synthetic_sensor"))
            readings.append(TelemetryReading(asset_id=motor_id, sensor_name="temperature", value=round(temp, 2), unit="deg_C", observed_at=ts, source="synthetic_sensor"))
            readings.append(TelemetryReading(asset_id=motor_id, sensor_name="power_draw", value=round(power, 2), unit="kW", observed_at=ts, source="synthetic_sensor"))

            # Pump P-201 normal readings
            flow = 48.0 + random.gauss(0, 0.8)
            press = 4.2 + random.gauss(0, 0.08)
            readings.append(TelemetryReading(asset_id=pump_id, sensor_name="flow_rate", value=round(flow, 2), unit="L/min", observed_at=ts, source="synthetic_sensor"))
            readings.append(TelemetryReading(asset_id=pump_id, sensor_name="pressure", value=round(press, 2), unit="bar", observed_at=ts, source="synthetic_sensor"))

            # Conveyor C-101 normal readings
            speed = 1.2 + random.gauss(0, 0.02)
            readings.append(TelemetryReading(asset_id=conveyor_id, sensor_name="belt_speed", value=round(speed, 3), unit="m/s", observed_at=ts, source="synthetic_sensor"))

            # CNC-301 normal readings
            rpm = 3200 + random.gauss(0, 25)
            spindle_temp = 54.0 + random.gauss(0, 0.6)
            readings.append(TelemetryReading(asset_id=cnc_id, sensor_name="spindle_rpm", value=round(rpm, 1), unit="RPM", observed_at=ts, source="synthetic_sensor"))
            readings.append(TelemetryReading(asset_id=cnc_id, sensor_name="spindle_temp", value=round(spindle_temp, 2), unit="deg_C", observed_at=ts, source="synthetic_sensor"))

        db.bulk_save_objects(readings)
        db.commit()

    # 4. Seed Canonical Demo Incident
    existing_incident = db.query(Incident).filter(Incident.id == DEMO_INCIDENT_ID).first()
    if not existing_incident:
        logger.info("Seeding canonical demo incident for Drive Motor M-101...")
        incident = Incident(
            id=DEMO_INCIDENT_ID,
            asset_id=motor_id,
            title="Elevated Vibration & Thermal Runaway Pattern on Drive Motor M-101",
            description=(
                "Drive Motor M-101 exhibiting sustained vibration exceeding 5.2 mm/s (warning threshold 4.5 mm/s) "
                "with coincident drive-end winding temperature climbing to 86.5°C over the past 4 hours. "
                "Downstream Main Conveyor C-101 and CNC Station CNC-301 are at imminent risk of uncommanded stoppage."
            ),
            severity="high",
            status="open",
            trigger_type="telemetry_anomaly",
            detected_at=now - timedelta(minutes=45),
            context_json={
                "triggering_sensor": "vibration",
                "triggering_value": 5.82,
                "threshold": 4.5,
                "secondary_sensor": "temperature",
                "secondary_value": 86.5,
                "secondary_threshold": 80.0,
                "affected_downstream_assets": [conveyor_id, cnc_id],
            },
            is_synthetic=True,
        )
        db.add(incident)
        db.commit()

    logger.info("Demo factory seed complete.")
