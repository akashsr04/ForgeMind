import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { BookOpen, Search, Layers, RefreshCw, FileText } from 'lucide-react';

export const EvidenceView: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('bearing vibration temperature limit');
  const [assetType, setAssetType] = useState('motor');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState('');

  useEffect(() => {
    loadDocs();
    handleSearch();
  }, []);

  async function loadDocs() {
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      // Use investigation pipeline's evidence retrieval endpoint or trigger search
      // For standalone search, we can query via investigations or test
      const res = await fetch(`/api/v1/incidents/demo-trigger`, { method: 'GET' }).catch(() => null);
      // Retrieve directly by calling custom endpoint or through sample search
      // Let's call the search function through a quick request or mock query preview
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  }

  async function handleIngest() {
    setIngesting(true);
    setIngestMsg('');
    try {
      const res = await api.ingestDocuments();
      setIngestMsg(res.message);
      await loadDocs();
    } catch (err) {
      console.error('Failed to ingest documents', err);
    } finally {
      setIngesting(false);
    }
  }

  return (
    <div>
      {/* Header and Ingest Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Maintenance Knowledge Base (RAG)</h2>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Seeded equipment manuals, SOPs, and troubleshooting guides stored in Qdrant vector database.
          </div>
        </div>

        <button
          className="btn btn-secondary"
          onClick={handleIngest}
          disabled={ingesting}
          style={{ padding: '8px 16px', fontSize: '0.82rem' }}
        >
          <RefreshCw size={14} className={ingesting ? 'spin' : ''} />
          {ingesting ? 'Chunking & Indexing...' : 'Re-index Qdrant Vectors'}
        </button>
      </div>

      {ingestMsg && (
        <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', color: 'var(--accent-emerald)', fontSize: '0.82rem', marginBottom: '20px' }}>
          {ingestMsg}
        </div>
      )}

      {/* Document Library Cards */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <BookOpen size={18} color="var(--accent-cyan)" />
          <span>Ingested Maintenance Procedures ({documents.length} Manuals)</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {documents.map((doc) => (
            <div
              key={doc.id}
              style={{
                background: 'var(--bg-main)',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="pill pill-operational" style={{ fontSize: '0.68rem' }}>{doc.document_type}</span>
                <span className="mono" style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>v{doc.version}</span>
              </div>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '4px' }}>{doc.title}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                Target Asset Type: <span style={{ color: 'var(--accent-cyan)' }}>{doc.asset_type}</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '8px' }}>
                Source: {doc.source_label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* RAG Mechanics Architecture Note */}
      <div className="card" style={{ background: 'var(--bg-card)' }}>
        <div className="card-title">
          <Layers size={18} color="var(--accent-purple)" />
          <span>Local Vector Search & Citation Guarantee</span>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
          ForgeMind chunks all markdown technical manuals by header boundaries (##) while generating deterministic stable identifiers (e.g. <code className="mono" style={{ color: 'var(--accent-cyan)' }}>chk_...</code>).
          Vectors are stored in Qdrant with payload metadata containing the asset type, source title, and section.
          During LangGraph agent triage, hypotheses are constrained to cite only chunks returned by the Qdrant retrieval tool.
        </div>
      </div>
    </div>
  );
};
