import type { ArticleMeta, Comment, ToolItem, MediaItem, SiteInfo } from "../types";

const API_BASE = "/api";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // Articles
  getArticles: (page = 1, limit = 20) =>
    fetchJSON<{ items: ArticleMeta[]; total: number; page: number }>(
      `/articles?page=${page}&limit=${limit}`
    ),
  getArticle: (id: number) =>
    fetchJSON<ArticleMeta>(`/articles/${id}`),
  getArticlesByCategory: (category: string) =>
    fetchJSON<ArticleMeta[]>(`/articles?category=${category}`),

  // Comments
  getComments: (articleId: number) =>
    fetchJSON<Comment[]>(`/articles/${articleId}/comments`),
  postComment: (articleId: number, author: string, content: string) =>
    fetch(`${API_BASE}/articles/${articleId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ author, content }),
    }),

  // Tools
  getTools: () => fetchJSON<ToolItem[]>("/tools"),

  // Media
  getMedia: (type?: string) =>
    fetchJSON<MediaItem[]>(type ? `/media?type=${type}` : "/media"),

  // Site info
  getSiteInfo: () => fetchJSON<SiteInfo>("/site-info"),
};
