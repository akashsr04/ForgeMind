import React from 'react';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Gauge,
  Thermometer,
  Zap,
} from 'lucide-react';
import { Incident } from '../../types';

interface OverviewViewProps {
  overviewData: any;
  onInvestigateIncident: (incidentId: string) => void;
  onInspectAsset: (assetId: string) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  overviewData,
  onInvestigateIncident,
  onInspectAsset,
}) => {
  const health = overviewData?.factory_health || {
    overall_status: 'nominal',
    total_assets: 7,
    operational_count: 6,
    degraded_count: 1,
    offline_count: 0,
    availability_pct: 85.7,
  };

  const incidents: Incident[] = overviewData?.active_incidents || [];
  const telemetry = overviewData?.key_asset_telemetry || {};
  const simulations = overviewData?.recent_simulations || [];

  return (
    <div>
      {/* Top Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-header">
            <span>FACTORY AVAILABILITY</span>
            <Activity size={16} color="var(--accent-cyan)" />
          </div>
          <div className="stat-value">{health.availability_pct}%</div>
          <div className="stat-sub">
            {health.operational_count} of {health.total_assets} assets nominal
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>ACTIVE INCIDENTS</span>
            <AlertTriangle size={16} color={health.degraded_count > 0 ? "var(--accent-rose)" : "var(--accent-emerald)"} />
          </div>
          <div className="stat-value" style={{ color: incidents.length > 0 ? 'var(--accent-rose)' : '#fff' }}>
            {overviewData?.active_incidents_count ?? incidents.length}
          </div>
          <div className="stat-sub">
            {health.degraded_count} degraded · {health.offline_count} offline
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>LINE BOTTLENECK RATE</span>
            <Gauge size={16} color="var(--accent-amber)" />
          </div>
          <div className="stat-value">300 <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>u/h</span></div>
          <div className="stat-sub">Constrained by Precision CNC-301</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <span>DIGITAL TWIN STATUS</span>
            <CheckCircle2 size={16} color="var(--accent-emerald)" />
          </div>
          <div className="stat-value" style={{ fontSize: '1.2rem', paddingTop: '6px' }}>Synchronized</div>
          <div className="stat-sub">{simulations.length} what-if scenarios evaluated</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
        {/* Active Incidents Panel */}
        <div className="card">
          <div className="card-title">
            <AlertTriangle size={18} color="var(--accent-amber)" />
            <span>Active Incident Triage</span>
          </div>

          {incidents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-dim)' }}>
              <CheckCircle2 size={36} color="var(--accent-emerald)" style={{ margin: '0 auto 12px' }} />
              <div>All factory assets operating within nominal design tolerances.</div>
              <div style={{ fontSize: '0.8rem', marginTop: '6px' }}>Use "Trigger Demo Incident" to simulate an alert.</div>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Incident Title</th>
                    <th>Trigger</th>
                    <th>Detected</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((inc) => (
                    <tr key={inc.id}>
                      <td>
                        <span className={`pill pill-${inc.severity}`}>
                          {inc.severity}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{inc.title}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', maxWidth: '380px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {inc.description}
                        </div>
                      </td>
                      <td>
                        <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {inc.trigger_type}
                        </span>
                      </td>
                      <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                        {new Date(inc.detected_at).toLocaleTimeString()}
                      </td>
                      <td>
                        <button
                          className="btn btn-primary"
                          style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                          onClick={() => onInvestigateIncident(inc.id)}
                        >
                          Investigate <ArrowRight size={13} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Target Asset Live Telemetry (Drive Motor M-101) */}
        <div className="card">
          <div className="card-title">
            <Activity size={18} color="var(--accent-cyan)" />
            <span>Drive Motor M-101 Telemetry</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ background: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Drive-End Vibration</span>
                <span className="mono" style={{ color: (telemetry.vibration?.value || 0) > 4.5 ? 'var(--accent-rose)' : 'var(--accent-emerald)', fontWeight: 600 }}>
                  {telemetry.vibration?.value ?? 5.82} mm/s
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#243048', borderRadius: '3px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${Math.min(100, ((telemetry.vibration?.value || 5.82) / 8.0) * 100)}%`,
                    height: '100%',
                    background: (telemetry.vibration?.value || 0) > 4.5 ? 'var(--accent-rose)' : 'var(--accent-emerald)',
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                Warning threshold: 4.5 mm/s (ISO 10816 Class II)
              </div>
            </div>

            <div style={{ background: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Winding Temperature</span>
                <span className="mono" style={{ color: (telemetry.temperature?.value || 0) > 80 ? 'var(--accent-amber)' : 'var(--accent-emerald)', fontWeight: 600 }}>
                  {telemetry.temperature?.value ?? 86.5}°C
                </span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#243048', borderRadius: '3px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${Math.min(100, ((telemetry.temperature?.value || 86.5) / 110.0) * 100)}%`,
                    height: '100%',
                    background: (telemetry.temperature?.value || 0) > 80 ? 'var(--accent-amber)' : 'var(--accent-emerald)',
                    transition: 'width 0.3s ease',
                  }}
                />
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                Thermal limit: 80.0°C
              </div>
            </div>

            <div style={{ background: 'var(--bg-main)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Active Power Draw</span>
                <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>
                  {telemetry.power_draw?.value ?? 18.4} kW
                </span>
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                Rated: 22.0 kW (Vortex Drive Corp VD-22K-IE4)
              </div>
            </div>

            <button
              className="btn btn-secondary"
              style={{ width: '100%', fontSize: '0.8rem', padding: '8px' }}
              onClick={() => onInspectAsset('11111111-1111-1111-1111-111111111102')}
            >
              Open Full Asset Diagnostics
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
