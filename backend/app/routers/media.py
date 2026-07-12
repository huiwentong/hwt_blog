from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MediaItem
from app.schemas import MediaListResponse, MediaResponse

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=MediaListResponse)
def list_media(
    type: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(MediaItem)
    if type:
        q = q.filter(MediaItem.type == type)

    total = q.count()
    items = q.order_by(MediaItem.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return MediaListResponse(
        items=[MediaResponse.model_validate(it) for it in items],
        total=total,
        page=page,
    )
