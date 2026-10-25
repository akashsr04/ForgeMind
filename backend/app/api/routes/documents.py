from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Document
from app.schemas.documents import DocumentResponse, DocumentIngestResponse
from app.rag.ingestion import ingest_demo_documents

router = APIRouter(tags=["Documents & Evidence"])


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.post("/documents/ingest-demo", response_model=DocumentIngestResponse, status_code=status.HTTP_200_OK)
def ingest_demo_documents_endpoint(db: Session = Depends(get_db)):
    result = ingest_demo_documents(db)
    return DocumentIngestResponse(**result)
