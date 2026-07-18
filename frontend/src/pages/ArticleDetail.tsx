import { useState, useEffect } from "react";
import { api } from "../api";
import type { ArticleMeta, Comment } from "../types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import Sidebar from "../components/Sidebar";

interface ArticleDetailProps {
  id: number;
  onBack: () => void;
  onNavigate: (page: string, id?: number) => void;
}

function parseUA(ua: string): { os: string; browser: string } {
  let os = "Unknown";
  let browser = "Unknown";

  if (/Windows NT 10/.test(ua)) os = "Windows 10";
  else if (/Windows NT 11/.test(ua)) os = "Windows 11";
  else if (/Windows NT 6\.3/.test(ua)) os = "Windows 8.1";
  else if (/Windows NT 6\.1/.test(ua)) os = "Windows 7";
  else if (/Mac OS X/.test(ua)) {
    const m = ua.match(/Mac OS X (\d+[._]\d+)/);
    os = m ? `macOS ${m[1].replace("_", ".")}` : "macOS";
  } else if (/Linux/.test(ua) && !/Android/.test(ua)) os = "Linux";
  else if (/Android/.test(ua)) {
    const m = ua.match(/Android (\d+\.?\d*)/);
    os = m ? `Android ${m[1]}` : "Android";
  } else if (/iPhone|iPad/.test(ua)) {
    const m = ua.match(/OS (\d+[._]\d+)/);
    os = m ? `iOS ${m[1].replace("_", ".")}` : "iOS";
  }

  if (/Edg\//.test(ua)) {
    const m = ua.match(/Edg\/(\d+)/);
    browser = m ? `Edge ${m[1]}` : "Edge";
  } else if (/Chrome/.test(ua)) {
    const m = ua.match(/Chrome\/(\d+)/);
    browser = m ? `Chrome ${m[1]}` : "Chrome";
  } else if (/Firefox/.test(ua)) {
    const m = ua.match(/Firefox\/(\d+)/);
    browser = m ? `Firefox ${m[1]}` : "Firefox";
  } else if (/Safari/.test(ua)) {
    const m = ua.match(/Version\/(\d+)/);
    browser = m ? `Safari ${m[1]}` : "Safari";
  }

  return { os, browser };
}

