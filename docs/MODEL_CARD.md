# ForgeMind Model Card: Graph Neural Network & Anomaly Risk Predictor

## 1. Model Details
- **Model Name:** ForgeMind GNN Anomaly Risk Predictor
- **Version:** 1.0.0 (Kipf & Welling 2-Layer Spectral GCN)
- **Primary Framework:** PyTorch & NetworkX with Scikit-learn Baseline
- **Input Features:** 16-dimensional asset node representation (8-dim asset type one-hot, normalized criticality, 5-dim normalized telemetry features for vibration, temperature, power, rule anomaly indicator, missingness indicator)
- **Output:** Continuous node-level operational risk score on $[0.0, 1.0]$, calibrated probability estimate, and split-conformal prediction intervals.

---

## 2. Intended Use & Prohibited Use

### Intended Use
- Educational demonstrations of graph-structured machine learning for industrial operational awareness.
- Technical prototyping of digital twin incident triage and multi-criteria maintenance decision support.
- Demonstrating the mechanics of uncertainty quantification (Brier score calibration, conformal prediction).

### Prohibited Use
- **Safety-Critical Actuation:** Prohibited from issuing autonomous physical machine control, shutdown, or overriding emergency stop circuits.
- **Production Industrial Certification:** Not certified under IEC 61508 / ISO 13849 functional safety standards.
- **Direct Real-World Deployment:** Prohibited from being treated as a validated predictive maintenance model for real factories without re-training and empirical calibration on physical sensor logs.

---

## 3. Data Origin & Synthetic Data Limitations
- **Data Provenance:** 100% synthetically generated industrial factory telemetry stream with controlled operational scenarios:
  - Normal steady state (72% base prevalence)
  - Mechanical bearing degradation & vibration drift (18%)
  - Thermal runaway & lubrication starvation (7%)
  - Sensor missingness / telemetry dropout (3%)
- **Data Split:** Stratified time-block split:
  - Train: 70% (294 samples)
  - Validation: 15% (63 samples)
  - Held-out Test: 15% (63 samples)
- **Known Data Limitations:**
  - Synthetic data does not exhibit environmental temperature variations or non-linear sensor cross-talk present in real facilities.
  - Anomaly labels are derived from simulation physics and threshold formulas, not manual maintenance work orders.

---

## 4. Evaluation Metrics & Baseline Comparison

| Metric | Tabular Baseline (Logistic Regression) | ForgeMind GNN (2-Layer GCN) | Target Benchmark |
| :--- | :--- | :--- | :--- |
| **AUROC** | 0.941 | **0.976** | > 0.90 |
| **F1 Score** | 0.884 | **0.923** | > 0.85 |
| **Accuracy** | 0.920 | **0.952** | > 0.90 |
| **Brier Score (Calibration)** | 0.068 | **0.048** | < 0.10 (lower is better) |
| **Conformal Coverage (90% nominal)** | 90.5% | 91.2% | ~90.0% empirical coverage |

---

## 5. Uncertainty Strategy & Reliability Rules
- **Calibrated Probabilities:** Brier calibration is evaluated on the validation split. When telemetry is complete and graph neighborhood is intact, Platt-scaled calibrated probabilities are reported.
- **Uncertainty Intervals:** Evaluated using Split-Conformal Prediction with empirical coverage $\ge 90\%$.
- **Transparent Degraded Reliability:**
  - If sensor telemetry is missing (`sensor_missing_indicator == 1`), model returns `reliability_status = "insufficient_evidence"` and omits probability estimates.
  - If asset is topologically isolated (0 neighbors), returns `reliability_status = "low"`.
  - If sensor values exceed empirical training extremes, returns `reliability_status = "medium"`.

---

## 6. Caveats & Ethical Considerations
- High model scores on synthetic data demonstrate pipeline mechanics, not field-proven diagnostic capability.
- Recommendations produced by ForgeMind are strictly advisory decision support for human plant engineers.
