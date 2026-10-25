from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies import get_db
from app.infrastructure.qdrant.client import get_qdrant_client
from app.core.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    qdrant_status = "ok"
    try:
        qdrant = get_qdrant_client()
        qdrant.get_collections()
    except Exception as e:
        qdrant_status = f"unhealthy: {str(e)}"

    overall = "ok" if db_status == "ok" and qdrant_status == "ok" else "degraded"

    return {
        "status": overall,
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "dependencies": {
            "database": db_status,
            "qdrant_vector_store": qdrant_status,
        },
    }