export default function ArticleDetail({ id, onBack, onNavigate }: ArticleDetailProps) {
  const [article, setArticle] = useState<ArticleMeta | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newAuthor, setNewAuthor] = useState("");
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const [adjacent, setAdjacent] = useState<{ prev: { id: number; title: string } | null; next: { id: number; title: string } | null }>({ prev: null, next: null });

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getArticle(id),
      api.getComments(id),
      api.getAdjacentArticles(id),
    ])
      .then(([a, c, adj]) => {
        setArticle(a);
        setComments(c);
        setAdjacent(adj);
        document.title = `${a.title} — HWT BLOG`;
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  const handlePostComment = async () => {
    if (!newAuthor.trim() || !newComment.trim() || submitting) return;
    setSubmitting(true);
    setSubmitted(false);
    try {
      await api.postComment(id, newAuthor, newComment);
      const updated = await api.getComments(id);
      setComments(updated);
      setNewAuthor("");
      setNewComment("");
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    } catch {
      // ignore
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-20">
        <div className="text-accent font-mono text-sm animate-pulse">$ loading article...</div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-600 font-mono text-sm">// Article not found</p>
        <button onClick={onBack} className="mt-4 text-accent underline font-mono text-sm">
          $ go_back()
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-8">
      {/* Main article */}
      <div className="flex-1 min-w-0">
        <button
          onClick={onBack}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-accent font-mono mb-6 transition-colors"
        >
          ← $ go_back()
        </button>

        <article className="terminal-card rounded-lg p-6 md:p-8">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 text-xs text-gray-500 font-mono mb-3">
              <span className="text-accent">?</span>
              <span>{article.created_at?.split("T")[0]}</span>
              <span className="text-dark-600">|</span>
              <span className="text-neon-blue">{article.category}</span>
            </div>

            <h1 className="text-2xl md:text-3xl font-bold text-gray-100 font-mono mb-3">
              {article.title}
            </h1>

            <p className="text-gray-400 text-sm leading-relaxed mb-4">{article.summary}</p>

            <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
              <div className="flex gap-1.5 flex-wrap">
                {article.tags?.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 rounded bg-dark-700 text-neon-purple"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
              <span className="text-dark-600">|</span>
              <span className="text-gray-500">?? {article.author}</span>
              <span className="text-dark-600">|</span>
              <span className="text-gray-500">?? {article.views}</span>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-dark-700 my-6" />

          {/* Content */}
          <div className="prose prose-invert max-w-none text-gray-300 text-sm leading-relaxed font-mono">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                h2: ({ children, ...props }) => {
                  const id = String(children)
                    .toLowerCase()
                    .replace(/[^\w\u4e00-\u9fff]+/g, "-")
                    .replace(/^-+|-+$/g, "");
                  return <h2 id={id} className="text-lg font-bold text-gray-100 mt-8 mb-4 font-mono" {...props}>{children}</h2>;
                },
                h3: ({ children, ...props }) => {
                  const id = String(children)
                    .toLowerCase()
                    .replace(/[^\w\u4e00-\u9fff]+/g, "-")
                    .replace(/^-+|-+$/g, "");
                  return <h3 id={id} className="text-base font-bold text-gray-200 mt-6 mb-3 font-mono" {...props}>{children}</h3>;
                },
              }}
            >{article.content}</ReactMarkdown>
          </div>

          {/* Divider */}
          <div className="border-t border-dark-700 my-6" />

          {/* Previous / Next Navigation */}
          <nav className="flex items-stretch justify-between gap-3 sm:gap-4">
            {adjacent.prev ? (
              <button
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: "instant" });
                  onNavigate("article", adjacent.prev!.id);
                }}
                className="group relative flex-1 flex flex-col items-start gap-1.5 p-4 sm:p-5 rounded-xl border border-dark-700 bg-dark-800/30 overflow-hidden transition-all duration-500 hover:border-accent/40 hover:bg-dark-800/80 hover:shadow-[0_0_25px_-5px_rgba(0,255,255,0.15)] text-left"
              >
                {/* Background gradient that slides in on hover */}
                <div className="absolute inset-0 bg-gradient-to-r from-accent/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Arrow icon column */}
                <div className="flex items-center gap-2 relative z-10">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full border border-dark-600 group-hover:border-accent/50 group-hover:bg-accent/10 transition-all duration-400">
                    <svg className="w-3.5 h-3.5 text-gray-500 group-hover:text-accent transition-colors duration-400 -translate-x-[1px] group-hover:-translate-x-[3px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                    </svg>
                  </span>
                  <span className="text-[10px] font-mono tracking-widest uppercase text-gray-500 group-hover:text-accent/80 transition-colors duration-400">
                    Previous
                  </span>
                </div>

                {/* Title */}
                <span className="relative z-10 text-xs sm:text-sm font-mono text-gray-300 group-hover:text-white leading-relaxed line-clamp-2 transition-colors duration-400 ml-0 group-hover:ml-1">
                  {adjacent.prev.title}
                </span>

                {/* Bottom border accent that expands on hover */}
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-[2px] bg-gradient-to-r from-transparent via-accent/60 to-transparent group-hover:w-3/4 transition-all duration-500 rounded-full" />
              </button>
            ) : (
              <div className="flex-1" />
            )}

            {adjacent.next ? (
              <button
                onClick={() => {
                  window.scrollTo({ top: 0, behavior: "instant" });
                  onNavigate("article", adjacent.next!.id);
                }}
                className="group relative flex-1 flex flex-col items-end gap-1.5 p-4 sm:p-5 rounded-xl border border-dark-700 bg-dark-800/30 overflow-hidden transition-all duration-500 hover:border-neon-blue/40 hover:bg-dark-800/80 hover:shadow-[0_0_25px_-5px_rgba(0,150,255,0.15)] text-right"
              >
                {/* Background gradient */}
                <div className="absolute inset-0 bg-gradient-to-l from-neon-blue/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Arrow icon column */}
                <div className="flex items-center gap-2 relative z-10 flex-row-reverse">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full border border-dark-600 group-hover:border-neon-blue/50 group-hover:bg-neon-blue/10 transition-all duration-400">
                    <svg className="w-3.5 h-3.5 text-gray-500 group-hover:text-neon-blue transition-colors duration-400 translate-x-[1px] group-hover:translate-x-[3px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                  </span>
                  <span className="text-[10px] font-mono tracking-widest uppercase text-gray-500 group-hover:text-neon-blue/80 transition-colors duration-400">
                    Next
                  </span>
                </div>

                {/* Title */}
                <span className="relative z-10 text-xs sm:text-sm font-mono text-gray-300 group-hover:text-white leading-relaxed line-clamp-2 transition-colors duration-400 mr-0 group-hover:-mr-1">
                  {adjacent.next.title}
                </span>

                {/* Bottom border accent */}
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-[2px] bg-gradient-to-r from-transparent via-neon-blue/60 to-transparent group-hover:w-3/4 transition-all duration-500 rounded-full" />
              </button>
            ) : (
              <div className="flex-1" />
            )}
          </nav>
        </article>

        {/* Comments Section */}
        <div className="terminal-card rounded-lg p-6 mt-6">
          <h3 className="text-sm text-accent font-mono mb-4">
            ? COMMENTS ({comments.length})
          </h3>

          <div className="space-y-4 mb-6">
            {comments.length === 0 ? (
              <p className="text-xs text-gray-600 font-mono">// no comments yet. be the first.</p>
            ) : (
              comments.map((c) => {
                const { os, browser } = parseUA(c.user_agent || "");
                return (
                  <div key={c.id} className="border-b border-dark-700 pb-3 last:border-0">
                    <div className="flex items-center gap-2 text-xs text-gray-500 font-mono mb-1">
                      <span className="text-neon-purple">@{c.author}</span>
                      <span>?</span>
                      <span>{c.created_at?.split("T")[0]}</span>
                    </div>
                    <p className="text-xs text-gray-400 font-mono">{c.content}</p>
                    <div className="flex items-center gap-2 text-[10px] text-gray-600 font-mono mt-1.5">
                      {c.ip_address && <span>?? {c.ip_address}</span>}
                      {os !== "Unknown" && <span>?? {os}</span>}
                      {browser !== "Unknown" && <span>?? {browser}</span>}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Comment Form */}
          <div className="border-t border-dark-700 pt-4">
            <div className="text-xs text-gray-500 font-mono mb-3">// leave a comment</div>
            <input
              type="text"
              placeholder="your alias..."
              value={newAuthor}
              onChange={(e) => setNewAuthor(e.target.value)}
              className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-xs font-mono text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent mb-2"
            />
            <textarea
              placeholder="your thoughts..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              rows={3}
              className="w-full bg-dark-800 border border-dark-600 rounded px-3 py-2 text-xs font-mono text-gray-200 placeholder-gray-600 focus:outline-none focus:border-accent mb-2 resize-none"
            />
            <button
              onClick={handlePostComment}
              disabled={submitting}
              className={`px-4 py-1.5 text-xs font-mono rounded border transition-all ${
                submitting
                  ? "text-gray-600 border-dark-700 cursor-not-allowed"
                  : submitted
                  ? "text-green-400 border-accent-dim bg-dark-800"
                  : "text-accent border-dark-600 hover:bg-dark-800 hover:border-accent"
              }`}
            >
              {submitting ? (
                <><span className="inline-block w-2.5 h-2.5 border border-accent border-t-transparent rounded-full animate-spin mr-1.5" /> sending...</>
              ) : submitted ? (
                "✓ sent!"
              ) : (
                "$ submit()"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-full lg:w-72 shrink-0 sticky top-24 self-start">
        <Sidebar type="article" articleId={id} content={article.content} onArticleClick={(newId) => { window.scrollTo({ top: 0, behavior: "instant" }); onNavigate("article", newId); }} />
      </div>
    </div>
  );
}
