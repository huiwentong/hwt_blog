import { useState, useEffect } from "react";
import { api } from "../api";
import type { ArticleMeta } from "../types";
import ArticleCard from "../components/ArticleCard";
import Sidebar from "../components/Sidebar";

interface HomeProps {
  onNavigate: (page: "home" | "articles" | "article" | "tool" | "my" | "about", id?: number) => void;
}

export default function Home({ onNavigate }: HomeProps) {
  const [articles, setArticles] = useState<ArticleMeta[]>([]);

  useEffect(() => {
    api.getArticles(1, 10).then((d) => setArticles(d.items)).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col lg:flex-row gap-8">
      {/* Main content */}
      <div className="flex-1">
        {/* Hero */}
        <section className="mb-10 border-b border-dark-700 pb-8">
          <div className="mb-2 text-accent text-sm font-mono glitch-text tracking-widest">
            $ SYSTEM_INIT — HWT BLOG v1.0
          </div>
          <h1 className="text-3xl md:text-4xl font-bold font-mono tracking-tight text-gray-100 mb-3">
            <span className="text-accent">HWT</span> — <span className="font-alibaba">惠文通的小屋</span>
          </h1>
          <p className="text-gray-500 font-mono text-sm leading-relaxed max-w-2xl">
            &gt; 代码、文字、音乐与电影的聚合体。<br />
            &gt; 在这里，每篇文章都是一次终端输出，每个分享都是一段开源协议。
            <span className="animate-pulse text-accent"> _</span>
          </p>
        </section>

        {/* Timeline section title */}
        <div className="flex items-center gap-3 mb-6">
          <span className="text-accent font-mono text-sm">❯ LATEST_POSTS</span>
          <div className="flex-1 h-px bg-dark-700" />
        </div>

        {/* Timeline */}
        <div className="relative pl-2">
          {articles.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-4xl mb-4 text-dark-600">{">>>"}</div>
              <p className="text-gray-600 font-mono text-sm">// No posts yet. Stay tuned.</p>
            </div>
          ) : (
            articles.map((article, i) => (
              <ArticleCard
                key={article.id}
                article={article}
                index={articles.length - i - 1}
                onClick={(id) => onNavigate("article", id)}
              />
            ))
          )}
        </div>

        {/* View all */}
        {articles.length > 0 && (
          <div className="text-center mt-4">
            <button
              onClick={() => onNavigate("articles")}
              className="px-6 py-2 text-sm font-mono text-accent border border-dark-600 rounded hover:bg-dark-800 hover:border-accent transition-all tracking-wider"
            >
              $ view_all_posts()
            </button>
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="w-full lg:w-72 shrink-0">
        <Sidebar type="site" />
      </div>
    </div>
  );
}
