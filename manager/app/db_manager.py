"""Database manager 閳?CRUD operations for HWT BLOG SQLite database."""
import sqlite3
import os
from datetime import datetime, timezone
from typing import Optional


class DbManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_tables()

    def ensure_tables(self):
        """Create tables if they don't exist (mirrors backend schema)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(50) DEFAULT 'HWT',
                category VARCHAR(50) DEFAULT 'General',
                tags TEXT DEFAULT '',
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                author VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                ip_address VARCHAR(45) DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                url VARCHAR(500) NOT NULL,
                icon VARCHAR(10) DEFAULT '棣冩暋',
                category VARCHAR(50) DEFAULT 'utility'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                type VARCHAR(20) NOT NULL,
                description TEXT DEFAULT '',
                url VARCHAR(500) DEFAULT '',
                cover VARCHAR(500) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: add ip_address / user_agent if missing
        try:
            cursor.execute("ALTER TABLE comments ADD COLUMN ip_address VARCHAR(45) DEFAULT ''")
        except sqlite3.OperationalError:
            pass  # column already exists
        try:
            cursor.execute("ALTER TABLE comments ADD COLUMN user_agent TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()

    # 閳光偓閳光偓 Articles 閳光偓閳光偓
    def add_article(
        self,
        title: str,
        summary: str,
        content: str,
        category: str,
        tags: str,
        author: str = "HWT",
    ) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO articles (title, summary, content, author, category, tags, views, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, summary, content, author, category, tags, 0, now, now),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_recent_articles(self, limit: int = 50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, summary, category, tags, author, views, created_at "
            "FROM articles ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    # 閳光偓閳光偓 Tools 閳光偓閳光偓
    def add_tool(
        self,
        name: str,
        description: str,
        url: str,
        category: str,
        icon: str = "棣冩暋",
    ) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tools (name, description, url, icon, category) VALUES (?, ?, ?, ?, ?)",
            (name, description, url, icon, category),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_recent_tools(self, limit: int = 50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description, url, icon, category "
            "FROM tools ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    # 閳光偓閳光偓 Media 閳光偓閳光偓
    def add_media(
        self,
        title: str,
        type_: str,
        description: str = "",
        url: str = "",
        cover: str = "",
    ) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO media (title, type, description, url, cover, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, type_, description, url, cover, now),
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id

    def get_recent_media(self, limit: int = 50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, type, description, url, cover, created_at "
            "FROM media ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows


    # ── Delete ──
    def delete_article(self, article_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def delete_tool(self, tool_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tools WHERE id = ?", (tool_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def delete_media(self, media_id: int) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM media WHERE id = ?", (media_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    def get_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        articles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tools")
        tools = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM media")
        media = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(views) FROM articles")
        views = cursor.fetchone()[0] or 0
        conn.close()
        return {"articles": articles, "tools": tools, "media": media, "views": views}