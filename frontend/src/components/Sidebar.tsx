import { api } from "../api";
import { useState, useEffect, useCallback } from "react";
import type { SiteInfo, ArticleMeta, Comment } from "../types";

interface TocItem {
  id: string;
  text: string;
  level: number;
}

interface SidebarProps {
  type: "site" | "article";
  articleId?: number;
  content?: string;          // markdown content for TOC parsing
  onCategoryClick?: (category: string) => void;
  onArticleClick?: (id: number) => void;
}

function parseToc(content: string): TocItem[] {
  const items: TocItem[] = [];
  const lines = content.split("\n");
  // Only process markdown headings (## or ###), skip HTML tags
  for (const line of lines) {
    const m = line.match(/^(#{2,3})\s+(.+)$/);
    if (m) {
      const level = m[1].length;
      const text = m[2].replace(/`/g, "").trim();
      const id = text
        .toLowerCase()
        .replace(/[^\w一-鿿]+/g, "-")
        .replace(/^-+|-+$/g, "");
      items.push({ id, text, level });
    }
  }
  return items;
}

export default function Sidebar({ type, articleId, content, onCategoryClick, onArticleClick }: SidebarProps) {
  const [siteInfo, setSiteInfo] = useState<SiteInfo | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [recentArticles, setRecentArticles] = useState<ArticleMeta[]>([]);
  const [activeHeading, setActiveHeading] = useState("");
  const [scrollProgress, setScrollProgress] = useState(0);
  const toc = content ? parseToc(content) : [];

  useEffect(() => {
    if (type === "site") {
      api.getSiteInfo().then(setSiteInfo).catch(() => {});
    }
    api.getArticles(1, 5).then((d) => setRecentArticles(d.items)).catch(() => {});
    if (articleId) {
      api.getComments(articleId).then(setComments).catch(() => {});
    }
  }, [type, articleId]);

  // Scroll listener for reading progress & active heading
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      setScrollProgress(docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0);

      // Find active heading
      let current = "";
      for (const item of toc) {
        const el = document.getElementById(item.id);
        if (el && el.getBoundingClientRect().top < 120) {
          current = item.id;
        }
      }
      setActiveHeading(current);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [toc]);

  const scrollToHeading = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, []);

  return (
    <aside className="space-y-6">
      {/* Reading Progress Bar */}
      {type === "article" && (
        <div className="terminal-card rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
            <span>?</span> PROGRESS
          </div>
          <div className="relative h-2 bg-dark-700 rounded-full overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-accent to-neon-blue rounded-full transition-all duration-200"
              style={{ width: `${scrollProgress * 100}%` }}
            />
          </div>
          <div className="mt-1 text-right text-[10px] text-gray-500 font-mono">
            {Math.round(scrollProgress * 100)}%
          </div>
        </div>
      )}

      {/* Table of Contents */}
      {type === "article" && toc.length > 0 && (
        <div className="terminal-card rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3 text-sm text-accent font-mono">
            <span>?</span> CONTENTS
          </div>
          <nav className="space-y-0.5 max-h-48 overflow-y-auto">
            {toc.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToHeading(item.id)}
                className={`block w-full text-left text-xs font-mono py-1 px-2 rounded transition-all duration-200 ${
                  activeHeading === item.id
                    ? "text-accent bg-accent/10 border-l-2 border-accent"
                    : "text-gray-400 hover:text-gray-200 hover:bg-dark-800/50 border-l-2 border-transparent"
                }`}
                style={{ paddingLeft: `${(item.level - 1) * 12 + 8}px` }}
              >
                {item.text}
              </button>
            ))}
          </nav>
        </div>
      )}

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
            <button
              key={a.id}
              onClick={() => onArticleClick?.(a.id)}
              className="block w-full text-left text-xs font-mono text-gray-400 hover:text-accent transition-all duration-200 group"
            >
              <span className="text-gray-600 group-hover:text-accent/60 transition-colors">
                {a.created_at?.split("T")[0]}
              </span>
              <span className="text-gray-600"> — </span>
              <span className="relative">
                {a.title.length > 24 ? a.title.slice(0, 24) + "…" : a.title}
                <span className="absolute bottom-0 left-0 w-0 h-[1px] bg-accent group-hover:w-full transition-all duration-300" />
              </span>
            </button>
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

      {/* Back to Top */}
      {type === "article" && (
        <div className="terminal-card rounded-lg p-4">
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="flex items-center justify-center gap-2 w-full py-3 text-xs font-mono
                       text-gray-400 hover:text-accent border border-dark-700
                       rounded-lg hover:border-accent/50 transition-all duration-300
                       group"
          >
            <svg className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
            <span>BACK TO TOP</span>
          </button>
        </div>
      )}
    </aside>
  );
}
