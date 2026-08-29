"""API client for the HWT BLOG manager.

All article / tool / media / h5-page operations go through the backend REST
API over the network instead of touching a local SQLite file.
"""
import json
import os
import urllib.error
import urllib.request

DEFAULT_API_BASE = os.environ.get("HWT_API_BASE", "https://hwthuiwentong.com")


class ApiError(Exception):
    """Raised when the backend returns an error or is unreachable."""


class DbManager:
    """Thin HTTP client matching the old SQLite DbManager method surface."""

    def __init__(self, base_url: str = DEFAULT_API_BASE):
        self.base_url = self._normalize_base(base_url)
        # Fail fast with a readable error if the server is unreachable.
        self._request("GET", "/health")

    @staticmethod
    def _normalize_base(base_url: str) -> str:
        """Append the /api prefix when the user only gives host:port."""
        base_url = base_url.strip().rstrip("/")
        if not base_url.endswith("/api"):
            base_url += "/api"
        return base_url

    # ---- HTTP helpers -------------------------------------------------

    def _request(self, method: str, path: str, payload: dict | None = None):
        url = f"{self.base_url}{path}"
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read()
                if not body:
                    return None
                return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = self._extract_detail(e)
            if e.code == 409:
                raise ValueError(detail or "Resource already exists (409)") from e
            raise ApiError(f"Request failed ({e.code}): {detail or e.reason}") from e
        except urllib.error.URLError as e:
            raise ApiError(f"Cannot reach server {self.base_url}: {e.reason}") from e

    @staticmethod
    def _extract_detail(err: urllib.error.HTTPError) -> str:
        try:
            data = json.loads(err.read().decode("utf-8"))
            detail = data.get("detail")
            if isinstance(detail, list):
                return "; ".join(str(d.get("msg", d)) for d in detail)
            return str(detail or "")
        except Exception:
            return ""

    # ---- Articles -----------------------------------------------------

    def add_article(
        self,
        title: str,
        summary: str,
        content: str,
        category: str,
        tags: str,
        author: str = "HWT",
    ) -> int:
        payload = {
            "title": title,
            "summary": summary,
            "content": content,
            "author": author,
            "category": category,
            "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        }
        data = self._request("POST", "/articles", payload)
        return data["id"]

    def get_recent_articles(self, limit: int = 50):
        data = self._request("GET", f"/articles?page=1&limit={limit}") or {}
        rows = []
        for a in data.get("items", []):
            rows.append({
                "id": a["id"],
                "title": a["title"],
                "summary": a.get("summary", ""),
                "category": a.get("category", ""),
                "tags": ",".join(a.get("tags") or []),
                "author": a.get("author", ""),
                "views": a.get("views", 0),
                "created_at": a.get("created_at", ""),
            })
        return rows

    def delete_article(self, article_id: int) -> bool:
        self._request("DELETE", f"/articles/{article_id}")
        return True

    # ---- Tools --------------------------------------------------------

    def add_tool(
        self,
        name: str,
        description: str,
        url: str,
        category: str,
        icon: str = "\U0001F527",
    ) -> int:
        data = self._request("POST", "/tools", {
            "name": name,
            "description": description,
            "url": url,
            "icon": icon,
            "category": category,
        })
        return data["id"]

    def get_recent_tools(self, limit: int = 50):
        items = self._request("GET", "/tools") or []
        return [{
            "id": t["id"],
            "name": t["name"],
            "description": t.get("description", ""),
            "url": t.get("url", ""),
            "icon": t.get("icon", ""),
            "category": t.get("category", ""),
        } for t in items]

    def delete_tool(self, tool_id: int) -> bool:
        self._request("DELETE", f"/tools/{tool_id}")
        return True

    # ---- Media --------------------------------------------------------

    def add_media(
        self,
        title: str,
        type_: str,
        description: str = "",
        url: str = "",
        cover: str = "",
    ) -> int:
        data = self._request("POST", "/media", {
            "title": title,
            "type": type_,
            "description": description,
            "url": url,
            "cover": cover,
        })
        return data["id"]

    def get_recent_media(self, limit: int = 50):
        data = self._request("GET", f"/media?page=1&limit={limit}") or {}
        rows = []
        for m in data.get("items", []):
            rows.append({
                "id": m["id"],
                "title": m["title"],
                "type": m["type"],
                "description": m.get("description", ""),
                "url": m.get("url", ""),
                "cover": m.get("cover", ""),
                "created_at": m.get("created_at", ""),
            })
        return rows

    def delete_media(self, media_id: int) -> bool:
        self._request("DELETE", f"/media/{media_id}")
        return True

    # ---- H5 pages -----------------------------------------------------

    def add_h5_page(self, slug: str, content: str) -> int:
        data = self._request("POST", "/tools/h5", {"slug": slug, "content": content})
        return data["id"]

    def get_h5_page_by_slug(self, slug: str) -> dict | None:
        for page in self._request("GET", "/tools/h5") or []:
            if page["slug"] == slug:
                return page
        return None

    def get_recent_h5_pages(self, limit: int = 50):
        return self._request("GET", "/tools/h5") or []

    def delete_h5_page(self, h5_id: int) -> bool:
        self._request("DELETE", f"/tools/h5/{h5_id}")
        return True

    # ---- Stats --------------------------------------------------------

    def get_stats(self) -> dict:
        data = self._request("GET", "/stats") or {}
        return {
            "articles": data.get("articles", 0),
            "tools": data.get("tools", 0),
            "media": data.get("media", 0),
            "h5_pages": data.get("h5_pages", 0),
            "views": data.get("views", 0),
        }
