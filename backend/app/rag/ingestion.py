import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from qdrant_client.http import models as qmodels

from app.infrastructure.db.models import Document
from app.rag.chunking import chunk_markdown_document
from app.infrastructure.embeddings.embedder import get_embedding_service
from app.infrastructure.qdrant.client import get_qdrant_client, ensure_qdrant_collection
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def ingest_demo_documents(db: Session) -> Dict[str, Any]:
    """
    Ingests all markdown documents in the demo_documents directory into PostgreSQL
    and Qdrant idempotently.
    """
    embedder = get_embedding_service()
    qdrant = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    ensure_qdrant_collection(qdrant, collection_name, vector_dim=embedder.dim)

    demo_docs_dir = Path(__file__).resolve().parent.parent / "seed" / "demo_documents"
    if not demo_docs_dir.exists():
        logger.warning(f"Demo documents directory not found: {demo_docs_dir}")
        return {"status": "warning", "total_documents": 0, "total_chunks": 0, "message": "Directory not found"}

    doc_files = list(demo_docs_dir.glob("*.md"))
    total_docs = 0
    total_chunks = 0
    qdrant_points = []

    for file_path in doc_files:
        content = file_path.read_text(encoding="utf-8")
        title = file_path.stem.replace("_", " ")

        # Infer asset_type and doc_type
        asset_type = "general"
        if "M101" in file_path.name or "Motor" in file_path.name:
            asset_type = "motor"
        elif "P201" in file_path.name or "Pump" in file_path.name:
            asset_type = "pump"
        elif "C101" in file_path.name or "Conveyor" in file_path.name:
            asset_type = "conveyor"
        elif "CNC301" in file_path.name or "CNC" in file_path.name:
            asset_type = "cnc"

        # Check existing in PostgreSQL
        existing_doc = db.query(Document).filter(Document.title == title).first()
        if not existing_doc:
            doc_id = str(uuid.uuid4())
            doc = Document(
                id=doc_id,
                title=title,
                document_type="procedure" if "SOP" in file_path.name else "manual",
                asset_type=asset_type,
                source_label=f"Plant Docs: {file_path.name}",
                version="1.0",
                is_demo=True,
            )
            db.add(doc)
            db.commit()
        else:
            doc_id = existing_doc.id

        chunks = chunk_markdown_document(
            doc_id=doc_id,
            title=title,
            asset_type=asset_type,
            markdown_content=content,
            source_label=f"Plant Docs: {file_path.name}",
        )

        for idx, chunk in enumerate(chunks):
            vector = embedder.embed_text(chunk["content"])
            # Generate deterministic integer ID for Qdrant point from chunk_id
            point_id = int(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]).int >> 64)

            payload = {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "section": chunk["section"],
                "asset_type": chunk["asset_type"],
                "source_label": chunk["source_label"],
                "content": chunk["content"],
                "metadata": chunk["metadata"],
            }

            qdrant_points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            )
            total_chunks += 1

        total_docs += 1

    if qdrant_points:
        logger.info(f"Upserting {len(qdrant_points)} chunks to Qdrant collection '{collection_name}'...")
        qdrant.upsert(
            collection_name=collection_name,
            points=qdrant_points,
            wait=True,
        )

    return {
        "status": "success",
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "message": f"Successfully ingested {total_docs} documents ({total_chunks} chunks).",
    }
