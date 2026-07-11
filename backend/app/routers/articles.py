from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Article, Comment
from app.schemas import ArticleResponse, ArticleListResponse

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
def list_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Article)
    if category:
        q = q.filter(Article.category == category)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Article.title.ilike(like)
            | Article.content.ilike(like)
            | Article.tags.ilike(like)
        )
    total = q.count()
    items = q.order_by(Article.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    def to_resp(a: Article) -> ArticleResponse:
        return ArticleResponse(
            id=a.id,
            title=a.title,
            summary=a.summary,
            content=a.content,
            author=a.author,
            category=a.category,
            tags=a.tags_list,
            views=a.views,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    return ArticleListResponse(
        items=[to_resp(a) for a in items],
        total=total,
        page=page,
    )


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Article not found")
    article.views += 1
    db.commit()
    db.refresh(article)
    return ArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        content=article.content,
        author=article.author,
        category=article.category,
        tags=article.tags_list,
        views=article.views,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
