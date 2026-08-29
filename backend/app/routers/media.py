from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MediaItem
from app.schemas import MediaListResponse, MediaResponse, MediaCreate, MediaUpdate

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=MediaListResponse)
def list_media(
    type: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(MediaItem)
    if type:
        q = q.filter(MediaItem.type == type)
    if search:
        like = f"%{search}%"
        q = q.filter(MediaItem.title.ilike(like) | MediaItem.description.ilike(like))

    total = q.count()
    items = q.order_by(MediaItem.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return MediaListResponse(
        items=[MediaResponse.model_validate(it) for it in items],
        total=total,
        page=page,
    )

@router.post("", response_model=MediaResponse, status_code=201)
def create_media(payload: MediaCreate, db: Session = Depends(get_db)):
    item = MediaItem(
        title=payload.title,
        type=payload.type,
        description=payload.description,
        url=payload.url,
        cover=payload.cover,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{media_id}", response_model=MediaResponse)
def update_media(media_id: int, payload: MediaUpdate, db: Session = Depends(get_db)):
    item = db.query(MediaItem).filter(MediaItem.id == media_id).first()
    if not item:
        raise HTTPException(404, "Media not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{media_id}")
def delete_media(media_id: int, db: Session = Depends(get_db)):
    item = db.query(MediaItem).filter(MediaItem.id == media_id).first()
    if not item:
        raise HTTPException(404, "Media not found")
    db.delete(item)
    db.commit()
    return {"ok": True}

