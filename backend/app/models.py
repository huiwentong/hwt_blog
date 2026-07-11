from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(50), default="HWT")
    category = Column(String(50), default="General")
    tags = Column(Text, default="")  # comma-separated
    views = Column(Integer, server_default=text("0"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()] if self.tags else []


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    author = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    ip_address = Column(String(45), default="")
    user_agent = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    article = relationship("Article", back_populates="comments")


class ToolItem(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String(500), nullable=False)
    icon = Column(String(10), default="🔧")
    category = Column(String(50), default="utility")


class MediaItem(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # music, photo, movie
    description = Column(Text, default="")
    url = Column(String(500), default="")
    cover = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))