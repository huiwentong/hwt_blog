import { useState, useEffect, useRef, useCallback } from "react";
import { api } from "../api";
import type { MediaItem } from "../types";

type MediaFilter = "all" | "music" | "photo" | "movie";

const filters: { key: MediaFilter; label: string }[] = [
  { key: "all", label: "ALL" },
  { key: "music", label: "♪ MUSIC" },
  { key: "photo", label: "◷ PHOTO" },
  { key: "movie", label: "▶ MOVIE" },
];

const typeIcons: Record<string, string> = {
  music: "♪",
  photo: "◷",
  movie: "▶",
};

const videoExts = [".mp4", ".mkv", ".avi", ".mov", ".webm"];

function isVideo(url: string): boolean {
  const u = url.toLowerCase();
  return videoExts.some((ext) => u.includes(ext));
}

function previewUrl(url: string): string {
  const dot = url.lastIndexOf(".");
  if (dot === -1) return url;
  return url.slice(0, dot) + "_preview" + url.slice(dot);
}

const PAGE_SIZE = 20;

const defaultRatios: Record<string, number> = {
  music: 1,
  photo: 4 / 3,
  movie: 16 / 9,
};

function spanClass(ar: number | undefined, type: string, idx: number): string {
  const r = ar || defaultRatios[type] || 1;
  if (r > 2.0) return "grid-span-featured";
  if (r > 1.5) return "grid-span-wide";
  if (r < 0.55) return "grid-span-xtall";
  if (r < 0.75) return "grid-span-tall";
  if (idx > 0 && idx % 4 === 0) return "grid-span-tall";
  if (idx > 0 && idx % 7 === 0) return "grid-span-featured";
  return "";
}

