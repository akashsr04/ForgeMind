from typing import Dict, Any, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss, f1_score
from app.ml.features import FEATURE_NAMES


class BaselineRiskPredictor:
    """
    Transparent linear/heuristic baseline risk predictor.
    Predicts asset anomaly/failure risk purely from node features without graph topology.
    """

    def __init__(self):
        self.model = LogisticRegression(class_weight="balanced", random_state=42, max_iter=200)
        self.is_fitted = False
        self.feature_weights: Dict[str, float] = {}

    def fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        self.model.fit(X, y)
        self.is_fitted = True

        coefs = self.model.coef_[0]
        self.feature_weights = {
            FEATURE_NAMES[i]: round(float(coefs[i]), 4)
            for i in range(min(len(FEATURE_NAMES), len(coefs)))
        }

        # Calculate train metrics
        probs = self.model.predict_proba(X)[:, 1]
        preds = (probs >= 0.5).astype(int)

        metrics = {
            "model_type": "LogisticRegressionBaseline",
            "features_used": len(FEATURE_NAMES),
            "top_features": sorted(self.feature_weights.items(), key=lambda x: abs(x[1]), reverse=True)[:5],
            "train_brier_score": round(float(brier_score_loss(y, probs)), 4),
            "train_f1": round(float(f1_score(y, preds, zero_division=0)), 4),
        }
        return metrics

    def predict_risk(self, x: np.ndarray) -> float:
        """
        Predicts anomaly risk score on [0.0, 1.0].
        If not fitted, uses transparent rule-based heuristic.
        """
        if self.is_fitted:
            x_2d = x.reshape(1, -1) if x.ndim == 1 else x
            prob = float(self.model.predict_proba(x_2d)[0, 1])
            return round(prob, 4)

        # Transparent heuristic fallback:
        # x[14] is rule-based anomaly indicator, x[10] is max vibration norm, x[12] is max temp norm
        score = 0.1
        if x.ndim == 1:
            if x[14] > 0.5:
                score += 0.5
            score += 0.25 * x[10] + 0.25 * x[12]
        return round(float(min(1.0, max(0.0, score))), 4)
