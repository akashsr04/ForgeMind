from typing import List, Optional
from qdrant_client.http import models as qmodels
from app.infrastructure.qdrant.client import get_qdrant_client
from app.infrastructure.embeddings.embedder import get_embedding_service
from app.schemas.documents import DocumentChunkResponse
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def retrieve_maintenance_evidence(
    query_text: str,
    asset_type: Optional[str] = None,
    limit: int = 4,
    score_threshold: float = 0.15,
) -> List[DocumentChunkResponse]:
    """
    Retrieves evidence chunks from Qdrant matching query and optional asset_type filter.
    Returns source titles, chunk IDs, and section metadata.
    """
    client = get_qdrant_client()
    embedder = get_embedding_service()
    collection_name = settings.QDRANT_COLLECTION

    # Check collection existence
    try:
        collections = client.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            logger.warning(f"Qdrant collection '{collection_name}' does not exist.")
            return []
    except Exception as e:
        logger.error(f"Failed to access Qdrant collections: {e}")
        return []

    query_vector = embedder.embed_text(query_text)

    query_filter = None
    if asset_type:
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="asset_type",
                    match=qmodels.MatchValue(value=asset_type),
                )
            ]
        )

    try:
        if hasattr(client, "query_points"):
            query_res = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )
            search_results = query_res.points
        elif hasattr(client, "search"):
            search_results = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )
        else:
            search_results = []
    except Exception as e:
        logger.error(f"Error executing Qdrant search: {e}")
        return []

    evidence_chunks: List[DocumentChunkResponse] = []
    for hit in search_results:
        payload = hit.payload or {}
        evidence_chunks.append(
            DocumentChunkResponse(
                chunk_id=payload.get("chunk_id", str(hit.id)),
                document_id=payload.get("document_id", ""),
                title=payload.get("title", "Unknown"),
                section=payload.get("section", "General"),
                asset_type=payload.get("asset_type", "general"),
                content=payload.get("content", ""),
                similarity_score=round(float(hit.score), 4),
                metadata=payload.get("metadata", {}),
            )
        )

    return evidence_chunks
