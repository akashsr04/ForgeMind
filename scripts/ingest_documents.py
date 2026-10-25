import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.infrastructure.db.session import SessionLocal, init_db
from app.rag.ingestion import ingest_demo_documents
from app.core.logging import setup_logging, logger


def main():
    setup_logging()
    init_db()
    db = SessionLocal()
    try:
        logger.info("Ingesting demo maintenance documents...")
        result = ingest_demo_documents(db)
        logger.info(f"Ingestion result: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
