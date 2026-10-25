from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    title: str
    document_type: str
    asset_type: str
    source_label: str
    version: str
    created_at: datetime
    is_demo: bool = True

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    section: str
    asset_type: str
    content: str
    similarity_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    status: str
    total_documents: int
    total_chunks: int
    message: str