export default function My() {
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [filter, setFilter] = useState<MediaFilter>("all");
  const [selected, setSelected] = useState<MediaItem | null>(null);
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [failedPreviews, setFailedPreviews] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [aspectRatios, setAspectRatios] = useState<Record<number, number>>({});
  const sentinelRef = useRef<HTMLDivElement>(null);
  const loadingRef = useRef(false);

  const fetchMedia = useCallback(async (pageNum: number, mediaFilter: MediaFilter, append: boolean) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const type = mediaFilter === "all" ? undefined : mediaFilter;
      const res = await api.getMedia(type, pageNum, PAGE_SIZE);
      if (res && Array.isArray(res.items)) {
        if (append) {
          setMedia(prev => [...prev, ...res.items]);
        } else {
          setMedia(res.items);
        }
        setTotal(res.total);
        setPage(pageNum);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
      setInitialLoading(false);
      loadingRef.current = false;
    }
  }, []);

  useEffect(() => {
    setInitialLoading(true);
    setMedia([]);
    setPage(1);
    setAspectRatios({});
    fetchMedia(1, filter, false);
  }, [filter, fetchMedia]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting && !loadingRef.current && media.length < total) {
          fetchMedia(page + 1, filter, true);
        }
      },
      { rootMargin: "400px" }
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [media.length, total, page, filter, fetchMedia]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  useEffect(() => {
    if (selected) setHoveredId(null);
  }, [selected]);

  const handleMediaLoad = (id: number, w: number, h: number) => {
    if (w && h) {
      setAspectRatios(prev => ({ ...prev, [id]: w / h }));
    }
  };

  const remaining = total - media.length;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-accent font-mono text-lg">◈ MY SPACE</span>
        <div className="flex-1 h-px bg-dark-700" />
      </div>

      <section className="mb-8">
        <p className="text-gray-500 font-mono text-xs leading-relaxed">
          &gt; 音乐、照片、电影——那些塑造我的碎片。
        </p>
      </section>

      <div className="flex flex-wrap gap-2 mb-6">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 text-xs font-mono rounded border transition-all ${
              filter === f.key
                ? "text-accent border-accent bg-dark-800"
                : "text-gray-500 border-dark-700 hover:text-gray-300 hover:border-dark-600"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {initialLoading ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-dark-600">◌</div>
          <p className="text-gray-600 font-mono text-sm">// Loading...</p>
        </div>
      ) : media.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-dark-600">◇</div>
          <p className="text-gray-600 font-mono text-sm">// No media shared yet.</p>
        </div>
      ) : (
        <>
          <div className="masonry-grid">
            {media.map((item, idx) => {
              const ar = aspectRatios[item.id];
              const sc = spanClass(ar, item.type, idx);
              const isHovered = hoveredId === item.id && !failedPreviews.has(item.id);
              const vidPreview = item.url && isVideo(item.url);
              const hasCover = !!item.cover;

              return (
                <div
                  key={item.id}
                  className={`masonry-item ${sc}`}
                  onClick={() => setSelected(item)}
                  onMouseEnter={() => setHoveredId(item.id)}
                  onMouseLeave={() => setHoveredId(null)}
                >
                  <div className="w-full h-full relative rounded-lg overflow-hidden bg-dark-800 terminal-card">
                    {hasCover ? (
                      <img
                        src={item.cover}
                        alt={item.title}
                        loading="lazy"
                        decoding="async"
                        className={`w-full h-full object-cover transition-opacity duration-300 ${
                          isHovered && vidPreview ? "opacity-0" : "opacity-100"
                        }`}
                        onLoad={(e) => {
                          const img = e.currentTarget;
                          handleMediaLoad(item.id, img.naturalWidth, img.naturalHeight);
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-dark-600 gap-2">
                        <span className="text-5xl">{typeIcons[item.type] || "◇"}</span>
                        <span className="text-[10px] font-mono uppercase tracking-widest opacity-50">
                          {item.type}
                        </span>
                      </div>
                    )}

                    {vidPreview && (
                      <video
                        src={previewUrl(item.url)}
                        muted
                        autoPlay
                        loop
                        playsInline
                        className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
                          isHovered ? "opacity-100" : "opacity-0 pointer-events-none"
                        }`}
                        onError={() => setFailedPreviews(prev => new Set(prev).add(item.id))}
                        onLoadedMetadata={(e) => {
                          const v = e.currentTarget;
                          handleMediaLoad(item.id, v.videoWidth, v.videoHeight);
                        }}
                      />
                    )}

                    <div className="absolute top-2 left-2 z-20">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-dark-900/80 text-neon-blue font-mono backdrop-blur-sm">
                        {item.type}
                      </span>
                    </div>

                    <div className="absolute bottom-0 left-0 right-0 z-20 p-2.5 bg-gradient-to-t from-dark-950/95 via-dark-950/60 to-transparent pointer-events-none">
                      <h3 className="text-[11px] font-mono text-gray-200 leading-tight line-clamp-1">
                        {item.title}
                      </h3>
                      <div className="flex items-center justify-between mt-0.5">
                        <span className="text-[10px] text-gray-400 font-mono">
                          {item.created_at?.split("T")[0]}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div ref={sentinelRef} className="w-full py-8 flex justify-center">
            {loading && (
              <div className="flex items-center gap-2 text-gray-500 font-mono text-xs">
                <span className="inline-block w-3 h-3 border border-accent border-t-transparent rounded-full animate-spin" />
                loading...
              </div>
            )}
            {!loading && remaining > 0 && (
              <span className="text-gray-600 font-mono text-xs">
                ↓ scroll for more ({remaining} left)
              </span>
            )}
            {remaining <= 0 && !loading && (
              <span className="text-gray-600 font-mono text-xs">— end —</span>
            )}
          </div>
        </>
      )}

      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => setSelected(null)}
        >
          <div
            className="terminal-card rounded-lg w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-dark-700">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{typeIcons[selected.type] || "◇"}</span>
                <span className="text-xs text-accent font-mono">// detail</span>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-gray-500 hover:text-gray-300 font-mono text-sm px-2 py-1 border border-dark-600 rounded hover:border-accent transition-all"
              >
                $ close()
              </button>
            </div>

            <div className="bg-dark-900">
              {selected.type === "music" && selected.url && !isVideo(selected.url) && (
                <div className="p-6 flex flex-col items-center gap-4">
                  <span className="text-6xl">{typeIcons.music}</span>
                  <audio controls autoPlay className="w-full max-w-md" src={selected.url} />
                </div>
              )}
              {(selected.type === "movie" || (selected.url && isVideo(selected.url))) && (
                <div className="w-full">
                  <video controls autoPlay className="w-full max-h-[60vh] object-contain bg-black" src={selected.url} />
                </div>
              )}
              {selected.type === "photo" && selected.cover && !isVideo(selected.url || "") && (
                <div className="w-full">
                  <div className="w-full img-placeholder">
                    <img src={selected.cover} alt={selected.title} className="w-full max-h-[60vh] object-contain" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 space-y-4">
              <div>
                <h2 className="text-lg font-bold text-gray-100 font-mono">{selected.title}</h2>
                <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-dark-700 text-neon-blue font-mono">{selected.type}</span>
              </div>
              {selected.description && (
                <div>
                  <div className="text-[10px] text-gray-600 font-mono mb-1">// description</div>
                  <p className="text-sm text-gray-400 font-mono leading-relaxed">{selected.description}</p>
                </div>
              )}
              {selected.url && (
                <div>
                  <div className="text-[10px] text-gray-600 font-mono mb-1">{selected.url !== selected.cover ? "// source" : "// url"}</div>
                  <a href={selected.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent font-mono underline break-all hover:text-accent-dim transition-colors">{selected.url}</a>
                </div>
              )}
              <div className="flex items-center gap-4 text-[10px] text-gray-600 font-mono pt-2 border-t border-dark-700">
                <span>id: {selected.id}</span>
                <span>date: {selected.created_at?.split("T")[0]}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
