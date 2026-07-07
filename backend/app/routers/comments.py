from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Article
from app.schemas import CommentCreate, CommentResponse

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
def create_comment(article_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    comment = Comment(
        article_id=article_id,
        author=payload.author,
        content=payload.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
