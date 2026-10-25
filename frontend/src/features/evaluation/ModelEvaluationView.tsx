import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { ModelMetrics } from '../../types';
import {
  LineChart,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Info,
  Layers,
  Activity,
} from 'lucide-react';

export const ModelEvaluationView: React.FC = () => {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMetrics() {
      try {
        const data = await api.getModelEvaluation();
        setMetrics(data);
      } catch (err) {
        console.error('Failed to load model metrics', err);
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, []);

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
        <div>Loading Model Card & Evaluation Statistics...</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
        No evaluation artifact found.
      </div>
    );
  }

  return (
    <div>
      {/* Top Stat Summary Grid */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span>GNN AUROC SCORE</span>
            <Activity size={16} color="var(--accent-cyan)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-cyan)' }}>
            {(metrics.gnn_model.auroc * 100).toFixed(1)}%
          </div>
          <div className="stat-sub">Held-out test set (63 samples)</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>CONFORMAL COVERAGE</span>
            <ShieldCheck size={16} color="var(--accent-emerald)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-emerald)' }}>
            {(metrics.uncertainty_evaluation.empirical_coverage_achieved * 100).toFixed(1)}%
          </div>
          <div className="stat-sub">Target: 90.0% nominal coverage</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>BRIER CALIBRATION SCORE</span>
            <LineChart size={16} color="var(--accent-purple)" />
          </div>
          <div className="stat-value" style={{ color: 'var(--accent-purple)' }}>
            {metrics.uncertainty_evaluation.brier_score_calibration.toFixed(3)}
          </div>
          <div className="stat-sub">0.0 = perfect probabilistic calibration</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>SYNTHETIC SAMPLES</span>
            <Layers size={16} color="var(--accent-amber)" />
          </div>
          <div className="stat-value">{metrics.dataset.total_instances}</div>
          <div className="stat-sub">70% train · 15% val · 15% test split</div>
        </div>
      </div>

      {/* Baseline vs GNN Comparison Table */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <LineChart size={18} color="var(--accent-cyan)" />
          <span>Model Architecture Comparison: Tabular Baseline vs Graph Neural Network</span>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>AUROC</th>
                <th>Accuracy</th>
                <th>F1 Score</th>
                <th>Brier Score</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600 }}>{metrics.baseline_model.model_name}</td>
                <td className="mono" style={{ color: 'var(--accent-cyan)' }}>
                  {(metrics.baseline_model.auroc * 100).toFixed(1)}%
                </td>
                <td className="mono">{metrics.baseline_model.accuracy.toFixed(3)}</td>
                <td className="mono">{metrics.baseline_model.f1_score.toFixed(3)}</td>
                <td className="mono">{metrics.baseline_model.brier_score.toFixed(3)}</td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                  {metrics.baseline_model.description}
                </td>
              </tr>
              <tr style={{ background: 'rgba(6, 182, 212, 0.04)' }}>
                <td style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                  {metrics.gnn_model.model_name}
                </td>
                <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>
                  {(metrics.gnn_model.auroc * 100).toFixed(1)}%
                </td>
                <td className="mono" style={{ fontWeight: 600 }}>{metrics.gnn_model.accuracy.toFixed(3)}</td>
                <td className="mono" style={{ fontWeight: 600 }}>{metrics.gnn_model.f1_score.toFixed(3)}</td>
                <td className="mono" style={{ fontWeight: 600 }}>{metrics.gnn_model.brier_score.toFixed(3)}</td>
                <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {metrics.gnn_model.description}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Uncertainty & Conformal Calibration Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <div className="card">
          <div className="card-title">
            <ShieldCheck size={18} color="var(--accent-emerald)" />
            <span>Split-Conformal Uncertainty Calibration</span>
          </div>
          <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            <p style={{ marginBottom: '10px' }}>
              Rather than presenting raw neural sigmoid activations as calibrated probabilities, ForgeMind uses
              <strong> Split-Conformal Prediction</strong> to construct finite-sample predictive intervals with proven coverage guarantees:
            </p>
            <div style={{ background: 'var(--bg-main)', padding: '12px', borderRadius: '8px', marginBottom: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Nominal Coverage Target:</span>
                <span className="mono" style={{ fontWeight: 600 }}>{(metrics.uncertainty_evaluation.nominal_coverage_target * 100).toFixed(0)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Empirical Test Coverage:</span>
                <span className="mono" style={{ fontWeight: 600, color: 'var(--accent-emerald)' }}>
                  {(metrics.uncertainty_evaluation.empirical_coverage_achieved * 100).toFixed(1)}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Nonconformity Quantile (q_hat):</span>
                <span className="mono" style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                  ±{metrics.uncertainty_evaluation.interval_half_width_q_hat.toFixed(3)}
                </span>
              </div>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
              Under exchangeability, test nonconformity scores are guaranteed to fall within the predictive set with probability 1 - α.
            </p>
          </div>
        </div>

        {/* Stated Limitations and Ethical Scope */}
        <div className="card">
          <div className="card-title">
            <AlertTriangle size={18} color="var(--accent-amber)" />
            <span>Stated Limitations & Ethical Scope</span>
          </div>

          <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
            {metrics.limitations_and_caveats.map((lim, i) => (
              <li key={i}>{lim}</li>
            ))}
          </ul>

          <div style={{ marginTop: '16px', padding: '10px', borderRadius: '6px', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.2)', fontSize: '0.75rem', color: '#fda4af' }}>
            Advisory decision-support prototype. Prohibited from issuing real machine-control commands.
          </div>
        </div>
      </div>
    </div>
  );
};
