from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.infrastructure.db.models import Asset
from app.schemas.recommendations import ActionRankingRequest, ActionRankingResponse
from app.domain.recommendations.ranker import rank_candidate_actions
from app.core.errors import ResourceNotFoundException

router = APIRouter(tags=["Recommendations"])


@router.post("/recommendations/rank", response_model=ActionRankingResponse)
def rank_actions_endpoint(
    req: ActionRankingRequest,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == req.asset_id).first()
    if not asset:
        raise ResourceNotFoundException("Asset", req.asset_id)

    res = rank_candidate_actions(
        asset_type=asset.asset_type,
        request=req,
        evidence_refs=[],
    )
    return res
