import React from 'react';
import {
  Activity,
  GitGraph,
  AlertTriangle,
  Cpu,
  BookOpen,
  LineChart,
  ShieldCheck,
} from 'lucide-react';

export type ViewType =
  | 'overview'
  | 'graph'
  | 'investigation'
  | 'digital-twin'
  | 'evidence'
  | 'model-eval';

interface SidebarProps {
  currentView: ViewType;
  onSelectView: (view: ViewType) => void;
  openIncidentsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onSelectView,
  openIncidentsCount,
}) => {
  const navItems = [
    { id: 'overview', label: 'Factory Overview', icon: Activity },
    { id: 'graph', label: 'Asset Topology', icon: GitGraph },
    {
      id: 'investigation',
      label: 'Incident Workbench',
      icon: AlertTriangle,
      badge: openIncidentsCount > 0 ? `${openIncidentsCount} Active` : undefined,
      badgeAlert: openIncidentsCount > 0,
    },
    { id: 'digital-twin', label: 'Digital Twin Lab', icon: Cpu },
    { id: 'evidence', label: 'Maintenance RAG', icon: BookOpen },
    { id: 'model-eval', label: 'Model & Evaluation', icon: LineChart },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldCheck size={22} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">ForgeMind</div>
          <div className="brand-subtitle">Industrial Twin AI</div>
        </div>
      </div>

      <nav className="nav-menu">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectView(item.id as ViewType)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badge && (
                <span className={`nav-badge ${item.badgeAlert ? 'badge-alert' : ''}`}>
                  {item.badge}
                </span>
              )}
            </div>
          );
        })}
      </nav>

      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--accent-emerald)' }}></span>
          <span style={{ fontWeight: 600, color: 'var(--text-muted)' }}>Local Execution Active</span>
        </div>
        <div>Zero-Paid-API Mode (Standalone)</div>
      </div>
    </aside>
  );
};
