from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# ── Article ──
class ArticleBase(BaseModel):
    title: str
    summary: str
    content: str
    author: str = "HWT"
    category: str = "General"
    tags: list[str] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: int
    views: int
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int


# ── Comment ──
class CommentCreate(BaseModel):
    author: str
    content: str


class CommentResponse(BaseModel):
    id: int
    article_id: int
    author: str
    content: str
    ip_address: str = ""
    user_agent: str = ""
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tool ──
class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    url: str
    icon: str
    category: str

    model_config = {"from_attributes": True}


# ── Media ──
class MediaResponse(BaseModel):
    id: int
    title: str
    type: str
    description: str
    url: str
    cover: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class MediaListResponse(BaseModel):
    items: list[MediaResponse]
    total: int
    page: int


# ── Site Info ──
class CategoryCount(BaseModel):
    category: str
    count: int


class SiteInfoResponse(BaseModel):
    total_articles: int
    total_views: int
    total_comments: int
    categories: list[CategoryCount]

# ---- Update payloads (manager CRUD) ----
class ArticleUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    content: str | None = None
    author: str | None = None
    category: str | None = None
    tags: list[str] | None = None


# ---- Tool ----
class ToolCreate(BaseModel):
    name: str
    description: str
    url: str
    icon: str = "\U0001F527"
    category: str = "utility"


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    url: str | None = None
    icon: str | None = None
    category: str | None = None


# ---- Media ----
class MediaCreate(BaseModel):
    title: str
    type: str
    description: str = ""
    url: str = ""
    cover: str = ""


class MediaUpdate(BaseModel):
    title: str | None = None
    type: str | None = None
    description: str | None = None
    url: str | None = None
    cover: str | None = None


# ---- H5 Page ----
class H5PageCreate(BaseModel):
    slug: str
    content: str


class H5PageResponse(BaseModel):
    id: int
    slug: str
    content: str

    model_config = {"from_attributes": True}

