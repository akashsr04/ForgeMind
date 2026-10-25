import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { Asset, SimulationResult } from '../../types';
import {
  Cpu,
  Play,
  ArrowRight,
  TrendingDown,
  DollarSign,
  Clock,
  Layers,
  AlertOctagon,
  CheckCircle2,
} from 'lucide-react';

interface DigitalTwinLabViewProps {
  initialAssetId?: string | null;
  initialScenarioType?: string | null;
}

export const DigitalTwinLabView: React.FC<DigitalTwinLabViewProps> = ({
  initialAssetId,
  initialScenarioType,
}) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [targetAssetId, setTargetAssetId] = useState<string>(
    initialAssetId || '11111111-1111-1111-1111-111111111102'
  );
  const [scenarioType, setScenarioType] = useState<string>(initialScenarioType || 'derating');
  const [durationMinutes, setDurationMinutes] = useState<number>(60);
  const [deratingFactor, setDeratingFactor] = useState<number>(0.5);
  const [repairCost, setRepairCost] = useState<number>(450);
  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    async function loadAssets() {
      try {
        const list = await api.getAssets();
        setAssets(list);
      } catch (err) {
        console.error('Failed to load assets', err);
      }
    }
    loadAssets();
  }, []);

  useEffect(() => {
    handleRunSimulation();
  }, [targetAssetId, scenarioType]);

  async function handleRunSimulation() {
    if (!targetAssetId) return;
    setLoading(true);
    try {
      const res = await api.runSimulation({
        target_asset_id: targetAssetId,
        scenario_type: scenarioType,
        duration_minutes: durationMinutes,
        derating_factor: deratingFactor,
        repair_cost_estimate: repairCost,
      });
      setSimResult(res);
    } catch (err) {
      console.error('Failed to run simulation', err);
    } finally {
      setLoading(false);
    }
  }

  const selectedAsset = assets.find((a) => a.id === targetAssetId);

  return (
    <div>
      {/* Simulation Controls Panel */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <Cpu size={18} color="var(--accent-cyan)" />
          <span>Scenario Builder & What-If Parameters</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', alignItems: 'flex-end' }}>
          {/* Target Asset */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
              TARGET ASSET
            </label>
            <select
              value={targetAssetId}
              onChange={(e) => setTargetAssetId(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--bg-main)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '8px 12px',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.asset_type})
                </option>
              ))}
            </select>
          </div>

          {/* Scenario Type */}
          <div>
            <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>
              SCENARIO INTERVENTION
            </label>
            <select
              value={scenarioType}
              onChange={(e) => setScenarioType(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--bg-main)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '8px 12px',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            >
              <option value="derating">Production Derating (Load Shedding)</option>
              <option value="outage">Unplanned Outage / Immediate Stoppage</option>
              <option value="inspection">Planned Ultrasound & Thermal Inspection</option>
              <option value="repair">Full Component Repair / Overhaul</option>
            </select>
          </div>

          {/* Duration Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>HORIZON</label>
              <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                {durationMinutes} min
              </span>
            </div>
            <input
              type="range"
              min="15"
              max="240"
              step="15"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(Number(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
            />
          </div>

          {/* Derating Factor (if derating) */}
          {scenarioType === 'derating' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>CAPACITY</label>
                <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--accent-amber)' }}>
                  {(deratingFactor * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.1"
                value={deratingFactor}
                onChange={(e) => setDeratingFactor(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-amber)' }}
              />
            </div>
          )}

          {/* Run Button */}
          <div>
            <button
              className="btn btn-primary"
              onClick={handleRunSimulation}
              disabled={loading}
              style={{ width: '100%', padding: '9px' }}
            >
              <Play size={15} />
              {loading ? 'Evaluating Model...' : 'Simulate Intervention'}
            </button>
          </div>
        </div>
      </div>

      {simResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Side-by-Side Comparison Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Baseline Card */}
            <div className="card" style={{ borderTop: '3px solid var(--accent-emerald)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--accent-emerald)' }}>
                  Baseline Factory State
                </span>
                <span className="pill pill-operational">Nominal</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Bottleneck Throughput</span>
                  <span className="mono" style={{ fontWeight: 700, fontSize: '1.2rem', color: '#fff' }}>
                    {simResult.baseline.throughput_units_per_hour} <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>u/h</span>
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Factory Operating Capacity</span>
                  <span className="mono" style={{ fontWeight: 600 }}>
                    {simResult.baseline.total_factory_capacity_pct}%
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Production Downtime</span>
                  <span className="mono" style={{ fontWeight: 600 }}>
                    {simResult.baseline.estimated_downtime_hours} hrs
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Financial Cost Incurred</span>
                  <span className="mono" style={{ fontWeight: 600 }}>
                    ${simResult.baseline.estimated_financial_cost.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {/* Scenario Card */}
            <div className="card" style={{ borderTop: '3px solid var(--accent-cyan)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--accent-cyan)' }}>
                  Intervention: {simResult.scenario_type.toUpperCase()}
                </span>
                <span className="pill pill-degraded">Simulated</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Projected Throughput</span>
                  <span className="mono" style={{ fontWeight: 700, fontSize: '1.2rem', color: 'var(--accent-cyan)' }}>
                    {simResult.scenario.throughput_units_per_hour} <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>u/h</span>
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Effective Capacity</span>
                  <span className="mono" style={{ fontWeight: 600 }}>
                    {simResult.scenario.total_factory_capacity_pct}%
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '8px' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Lost Production Time</span>
                  <span className="mono" style={{ fontWeight: 600, color: 'var(--accent-amber)' }}>
                    {simResult.scenario.estimated_downtime_hours} hrs
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Total Financial Impact</span>
                  <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-rose)' }}>
                    ${simResult.scenario.estimated_financial_cost.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Impact Deltas Summary */}
          <div className="stat-grid">
            <div className="stat-card">
              <div className="stat-header">THROUGHPUT DELTA</div>
              <div className="stat-value" style={{ color: simResult.delta_throughput < 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
                {simResult.delta_throughput > 0 ? `+${simResult.delta_throughput}` : simResult.delta_throughput} u/h
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-header">LOST DOWNTIME</div>
              <div className="stat-value" style={{ color: 'var(--accent-amber)' }}>
                +{simResult.delta_downtime_hours} hrs
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-header">TOTAL INTERVENTION COST</div>
              <div className="stat-value" style={{ color: 'var(--accent-rose)' }}>
                ${simResult.delta_cost.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Cascade & Assumptions */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Propagation Path */}
            <div className="card">
              <div className="card-title">
                <Layers size={16} color="var(--accent-purple)" />
                <span>Downstream Dependency Impact ({simResult.affected_asset_ids.length} Assets)</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {simResult.propagation_path.map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      background: 'var(--bg-main)',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                    }}
                  >
                    <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                      0{idx + 1}
                    </span>
                    <span style={{ color: '#fff' }}>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Assumptions & Disclaimers */}
            <div className="card">
              <div className="card-title">
                <CheckCircle2 size={16} color="var(--accent-emerald)" />
                <span>Simulation Physics Assumptions</span>
              </div>

              <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
                {simResult.assumptions.map((asm, i) => (
                  <li key={i}>{asm}</li>
                ))}
              </ul>

              <div style={{ marginTop: '20px', padding: '10px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.03)', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                Simulated estimate generated by ForgeMind discrete-event digital twin model. Not a certified industrial forecast.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
