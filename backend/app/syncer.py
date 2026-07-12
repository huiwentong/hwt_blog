"""Syncer: make backend DB mirror the shared manager DB for managed tables,
while preserving server-only data (comments, article views)."""
import sqlite3
import os
import pathlib
from datetime import datetime, timezone

# Shared folder paths
WATCH_DIR_WIN = "Z:/github/db"
WATCH_DIR_LINUX = "/mnt/z/github/db"
SIGNAL_FILE = "new.txt"
DB_FILE = "hwt_blog.db"


def _get_watch_dir() -> str | None:
    if os.name == "nt":
        d = WATCH_DIR_WIN
        if os.path.isdir(d):
            return d
        print(f"[syncer] Watch dir not found: {d}")
        return None
    else:
        d = WATCH_DIR_LINUX
        if os.path.isdir(d):
            return d
        print(f"[syncer] Watch dir not found: {d}")
        return None


def merge_from_shared(backend_db: str) -> bool:
    """Fully replace articles/tools/media from shared DB, preserving comments and views."""
    watch_dir = _get_watch_dir()
    if not watch_dir:
        return False

    signal_path = os.path.join(watch_dir, SIGNAL_FILE)
    shared_db = os.path.join(watch_dir, DB_FILE)

    if not os.path.isfile(signal_path):
        return False
    if not os.path.isfile(shared_db):
        print(f"[syncer] Signal file found but no DB at: {shared_db}")
        return False

    now = datetime.now(timezone.utc).isoformat()

    try:
        b_conn = sqlite3.connect(backend_db, timeout=10)
        b_cur = b_conn.cursor()
        b_cur.execute("PRAGMA journal_mode=WAL")
        b_cur.execute("PRAGMA foreign_keys = OFF")
        b_conn.commit()

        s_conn = sqlite3.connect(shared_db)
        s_cur = s_conn.cursor()


        # 1. Preserve server-only data (before clearing)
        # Assign new auto-increment IDs so they won't conflict
        comments = b_cur.execute(
            "SELECT article_id, author, content, ip_address, user_agent, created_at FROM comments"
        ).fetchall()

        article_views = {
            row[0]: row[1]
            for row in b_cur.execute("SELECT id, views FROM articles").fetchall()
        }

        # 2. Clear all managed tables (explicit order, no FK cascade)
        b_cur.execute("DELETE FROM comments")
        b_cur.execute("DELETE FROM media")
        b_cur.execute("DELETE FROM tools")
        b_cur.execute("DELETE FROM articles")

        # 3. Re-insert articles from shared
        s_articles = s_cur.execute(
            "SELECT id, title, summary, content, author, category, tags, created_at, updated_at FROM articles"
        ).fetchall()
        for art in s_articles:
            aid, title, summary, content, author, category, tags, created, updated = art
            views = article_views.get(aid, 0)
            b_cur.execute(
                """INSERT INTO articles
                   (id, title, summary, content, author, category, tags, views, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (aid, title, summary, content, author, category, tags, views, created or now, updated or now),
            )

        # 4. Re-insert preserved comments (auto-increment IDs)
        for c in comments:
            article_id, author, content, ip, ua, created = c
            exists = b_cur.execute("SELECT 1 FROM articles WHERE id = ?", (article_id,)).fetchone()
            if exists:
                b_cur.execute(
                    """INSERT INTO comments (article_id, author, content, ip_address, user_agent, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (article_id, author, content, ip, ua, created),
                )

        # 5. Re-insert tools from shared
        s_tools = s_cur.execute(
            "SELECT id, name, description, url, icon, category FROM tools"
        ).fetchall()
        for t in s_tools:
            b_cur.execute(
                """INSERT INTO tools (id, name, description, url, icon, category)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                t,
            )

        # 6. Re-insert media from shared
        s_media = s_cur.execute(
            "SELECT id, title, type, description, url, cover, created_at FROM media"
        ).fetchall()
        for m in s_media:
            b_cur.execute(
                """INSERT INTO media (id, title, type, description, url, cover, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                m,
            )

        b_cur.execute("PRAGMA foreign_keys = ON")
        b_conn.commit()
        b_conn.close()
        s_conn.close()

        os.remove(signal_path)
        return True

    except Exception as e:
        print(f"[syncer] Merge failed: {e}")
        return False


def get_db_path() -> str:
    _db_dir = pathlib.Path(__file__).resolve().parent.parent / "data"
    return str(_db_dir / "hwt_blog.db")

def sync_comment_to_shared(
    article_id: int,
    author: str,
    content: str,
    ip_address: str = "",
    user_agent: str = "",
    created_at: str | None = None,
) -> bool:
    """After a comment is created locally, push it to the shared manager DB."""
    watch_dir = _get_watch_dir()
    if not watch_dir:
        return False

    shared_db = os.path.join(watch_dir, DB_FILE)
    if not os.path.isfile(shared_db):
        print(f"[sync-comment] Shared DB not found at: {shared_db}")
        return False

    try:
        conn = sqlite3.connect(shared_db, timeout=10)
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")

        # Ensure the table exists (schema may differ from backend)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                author VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                ip_address VARCHAR(45) DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute(
            """INSERT INTO comments (article_id, author, content, ip_address, user_agent, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (article_id, author, content, ip_address, user_agent, created_at),
        )
        conn.commit()
        conn.close()
        print(f"[sync-comment] Comment synced to shared DB (article={article_id})")
        return True

    except Exception as e:
        print(f"[sync-comment] Failed: {e}")
        return False