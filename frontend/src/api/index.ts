import type { ArticleMeta, Comment, ToolItem, MediaListResponse, SiteInfo } from "../types";

const API_BASE = "/api";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  // Articles
  getArticles: (page = 1, limit = 20, category?: string, search?: string) => {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    if (category) params.set("category", category);
    if (search) params.set("search", search);
    return fetchJSON<{ items: ArticleMeta[]; total: number; page: number }>(
      `/articles?${params}`
    );
  },
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
  getMedia: (type?: string, page = 1, limit = 20) => {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    if (type) params.set("type", type);
    return fetchJSON<MediaListResponse>(`/media?${params}`);
  },

  // Adjacent articles (prev/next)
  getAdjacentArticles: (id: number) =>
    fetchJSON<{ prev: { id: number; title: string } | null; next: { id: number; title: string } | null }>(
      `/articles/${id}/adjacent`
    ),

  // Site info
  getSiteInfo: () => fetchJSON<SiteInfo>("/site-info"),
};
