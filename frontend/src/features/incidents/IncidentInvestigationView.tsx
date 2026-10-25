import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Incident, StructuredInvestigation } from '../../types';
import {
  AlertTriangle,
  Play,
  RotateCw,
  FileText,
  CheckCircle,
  HelpCircle,
  Clock,
  ArrowRight,
  TrendingDown,
  Layers,
  ShieldAlert,
} from 'lucide-react';

interface IncidentInvestigationViewProps {
  initialIncidentId?: string | null;
  onNavigateToSimulation: (assetId: string, actionType: string) => void;
}

export const IncidentInvestigationView: React.FC<IncidentInvestigationViewProps> = ({
  initialIncidentId,
  onNavigateToSimulation,
}) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(initialIncidentId || null);
  const [investigation, setInvestigation] = useState<StructuredInvestigation | null>(null);
  const [loading, setLoading] = useState(false);
  const [runningWorkflow, setRunningWorkflow] = useState(false);

  useEffect(() => {
    async function loadIncidents() {
      try {
        const list = await api.getIncidents();
        setIncidents(list);
        if (!selectedIncidentId && list.length > 0) {
          setSelectedIncidentId(list[0].id);
        }
      } catch (err) {
        console.error('Failed to load incidents', err);
      }
    }
    loadIncidents();
  }, []);

  useEffect(() => {
    if (selectedIncidentId) {
      loadInvestigation(selectedIncidentId);
    }
  }, [selectedIncidentId]);

  async function loadInvestigation(incId: string) {
    setLoading(true);
    try {
      // Auto-run investigation if not yet generated
      const result = await api.triggerInvestigation(incId);
      setInvestigation(result);
    } catch (err) {
      console.error('Failed to load/run investigation', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleRerun() {
    if (!selectedIncidentId) return;
    setRunningWorkflow(true);
    try {
      const result = await api.triggerInvestigation(selectedIncidentId);
      setInvestigation(result);
    } catch (err) {
      console.error('Failed to rerun investigation', err);
    } finally {
      setRunningWorkflow(false);
    }
  }

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId);

  return (
    <div>
      {/* Incident Selector Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Active Incident:</span>
          <select
            value={selectedIncidentId || ''}
            onChange={(e) => setSelectedIncidentId(e.target.value)}
            style={{
              background: 'var(--bg-card)',
              color: 'var(--text-main)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px 14px',
              fontSize: '0.88rem',
              outline: 'none',
              maxWidth: '420px',
            }}
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.id}>
                [{inc.severity.toUpperCase()}] {inc.title}
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRerun}
          disabled={runningWorkflow || loading}
          style={{ padding: '8px 16px', fontSize: '0.84rem' }}
        >
          <RotateCw size={14} className={runningWorkflow ? 'spin' : ''} />
          {runningWorkflow ? 'Running LangGraph Workflow...' : 'Re-run Agent Investigation'}
        </button>
      </div>

      {loading && !investigation ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
          <RotateCw size={32} className="spin" color="var(--accent-cyan)" style={{ margin: '0 auto 16px' }} />
          <div style={{ fontWeight: 600 }}>Executing Bounded LangGraph Investigation Pipeline...</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '6px' }}>
            Collecting telemetry summaries → Estimating risk & conformal intervals → Querying Qdrant vectors → Synthesizing hypotheses
          </div>
        </div>
      ) : !investigation ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          No investigation available for selected incident. Click "Re-run Agent Investigation".
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Executive Diagnostic Summary Banner */}
          <div
            style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(37, 99, 235, 0.08))',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              borderRadius: '12px',
              padding: '20px 24px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className={`pill pill-${investigation.status === 'completed' ? 'operational' : 'degraded'}`}>
                  {investigation.status}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Workflow Engine: LangGraph Deterministic State Graph (v1.0.0)
                </span>
              </div>
              <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                ID: {investigation.investigation_id.slice(0, 8)}...
              </span>
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 600, color: '#ffffff', lineHeight: 1.5 }}>
              {investigation.summary}
            </div>
          </div>

          {/* Section: Risk & Uncertainty Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
            {/* Risk Gauge Card */}
            <div className="card">
              <div className="card-title">
                <AlertTriangle size={18} color="var(--accent-rose)" />
                <span>Operational Risk & Confidence</span>
              </div>

              <div style={{ textAlign: 'center', padding: '16px 0' }}>
                <div style={{ fontSize: '2.8rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--accent-rose)' }}>
                  {(investigation.risk.risk_score * 100).toFixed(0)}%
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                  Model Anomaly Risk Score
                </div>

                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'var(--bg-main)', padding: '6px 14px', borderRadius: '20px', border: '1px solid var(--border-subtle)', marginBottom: '16px' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Reliability:</span>
                  <span className={`pill pill-${investigation.risk.reliability_status}`}>
                    {investigation.risk.reliability_status}
                  </span>
                </div>

                {/* Conformal Uncertainty Interval */}
                <div style={{ background: 'var(--bg-main)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)', textAlign: 'left', fontSize: '0.78rem' }}>
                  <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Conformal Prediction Interval (90% Coverage):
                  </div>
                  <div className="mono" style={{ fontWeight: 600, color: 'var(--accent-cyan)' }}>
                    [{((investigation.risk.uncertainty.lower || 0) * 100).toFixed(0)}% — {((investigation.risk.uncertainty.upper || 1) * 100).toFixed(0)}%]
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                    Method: {investigation.risk.uncertainty.method}
                  </div>
                </div>
              </div>
            </div>

            {/* Diagnostic Hypotheses & Evidence Citations */}
            <div className="card">
              <div className="card-title">
                <FileText size={18} color="var(--accent-cyan)" />
                <span>Diagnostic Hypotheses & Evidence Citations</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {investigation.hypotheses.map((hypo, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'var(--bg-main)',
                      padding: '16px',
                      borderRadius: '8px',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                      <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{hypo.label}</div>
                      <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--accent-amber)', background: 'rgba(245, 158, 11, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                        {hypo.status.replace(/_/g, ' ')}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '10px', lineHeight: 1.4 }}>
                      {hypo.rationale}
                    </div>

                    {/* Cited Evidence Chunks */}
                    {hypo.supporting_evidence_refs.length > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
                        <span style={{ color: 'var(--text-dim)' }}>Supporting Citations:</span>
                        {hypo.supporting_evidence_refs.map((ref) => (
                          <span
                            key={ref}
                            className="mono"
                            style={{
                              background: 'rgba(6, 182, 212, 0.12)',
                              color: 'var(--accent-cyan)',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              border: '1px solid rgba(6, 182, 212, 0.25)',
                            }}
                          >
                            {ref}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section: Retrieved Maintenance Documentation Chunks */}
          <div className="card">
            <div className="card-title">
              <Layers size={18} color="var(--accent-purple)" />
              <span>Retrieved Maintenance Evidence (Qdrant Vector Engine)</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '14px' }}>
              {investigation.retrieved_evidence.map((chunk) => (
                <div
                  key={chunk.chunk_id}
                  style={{
                    background: 'var(--bg-main)',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                      {chunk.chunk_id}
                    </span>
                    <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                      Match: {((chunk.similarity_score || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem', marginBottom: '2px' }}>{chunk.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '8px' }}>
                    Section: {chunk.section} · Asset: {chunk.asset_type}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4, maxHeight: '110px', overflowY: 'auto' }}>
                    {chunk.content}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section: Ranked Candidate Maintenance Actions */}
          <div className="card">
            <div className="card-title">
              <CheckCircle size={18} color="var(--accent-emerald)" />
              <span>Ranked Candidate Actions (Multi-Criteria Decision Analysis)</span>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Action</th>
                    <th>Risk Reduction</th>
                    <th>Downtime</th>
                    <th>Direct Cost</th>
                    <th>Uncertainty Penalty</th>
                    <th>Net Score</th>
                    <th>Digital Twin</th>
                  </tr>
                </thead>
                <tbody>
                  {investigation.recommendations.map((action, idx) => (
                    <tr key={idx}>
                      <td className="mono" style={{ fontWeight: 700, color: idx === 0 ? 'var(--accent-emerald)' : 'var(--text-dim)' }}>
                        #{idx + 1}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{action.title}</div>
                        <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)' }}>{action.rationale}</div>
                      </td>
                      <td className="mono" style={{ color: 'var(--accent-emerald)' }}>
                        +{action.score_components.risk_reduction_term}
                      </td>
                      <td className="mono" style={{ color: 'var(--accent-amber)' }}>
                        {action.score_components.downtime_cost_term}
                      </td>
                      <td className="mono" style={{ color: 'var(--accent-rose)' }}>
                        {action.score_components.direct_cost_term}
                      </td>
                      <td className="mono" style={{ color: 'var(--text-dim)' }}>
                        {action.score_components.uncertainty_penalty_term}
                      </td>
                      <td className="mono" style={{ fontWeight: 700, fontSize: '1rem', color: action.net_score > 0 ? 'var(--accent-emerald)' : 'var(--text-dim)' }}>
                        {action.net_score.toFixed(1)}
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '5px 12px', fontSize: '0.75rem' }}
                          onClick={() => onNavigateToSimulation(selectedIncident?.asset_id || '', action.action_type)}
                        >
                          Simulate in Twin <ArrowRight size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Audit Trail Timeline */}
          <div className="card">
            <div className="card-title">
              <Clock size={18} color="var(--accent-cyan)" />
              <span>LangGraph Audit Trail Timeline ({investigation.audit_events.length} Steps)</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {investigation.audit_events.map((ev, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    padding: '8px 12px',
                    background: 'var(--bg-main)',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                  }}
                >
                  <span className="mono" style={{ color: 'var(--text-dim)', minWidth: '70px' }}>
                    {new Date(ev.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="mono" style={{ color: 'var(--accent-cyan)', minWidth: '160px' }}>
                    {ev.step}
                  </span>
                  <span style={{ color: 'var(--text-main)', flex: 1 }}>{ev.action}</span>
                  <span className="pill pill-operational" style={{ fontSize: '0.68rem', padding: '1px 6px' }}>
                    {ev.outcome}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Safety Disclaimer */}
          <div
            style={{
              padding: '12px 18px',
              borderRadius: '8px',
              background: 'rgba(244, 63, 94, 0.08)',
              border: '1px solid rgba(244, 63, 94, 0.2)',
              fontSize: '0.78rem',
              color: '#fda4af',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <ShieldAlert size={18} style={{ flexShrink: 0 }} />
            <span>{investigation.safety_disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
};
