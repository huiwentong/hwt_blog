from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MediaItem
from app.schemas import MediaResponse

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[MediaResponse])
def list_media(type: str | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(MediaItem)
    if type:
        q = q.filter(MediaItem.type == type)
    return q.order_by(MediaItem.created_at.desc()).all()
