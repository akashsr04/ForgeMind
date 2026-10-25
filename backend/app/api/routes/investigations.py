from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Investigation
from app.schemas.investigations import StructuredInvestigation
from app.core.errors import ResourceNotFoundException

router = APIRouter(tags=["Investigations"])


@router.get("/investigations/{investigation_id}", response_model=StructuredInvestigation)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise ResourceNotFoundException("Investigation", investigation_id)
    return inv.structured_result
