import { api } from "../api";
import { useState, useEffect } from "react";
import type { SiteInfo, ArticleMeta, Comment } from "../types";

interface SidebarProps {
  type: "site" | "article";
  articleId?: number;
  onCategoryClick?: (category: string) => void;
}

export default function Sidebar({ type, articleId, onCategoryClick }: SidebarProps) {
  const [siteInfo, setSiteInfo] = useState<SiteInfo | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [recentArticles, setRecentArticles] = useState<ArticleMeta[]>([]);

  useEffect(() => {
    if (type === "site") {
      api.getSiteInfo().then(setSiteInfo).catch(() => {});
    }
    api.getArticles(1, 5).then((d) => setRecentArticles(d.items)).catch(() => {});
    if (articleId) {
      api.getComments(articleId).then(setComments).catch(() => {});
    }
  }, [type, articleId]);

  return (
    <aside className="space-y-6">
      {/* Site Stats */}
      {siteInfo && type === "site" && (
        <div className="terminal-card rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
            <span>?</span> STATS
          </div>
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="bg-dark-800/50 rounded p-2">
              <div className="text-accent text-lg font-bold">{siteInfo.total_articles}</div>
              <div className="text-gray-500 text-xs font-mono">Articles</div>
            </div>
            <div className="bg-dark-800/50 rounded p-2">
              <div className="text-neon-blue text-lg font-bold">{siteInfo.total_views}</div>
              <div className="text-gray-500 text-xs font-mono">Views</div>
            </div>
          </div>
        </div>
      )}

      {/* Categories */}
      {siteInfo && siteInfo.categories?.length > 0 && (
        <div className="terminal-card rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
            <span>?</span> CATEGORIES
          </div>
          <div className="space-y-1.5">
            {siteInfo.categories.map((cat) => (
              <button
                key={cat.category}
                onClick={() => onCategoryClick?.(cat.category)}
                className="flex items-center justify-between w-full px-2 py-1 rounded text-xs font-mono text-gray-400 hover:text-accent hover:bg-dark-800/50 transition-colors"
              >
                <span className="text-neon-blue">{cat.category}</span>
                <span className="bg-dark-700 px-1.5 py-0.5 rounded text-gray-500">{cat.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Recent Articles */}
      <div className="terminal-card rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
          <span>?</span> RECENT
        </div>
        <div className="space-y-2">
          {recentArticles.slice(0, 5).map((a) => (
            <div key={a.id} className="text-xs font-mono text-gray-400 hover:text-accent transition-colors cursor-pointer">
              <span className="text-gray-600">{a.created_at?.split("T")[0]}</span>
              {" — "}{a.title.length > 24 ? a.title.slice(0, 24) + "…" : a.title}
            </div>
          ))}
        </div>
      </div>

      {/* Article Comments */}
      {type === "article" && (
        <div className="terminal-card rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
            <span>?</span> COMMENTS ({comments.length})
          </div>
          {comments.length === 0 ? (
            <p className="text-xs text-gray-600 font-mono">// no comments yet</p>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {comments.map((c) => (
                <div key={c.id} className="border-b border-dark-700 pb-2 last:border-0">
                  <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
                    <span className="text-neon-purple">{c.author}</span>
                    <span>?</span>
                    <span>{c.created_at?.split("T")[0]}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{c.content}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
