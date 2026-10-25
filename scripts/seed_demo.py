import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.infrastructure.db.session import SessionLocal, init_db
from app.seed.demo_factory import seed_demo_factory
from app.core.logging import setup_logging, logger


def main():
    setup_logging()
    logger.info("Initializing database schema...")
    init_db()

    db = SessionLocal()
    try:
        logger.info("Running factory seed...")
        seed_demo_factory(db)
        logger.info("Seeding completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
