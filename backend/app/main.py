from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app.routers import articles, comments, tools, media
from app.schemas import SiteInfoResponse, CategoryCount
from app.models import Article, Comment


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="NEXUS BLOG API",
    version="1.0.0",
    description="Dark hacker blog backend API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(media.router, prefix="/api")


@app.get("/api/site-info", response_model=SiteInfoResponse)
def get_site_info(db: Session = Depends(get_db)):
    total_articles = db.query(func.count(Article.id)).scalar() or 0
    total_views = db.query(func.coalesce(func.sum(Article.views), 0)).scalar() or 0
    total_comments = db.query(func.count(Comment.id)).scalar() or 0
    cats = db.query(Article.category, func.count(Article.id).label("count")).group_by(Article.category).all()
    categories = [CategoryCount(category=c, count=ct) for c, ct in cats]
    return SiteInfoResponse(
        total_articles=total_articles,
        total_views=total_views,
        total_comments=total_comments,
        categories=categories,
    )


@app.get("/api/health")
def health():
    return {"status": "online", "system": "NEXUS BLOG v1.0"}
