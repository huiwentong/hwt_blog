import { useState, useEffect } from "react";
import { api } from "../api";
import type { ArticleMeta } from "../types";
import ArticleCard from "../components/ArticleCard";

interface ArticleListProps {
  onNavigate: (page: "home" | "articles" | "article" | "tool" | "my" | "about", id?: number) => void;
}

export default function ArticleList({ onNavigate }: ArticleListProps) {
  const [articles, setArticles] = useState<ArticleMeta[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getArticles(1, 50)
      .then((d) => setArticles(d.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="flex items-center gap-3 mb-8">
        <span className="text-accent font-mono text-lg">? ARTICLES</span>
        <div className="flex-1 h-px bg-dark-700" />
        <span className="text-xs text-gray-600 font-mono">{articles.length} posts</span>
      </div>

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
          {[...articles].reverse().map((article, i) => (
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
