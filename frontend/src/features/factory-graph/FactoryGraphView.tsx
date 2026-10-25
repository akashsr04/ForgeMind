import React, { useState, useMemo } from 'react';
import { FactoryGraphData, GraphNode, GraphEdge } from '../../types';
import { Filter, Layers, Info, CheckCircle2, AlertTriangle, XCircle, ArrowRight } from 'lucide-react';

interface FactoryGraphViewProps {
  graphData: FactoryGraphData | null;
  onSelectNode: (assetId: string) => void;
}

// Preset visual coordinates for the 7 factory assets in logical production flow
const NODE_LAYOUT: Record<string, { x: number; y: number }> = {
  // Raw Material Feeder F-01
  '11111111-1111-1111-1111-111111111101': { x: 80, y: 220 },
  // Drive Motor M-101
  '11111111-1111-1111-1111-111111111102': { x: 260, y: 70 },
  // Main Infeed Conveyor C-101
  '11111111-1111-1111-1111-111111111103': { x: 260, y: 220 },
  // Coolant Circulation Pump P-201
  '11111111-1111-1111-1111-111111111104': { x: 440, y: 70 },
  // Precision CNC Station CNC-301
  '11111111-1111-1111-1111-111111111105': { x: 440, y: 220 },
  // Optical Quality Inspection INS-401
  '11111111-1111-1111-1111-111111111106': { x: 620, y: 220 },
  // Robotic Packaging Cell PKG-501
  '11111111-1111-1111-1111-111111111107': { x: 800, y: 220 },
};

