import { useState, useEffect, useCallback } from "react";
import { api } from "../api";
import type { ArticleMeta } from "../types";
import ArticleCard from "../components/ArticleCard";

interface ArticleListProps {
  onNavigate: (page: "home" | "articles" | "article" | "tool" | "my" | "about", id?: number) => void;
}

export default function ArticleList({ onNavigate }: ArticleListProps) {
  const [articles, setArticles] = useState<ArticleMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [allCategories, setAllCategories] = useState<string[]>([]);

  const fetchArticles = useCallback(async (cat: string, q: string) => {
    setLoading(true);
    try {
      const data = await api.getArticles(1, 50, cat || undefined, q || undefined);
      setArticles(data.items);
      // Collect unique categories from all articles for the filter dropdown
      if (!cat && !q) {
        const cats = [...new Set(data.items.map((a) => a.category))].sort();
        setAllCategories(cats);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchArticles("", "");
  }, [fetchArticles]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchArticles(category, search);
    }, 300);
    return () => clearTimeout(timer);
  }, [category, search, fetchArticles]);

  const handleCategoryClick = (cat: string) => {
    setCategory(cat === category ? "" : cat);
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <span className="text-accent font-mono text-lg">? ARTICLES</span>
        <div className="flex-1 h-px bg-dark-700" />
        <span className="text-xs text-gray-600 font-mono">{articles.length} posts</span>
      </div>

      {/* Search bar */}
      <div className="mb-4">
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 font-mono text-xs">$</span>
          <input
            type="text"
            placeholder="grep title / content / tags..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-dark-900 border border-dark-600 rounded pl-8 pr-3 py-2 text-xs font-mono text-gray-300 placeholder-gray-700 focus:outline-none focus:border-accent transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 text-xs"
            >
              x
            </button>
          )}
        </div>
      </div>

      {/* Category filter pills */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        <span className="text-[10px] text-gray-600 font-mono mr-1">// filter:</span>
        {allCategories.map((cat) => (
          <button
            key={cat}
            onClick={() => handleCategoryClick(cat)}
            className={`px-2.5 py-1 text-[11px] font-mono rounded border transition-all ${
              category === cat
                ? "border-accent text-accent bg-accent/10"
                : "border-dark-600 text-gray-500 hover:border-dark-500 hover:text-gray-400"
            }`}
          >
            {cat}
          </button>
        ))}
        {category && (
          <button
            onClick={() => setCategory("")}
            className="text-[10px] text-gray-600 font-mono hover:text-gray-400 ml-1"
          >
            // clear
          </button>
        )}
      </div>

      {/* Article list */}
      {loading ? (
        <div className="text-center py-20">
          <div className="text-accent font-mono text-sm animate-pulse">$ loading...</div>
        </div>
      ) : articles.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-dark-600">?</div>
          <p className="text-gray-600 font-mono text-sm">// No articles found</p>
        </div>
      ) : (
        <div className="relative pl-2">
          {articles.map((article, i) => (
            <ArticleCard
              key={article.id}
              article={article}
              index={i}
              onClick={(id) => onNavigate("article", id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
