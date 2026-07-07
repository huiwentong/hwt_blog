import type { ArticleMeta } from "../types";

interface ArticleCardProps {
  article: ArticleMeta;
  index: number;
  onClick: (id: number) => void;
}

export default function ArticleCard({ article, index, onClick }: ArticleCardProps) {
  return (
    <div className="flex items-start gap-4 group cursor-pointer" onClick={() => onClick(article.id)}>
      {/* timeline dot + line */}
      <div className="flex flex-col items-center shrink-0">
        <div className="w-4 h-4 rounded-full border-2 border-accent bg-dark-950 group-hover:bg-accent transition-colors z-10" />
        {index > 0 && (
          <div className="w-0.5 flex-1 timeline-line mt-1" style={{ minHeight: "100%" }} />
        )}
      </div>

      {/* card */}
      <div className="flex-1 terminal-card rounded-lg p-5 mb-6 group-hover:-translate-y-0.5 transition-all">
        <div className="flex items-center gap-3 text-xs text-gray-500 mb-2 font-mono">
          <span className="text-accent">?</span>
          <span>{article.created_at?.split("T")[0] || "unknown"}</span>
          <span className="text-dark-600">|</span>
          <span className="text-neon-blue">{article.category}</span>
          <span className="text-dark-600">|</span>
          <span className="text-gray-600">?? {article.views}</span>
        </div>

        <h3 className="text-lg font-bold text-gray-100 group-hover:text-accent transition-colors mb-2 font-mono tracking-tight">
          {article.title}
        </h3>

        <p className="text-sm text-gray-400 leading-relaxed mb-3 line-clamp-2">
          {article.summary}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex gap-1.5 flex-wrap">
            {article.tags?.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 text-xs rounded bg-dark-700 text-neon-purple font-mono"
              >
                #{tag}
              </span>
            ))}
          </div>
          <span className="text-xs text-gray-500 font-mono">
            {article.author}
          </span>
        </div>
      </div>
    </div>
  );
}
