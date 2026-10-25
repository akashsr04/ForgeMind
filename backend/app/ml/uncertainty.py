from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from app.schemas.common import RiskAssessment, UncertaintyDetail


def evaluate_brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """
    Computes Brier calibration score: mean((y_prob - y_true)^2).
    Lower is better calibrated (0.0 is perfect calibration, 0.25 is uninformative coin toss).
    """
    if len(y_true) == 0:
        return 0.0
    return float(np.mean((y_prob - y_true) ** 2))


def compute_conformal_interval(
    score: float,
    calibration_residuals: Optional[np.ndarray] = None,
    alpha: float = 0.10,  # 90% coverage
) -> Tuple[float, float, str]:
    """
    Computes Split-Conformal prediction interval for the risk estimate.
    Given nonconformity scores on validation set |y_true - score|, finds (1-alpha) quantile q_hat.
    Interval is [max(0, score - q_hat), min(1, score + q_hat)].
    """
    if calibration_residuals is not None and len(calibration_residuals) >= 20:
        n = len(calibration_residuals)
        q_idx = int(np.ceil((n + 1) * (1.0 - alpha))) - 1
        q_idx = min(max(0, q_idx), n - 1)
        sorted_residuals = np.sort(calibration_residuals)
        q_hat = float(sorted_residuals[q_idx])
        lower = max(0.0, score - q_hat)
        upper = min(1.0, score + q_hat)
        method = f"split_conformal_{int((1-alpha)*100)}pct_coverage"
    else:
        # Transparent empirical dispersion heuristic
        dispersion = 0.15
        lower = max(0.0, score - dispersion)
        upper = min(1.0, score + dispersion)
        method = "heuristic_dispersion_interval"

    return round(lower, 3), round(upper, 3), method


def assess_uncertainty_and_reliability(
    risk_score: float,
    node_features: Optional[np.ndarray] = None,
    calibration_residuals: Optional[np.ndarray] = None,
    neighbor_count: int = 1,
) -> RiskAssessment:
    """
    Synthesizes risk score, estimated calibrated probability, conformal uncertainty interval,
    and reliability classification with transparent limitations.
    """
    limitations: List[str] = [
        "Synthetic demo data; not calibrated against real operational factory logs.",
        "Exchangeability assumed under simulated drift conditions only.",
    ]

    has_missing_data = False
    is_extreme_value = False

    if node_features is not None:
        # Check missing sensor feature (index 15)
        if node_features[15] > 0.5:
            has_missing_data = True
            limitations.append("Recent sensor telemetry is sparse or missing.")
        # Check out-of-distribution values
        if node_features[9] > 0.9 or node_features[11] > 0.9:
            is_extreme_value = True

    if neighbor_count < 1:
        limitations.append("Isolated node with zero topology neighbors in factory graph.")

    # Determine reliability status
    if has_missing_data:
        reliability = "insufficient_evidence"
        explanation = "Telemetry history for this asset is incomplete or missing."
        calibrated_prob = None
    elif neighbor_count < 1:
        reliability = "low"
        explanation = "Asset is topologically isolated; graph contextual propagation is unavailable."
        calibrated_prob = round(risk_score * 0.9, 3)
    elif is_extreme_value:
        reliability = "medium"
        explanation = "Sensor values exceed typical empirical range; high leverage point."
        calibrated_prob = round(risk_score, 3)
    else:
        reliability = "high"
        explanation = "Full sensor history available; normal graph neighborhood connectivity."
        calibrated_prob = round(risk_score, 3)

    lower, upper, method = compute_conformal_interval(risk_score, calibration_residuals)

    uncertainty_detail = UncertaintyDetail(
        method=method,
        lower=lower,
        upper=upper,
        limitations=limitations,
    )

    return RiskAssessment(
        risk_score=round(risk_score, 3),
        estimated_probability=calibrated_prob,
        reliability_status=reliability,
        uncertainty=uncertainty_detail,
        explanation=explanation,
    )
