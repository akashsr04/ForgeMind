import pytest
from app.infrastructure.db.session import SessionLocal, init_db
from app.rag.ingestion import ingest_demo_documents
from app.rag.retrieval import retrieve_maintenance_evidence


@pytest.fixture(scope="module")
def seeded_db():
    init_db()
    db = SessionLocal()
    ingest_demo_documents(db)
    yield db
    db.close()


def test_rag_retrieval_returns_relevant_chunks(seeded_db):
    results = retrieve_maintenance_evidence(query_text="bearing vibration temperature SKF", asset_type="motor", limit=3)
    assert len(results) > 0
    first = results[0]
    assert first.chunk_id.startswith("chk_")
    assert first.asset_type == "motor"
    assert "bearing" in first.content.lower() or "vibration" in first.content.lower()
    assert first.similarity_score is not None


def test_rag_retrieval_empty_query():
    # Searching for non-existent concept with high threshold or non-matching asset
    results = retrieve_maintenance_evidence(query_text="quantum cryptography teleportation", limit=2, score_threshold=0.99)
    assert len(results) == 0
