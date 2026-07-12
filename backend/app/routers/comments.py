from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Article
from app.schemas import CommentCreate, CommentResponse
from app.syncer import sync_comment_to_shared

router = APIRouter(prefix="/articles/{article_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentResponse])
def list_comments(article_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .filter(Comment.article_id == article_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return comments


@router.post("", response_model=CommentResponse, status_code=201)
def create_comment(
    article_id: int,
    payload: CommentCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")

    # Capture client IP address
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else ""

    user_agent = request.headers.get("user-agent", "")

    comment = Comment(
        article_id=article_id,
        author=payload.author,
        content=payload.content,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Sync comment to shared Z drive DB (best-effort, won't break the response)
    sync_comment_to_shared(
        article_id=article_id,
        author=payload.author,
        content=payload.content,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=comment.created_at.isoformat() if comment.created_at else None,
    )

    return comment