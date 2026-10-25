import React, { useState, useEffect } from 'react';
import { Bell, Zap, CheckCircle2, Clock } from 'lucide-react';
import { api } from '../api/client';

interface TopBarProps {
  title: string;
  onTriggerDemo: () => Promise<void>;
  isTriggering: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ title, onTriggerDemo, isTriggering }) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + ' UTC');
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="top-bar">
      <div>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.2px' }}>{title}</h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button
          className="btn btn-primary"
          onClick={onTriggerDemo}
          disabled={isTriggering}
          style={{ padding: '7px 14px', fontSize: '0.82rem' }}
          title="Simulate bearing degradation & thermal runaway on Drive Motor M-101"
        >
          <Zap size={15} />
          {isTriggering ? 'Simulating Incident...' : 'Trigger Demo Incident'}
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg-card)', padding: '6px 12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
          <Clock size={14} color="var(--accent-cyan)" />
          <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{timeStr}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--accent-emerald)' }}>
          <CheckCircle2 size={16} />
          <span style={{ fontWeight: 600 }}>Backend Connected</span>
        </div>
      </div>
    </header>
  );
};