export const FactoryGraphView: React.FC<FactoryGraphViewProps> = ({
  graphData,
  onSelectNode,
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);

  const nodes = useMemo(() => {
    if (!graphData) return [];
    if (filterStatus === 'all') return graphData.nodes;
    return graphData.nodes.filter((n) => n.status === filterStatus);
  }, [graphData, filterStatus]);

  const edges = useMemo(() => {
    if (!graphData) return [];
    return graphData.edges;
  }, [graphData]);

  const activeNode = useMemo(() => {
    if (!selectedAssetId || !graphData) return null;
    return graphData.nodes.find((n) => n.id === selectedAssetId) || null;
  }, [selectedAssetId, graphData]);

  const getStatusColor = (status: string) => {
    if (status === 'operational') return '#10b981';
    if (status === 'degraded') return '#f59e0b';
    return '#f43f5e';
  };

  const getEdgeStroke = (rel: string) => {
    if (rel === 'drives') return '#06b6d4';
    if (rel === 'cools') return '#3b82f6';
    return '#64748b'; // feeds
  };

  return (
    <div>
      {/* Controls & Filter Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'operational', 'degraded', 'offline'].map((st) => (
            <button
              key={st}
              className={`btn ${filterStatus === st ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 14px', fontSize: '0.8rem', textTransform: 'capitalize' }}
              onClick={() => setFilterStatus(st)}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '18px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', background: '#64748b' }}></span>
            <span>Feeds Material</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', background: '#06b6d4' }}></span>
            <span>Drives Mechanical</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', background: '#3b82f6' }}></span>
            <span>Cools Auxiliary</span>
          </div>
        </div>
      </div>

      {/* 2D Interactive Topology Canvas */}
      <div className="card" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
        <svg
          viewBox="0 0 920 380"
          style={{ width: '100%', height: 'auto', minHeight: '400px' }}
        >
          <defs>
            <marker
              id="arrowhead-feeds"
              markerWidth="8"
              markerHeight="6"
              refX="7"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#64748b" />
            </marker>
            <marker
              id="arrowhead-drives"
              markerWidth="8"
              markerHeight="6"
              refX="7"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#06b6d4" />
            </marker>
            <marker
              id="arrowhead-cools"
              markerWidth="8"
              markerHeight="6"
              refX="7"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#3b82f6" />
            </marker>
          </defs>

          {/* Render Graph Edges */}
          {edges.map((e) => {
            const srcPos = NODE_LAYOUT[e.source];
            const dstPos = NODE_LAYOUT[e.target];
            if (!srcPos || !dstPos) return null;

            // Offset to node border
            const dx = dstPos.x - srcPos.x;
            const dy = dstPos.y - srcPos.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const r = 38;

            const x1 = srcPos.x + (dx * r) / dist;
            const y1 = srcPos.y + (dy * r) / dist;
            const x2 = dstPos.x - (dx * (r + 8)) / dist;
            const y2 = dstPos.y - (dy * (r + 8)) / dist;

            const strokeColor = getEdgeStroke(e.relationship_type);
            const markerId = `arrowhead-${e.relationship_type}`;

            return (
              <g key={e.id}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={strokeColor}
                  strokeWidth="2"
                  strokeDasharray={e.relationship_type === 'cools' ? '4 3' : 'none'}
                  markerEnd={`url(#${markerId})`}
                />
                <text
                  x={(x1 + x2) / 2}
                  y={(y1 + y2) / 2 - 6}
                  fill="var(--text-dim)"
                  fontSize="9"
                  fontFamily="var(--font-mono)"
                  textAnchor="middle"
                >
                  {e.relationship_type}
                </text>
              </g>
            );
          })}

          {/* Render Graph Nodes */}
          {nodes.map((node) => {
            const pos = NODE_LAYOUT[node.id] || { x: 450, y: 190 };
            const isSelected = selectedAssetId === node.id;
            const statusColor = getStatusColor(node.status);

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  setSelectedAssetId(node.id);
                  onSelectNode(node.id);
                }}
              >
                {/* Node Ring */}
                <circle
                  r="34"
                  fill="#121824"
                  stroke={isSelected ? 'var(--accent-cyan)' : statusColor}
                  strokeWidth={isSelected ? '3' : '2'}
                  filter={isSelected ? 'drop-shadow(0 0 8px rgba(6, 182, 212, 0.6))' : 'none'}
                />

                {/* Inner Icon / Letter */}
                <text
                  textAnchor="middle"
                  dy="-4"
                  fill="#ffffff"
                  fontSize="12"
                  fontWeight="700"
                  fontFamily="var(--font-sans)"
                >
                  {node.asset_type.toUpperCase().slice(0, 3)}
                </text>

                {/* Status Dot */}
                <circle
                  cx="0"
                  cy="14"
                  r="4"
                  fill={statusColor}
                />

                {/* Node Label */}
                <text
                  textAnchor="middle"
                  dy="52"
                  fill="#f8fafc"
                  fontSize="11"
                  fontWeight="600"
                  fontFamily="var(--font-sans)"
                >
                  {node.name.split(' ')[0]} {node.name.split(' ')[1] || ''}
                </text>

                <text
                  textAnchor="middle"
                  dy="66"
                  fill="var(--text-dim)"
                  fontSize="9"
                  fontFamily="var(--font-mono)"
                >
                  Crit {node.criticality.toFixed(1)}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Summary Box */}
        {activeNode && (
          <div
            style={{
              position: 'absolute',
              bottom: '20px',
              right: '20px',
              background: 'rgba(20, 28, 46, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '16px 20px',
              width: '320px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.5)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span className={`pill pill-${activeNode.status}`}>{activeNode.status}</span>
              <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                Crit {activeNode.criticality.toFixed(1)}/5.0
              </span>
            </div>
            <div style={{ fontWeight: 700, fontSize: '0.98rem', marginBottom: '4px' }}>{activeNode.name}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '12px' }}>
              Type: {activeNode.asset_type} · Location: {activeNode.location || 'Main Factory'}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '10px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Anomaly Risk Score:</span>
              <span className="mono" style={{ fontWeight: 600, color: (activeNode.current_risk_score || 0) > 0.5 ? 'var(--accent-rose)' : 'var(--accent-emerald)' }}>
                {((activeNode.current_risk_score || 0) * 100).toFixed(0)}%
              </span>
            </div>
            <button
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '12px', fontSize: '0.78rem', padding: '6px' }}
              onClick={() => onSelectNode(activeNode.id)}
            >
              Inspect Telemetry & Neighbors <ArrowRight size={13} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
