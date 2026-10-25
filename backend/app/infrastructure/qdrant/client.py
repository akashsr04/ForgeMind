from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()

_qdrant_client_instance: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    global _qdrant_client_instance
    if _qdrant_client_instance is not None:
        return _qdrant_client_instance

    url = settings.QDRANT_URL.strip()

    if url.lower() in ("memory", ":memory:", "embedded", ""):
        logger.info("Initializing in-memory embedded Qdrant client...")
        _qdrant_client_instance = QdrantClient(":memory:")
    else:
        try:
            logger.info(f"Connecting to Qdrant at {url}...")
            client = QdrantClient(url=url, timeout=3.0)
            # Test connectivity
            client.get_collections()
            logger.info("Successfully connected to external Qdrant service.")
            _qdrant_client_instance = client
        except Exception as e:
            logger.warning(
                f"Could not connect to external Qdrant at {url} ({e}). "
                f"Falling back to embedded in-memory Qdrant instance for zero-friction local run."
            )
            _qdrant_client_instance = QdrantClient(":memory:")

    return _qdrant_client_instance


def ensure_qdrant_collection(client: QdrantClient, collection_name: str, vector_dim: int = 384) -> None:
    try:
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        if not exists:
            logger.info(f"Creating Qdrant collection '{collection_name}' with dim {vector_dim} (Cosine distance)...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_dim,
                    distance=qmodels.Distance.COSINE,
                ),
            )
        else:
            logger.info(f"Qdrant collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Error ensuring Qdrant collection '{collection_name}': {e}")
        raise
