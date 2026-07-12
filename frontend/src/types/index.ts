export interface ArticleMeta {
  id: number;
  title: string;
  summary: string;
  content: string;
  author: string;
  category: string;
  tags: string[];
  views: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  article_id: number;
  author: string;
  content: string;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export interface ToolItem {
  id: number;
  name: string;
  description: string;
  url: string;
  icon: string;
  category: string;
}

export interface MediaItem {
  id: number;
  title: string;
  type: "music" | "photo" | "movie";
  description: string;
  url: string;
  cover: string;
  created_at: string;
}

export interface MediaListResponse {
  items: MediaItem[];
  total: number;
  page: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface SiteInfo {
  total_articles: number;
  total_views: number;
  total_comments: number;
  categories: CategoryCount[];
}
