from typing import List, Dict, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session
from app.infrastructure.db.models import Asset, TelemetryReading

ASSET_TYPES = ["feeder", "motor", "conveyor", "pump", "cnc", "inspection", "packaging", "other"]

FEATURE_NAMES = [
    "type_feeder",
    "type_motor",
    "type_conveyor",
    "type_pump",
    "type_cnc",
    "type_inspection",
    "type_packaging",
    "type_other",
    "criticality_norm",
    "vibration_mean_norm",
    "vibration_max_norm",
    "temperature_mean_norm",
    "temperature_max_norm",
    "power_mean_norm",
    "sensor_anomaly_indicator",
    "sensor_missing_indicator",
]


def extract_node_features(asset: Asset, readings: List[TelemetryReading]) -> np.ndarray:
    """
    Extracts 16-dimensional standardized feature vector for an asset node:
    - 8 asset type one-hot indicators
    - 1 normalized criticality score [0, 1]
    - 5 normalized telemetry statistics (vibration, temperature, power)
    - 1 rule-based anomaly flag
    - 1 missingness indicator
    """
    vec = np.zeros(len(FEATURE_NAMES), dtype=np.float32)

    # 1. One-hot asset type
    atype = asset.asset_type.lower()
    if atype in ASSET_TYPES:
        vec[ASSET_TYPES.index(atype)] = 1.0
    else:
        vec[ASSET_TYPES.index("other")] = 1.0

    # 2. Criticality (1.0 to 5.0 -> 0.0 to 1.0)
    crit = float(asset.criticality or 1.0)
    vec[8] = np.clip((crit - 1.0) / 4.0, 0.0, 1.0)

    # 3. Telemetry aggregations
    sensor_map: Dict[str, List[float]] = {}
    for r in readings:
        sensor_map.setdefault(r.sensor_name.lower(), []).append(r.value)

    # Missing indicator
    if not sensor_map:
        vec[15] = 1.0  # missing sensor data
        return vec

    # Vibration: baseline ~2.0, threshold 4.5, max 10.0
    vib_vals = sensor_map.get("vibration", [])
    if vib_vals:
        vec[9] = float(np.clip(np.mean(vib_vals) / 10.0, 0.0, 1.0))
        vec[10] = float(np.clip(np.max(vib_vals) / 10.0, 0.0, 1.0))

    # Temperature: baseline ~60, threshold 82, max 120.0
    temp_vals = sensor_map.get("temperature", [])
    if temp_vals:
        vec[11] = float(np.clip(np.mean(temp_vals) / 120.0, 0.0, 1.0))
        vec[12] = float(np.clip(np.max(temp_vals) / 120.0, 0.0, 1.0))

    # Power draw: baseline ~15, max 30.0
    power_vals = sensor_map.get("power_draw", [])
    if power_vals:
        vec[13] = float(np.clip(np.mean(power_vals) / 30.0, 0.0, 1.0))

    # Rule-based threshold anomaly flag
    is_anomaly = False
    if vib_vals and np.max(vib_vals) > 4.5:
        is_anomaly = True
    if temp_vals and np.max(temp_vals) > 80.0:
        is_anomaly = True

    vec[14] = 1.0 if is_anomaly else 0.0
    return vec
