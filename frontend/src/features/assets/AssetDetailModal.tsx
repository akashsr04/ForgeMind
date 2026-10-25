import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { Asset, AssetTelemetryData } from '../../types';
import { X, Activity, GitCommit, AlertTriangle, ShieldCheck } from 'lucide-react';

interface AssetDetailModalProps {
  assetId: string;
  onClose: () => void;
  onInvestigateIncident: (incidentId: string) => void;
}

export const AssetDetailModal: React.FC<AssetDetailModalProps> = ({
  assetId,
  onClose,
  onInvestigateIncident,
}) => {
  const [asset, setAsset] = useState<Asset | null>(null);
  const [neighbors, setNeighbors] = useState<any[]>([]);
  const [telemetry, setTelemetry] = useState<AssetTelemetryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [a, n, t] = await Promise.all([
          api.getAsset(assetId),
          api.getAssetNeighbors(assetId),
          api.getAssetTelemetry(assetId, 24),
        ]);
        setAsset(a);
        setNeighbors(n.neighbors || []);
        setTelemetry(t);
      } catch (err) {
        console.error('Failed to load asset detail', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [assetId]);

  if (!asset && loading) {
    return (
      <div className="modal-overlay">
        <div className="modal-content" style={{ textAlign: 'center', padding: '60px' }}>
          <div>Loading asset telemetry...</div>
        </div>
      </div>
    );
  }

  if (!asset) return null;

  const vibReadings = telemetry?.readings.filter((r) => r.sensor_name === 'vibration') || [];
  const tempReadings = telemetry?.readings.filter((r) => r.sensor_name === 'temperature') || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '850px' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <span className={`pill pill-${asset.status}`}>{asset.status}</span>
              <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                ID: {asset.id.slice(0, 8)}...
              </span>
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>{asset.name}</h2>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              {asset.asset_type.toUpperCase()} · Location: {asset.location || 'Factory Floor'} · Criticality: {asset.criticality}/5.0
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}
          >
            <X size={22} />
          </button>
        </div>

        {/* Telemetry Chart Section */}
        <div className="card" style={{ marginBottom: '20px', background: 'var(--bg-main)' }}>
          <div className="card-title">
            <Activity size={16} color="var(--accent-cyan)" />
            <span>24-Hour Sensor Telemetry History</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Vibration Mini Sparkline */}
            <div style={{ background: 'var(--bg-card)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Vibration (mm/s)</span>
                <span className="mono" style={{ fontWeight: 600, color: 'var(--accent-rose)' }}>
                  {telemetry?.summaries?.vibration?.current_value ?? '--'} mm/s
                </span>
              </div>
              <svg viewBox="0 0 300 60" style={{ width: '100%', height: '60px' }}>
                <polyline
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="2"
                  points={
                    vibReadings.length > 0
                      ? vibReadings
                          .map((r, i) => `${(i / (vibReadings.length - 1)) * 300},${60 - Math.min(55, (r.value / 8.0) * 55)}`)
                          .join(' ')
                      : '0,50 300,50'
                  }
                />
              </svg>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'flex', justifyContent: 'space-between' }}>
                <span>Mean: {telemetry?.summaries?.vibration?.mean_value ?? '--'}</span>
                <span>Max: {telemetry?.summaries?.vibration?.max_value ?? '--'}</span>
              </div>
            </div>

            {/* Temperature Mini Sparkline */}
            <div style={{ background: 'var(--bg-card)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Temperature (°C)</span>
                <span className="mono" style={{ fontWeight: 600, color: 'var(--accent-amber)' }}>
                  {telemetry?.summaries?.temperature?.current_value ?? '--'} °C
                </span>
              </div>
              <svg viewBox="0 0 300 60" style={{ width: '100%', height: '60px' }}>
                <polyline
                  fill="none"
                  stroke="#f59e0b"
                  strokeWidth="2"
                  points={
                    tempReadings.length > 0
                      ? tempReadings
                          .map((r, i) => `${(i / (tempReadings.length - 1)) * 300},${60 - Math.min(55, ((r.value - 40) / 70.0) * 55)}`)
                          .join(' ')
                      : '0,50 300,50'
                  }
                />
              </svg>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', display: 'flex', justifyContent: 'space-between' }}>
                <span>Mean: {telemetry?.summaries?.temperature?.mean_value ?? '--'}</span>
                <span>Max: {telemetry?.summaries?.temperature?.max_value ?? '--'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Connected Neighbors */}
        <div className="card" style={{ marginBottom: '20px', background: 'var(--bg-main)' }}>
          <div className="card-title">
            <GitCommit size={16} color="var(--accent-emerald)" />
            <span>Operational Graph Topology Neighbors</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {neighbors.map((nb, i) => (
              <div
                key={i}
                style={{
                  background: 'var(--bg-card)',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{nb.asset.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    Type: {nb.asset.asset_type} · {nb.direction}
                  </div>
                </div>
                <span className="mono" style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '4px' }}>
                  {nb.relationship_type}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Specs from Metadata */}
        {asset.metadata_json && Object.keys(asset.metadata_json).length > 0 && (
          <div className="card" style={{ background: 'var(--bg-main)' }}>
            <div className="card-title">
              <ShieldCheck size={16} color="var(--accent-purple)" />
              <span>Asset Equipment Specifications</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
              {Object.entries(asset.metadata_json).map(([k, v]) => (
                <div key={k} style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: '6px' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                    {k.replace(/_/g, ' ')}
                  </div>
                  <div className="mono" style={{ fontSize: '0.85rem', fontWeight: 600 }}>{String(v)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
