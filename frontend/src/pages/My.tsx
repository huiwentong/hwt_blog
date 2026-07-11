import { useState, useEffect } from "react";
import { api } from "../api";
import type { MediaItem } from "../types";

type MediaFilter = "all" | "music" | "photo" | "movie";

const filters: { key: MediaFilter; label: string }[] = [
  { key: "all", label: "ALL" },
  { key: "music", label: "? MUSIC" },
  { key: "photo", label: "? PHOTO" },
  { key: "movie", label: "? MOVIE" },
];

const typeIcons: Record<string, string> = {
  music: "?",
  photo: "?",
  movie: "?",
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

export default function My() {
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [filter, setFilter] = useState<MediaFilter>("all");
  const [selected, setSelected] = useState<MediaItem | null>(null);
  const [hoveredId, setHoveredId] = useState<number | null>(null);
  const [failedPreviews, setFailedPreviews] = useState<Set<number>>(new Set());

  useEffect(() => {
    const type = filter === "all" ? undefined : filter;
    api.getMedia(type).then(setMedia).catch(() => {});
  }, [filter]);

  // Close modal on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  // Pause hovered video when modal opens
  useEffect(() => {
    if (selected) setHoveredId(null);
  }, [selected]);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <span className="text-accent font-mono text-lg">? MY SPACE</span>
        <div className="flex-1 h-px bg-dark-700" />
      </div>

      <section className="mb-8">
        <p className="text-gray-500 font-mono text-xs leading-relaxed">
          &gt; 音乐、照片、电影——那些塑造我的碎片。
        </p>
      </section>

      {/* Filter tabs */}
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

      {media.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-dark-600">?</div>
          <p className="text-gray-600 font-mono text-sm">// No media shared yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {media.map((item) => {
            const isHovered = hoveredId === item.id && !failedPreviews.has(item.id);
            const vidPreview = item.url && isVideo(item.url);
            return (
              <div
                key={item.id}
                className="terminal-card rounded-lg overflow-hidden group cursor-pointer relative"
                onClick={() => setSelected(item)}
                onMouseEnter={() => setHoveredId(item.id)}
                onMouseLeave={() => setHoveredId(null)}
              >
                <div className="aspect-video bg-dark-800 flex items-center justify-center text-4xl text-dark-600 overflow-hidden relative">
                  {isVideo(item.url || "") && !item.cover && (
                    <div className="absolute inset-0 flex items-center justify-center z-10">
                      <span className="text-5xl opacity-60">{typeIcons.movie}</span>
                    </div>
                  )}

                  {isHovered && vidPreview ? (
                    <video
                      src={previewUrl(item.url)}
                      muted
                      autoPlay
                      loop
                      playsInline
                      className="w-full h-full object-cover"
                      onError={() => {
                        setFailedPreviews((prev) => new Set(prev).add(item.id));
                      }}
                    />
                  ) : item.cover ? (
                    <div className="w-full h-full img-placeholder">
                      <img
                        src={item.cover}
                        alt={item.title}
                        loading="lazy"
                        decoding="async"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ) : (
                    <span>{typeIcons[item.type] || "?"}</span>
                  )}

                  {/* Play overlay for movies */}
                  {vidPreview && !isHovered && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="text-4xl">?</span>
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="text-sm font-bold text-gray-100 font-mono group-hover:text-accent transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-xs text-gray-500 font-mono mt-1 line-clamp-2">
                    {item.description}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs px-1.5 py-0.5 rounded bg-dark-700 text-neon-blue font-mono">
                      {item.type}
                    </span>
                    <span className="text-xs text-gray-600 font-mono">
                      {item.created_at?.split("T")[0]}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Detail Modal */}
      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => setSelected(null)}
        >
          <div
            className="terminal-card rounded-lg w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-dark-700">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{typeIcons[selected.type] || "?"}</span>
                <span className="text-xs text-accent font-mono">// detail</span>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-gray-500 hover:text-gray-300 font-mono text-sm px-2 py-1 border border-dark-600 rounded hover:border-accent transition-all"
              >
                $ close()
              </button>
            </div>

            {/* Media Player / Cover */}
            <div className="bg-dark-900">
              {selected.type === "music" && selected.url && !isVideo(selected.url) && (
                <div className="p-6 flex flex-col items-center gap-4">
                  <span className="text-6xl">{typeIcons.music}</span>
                  <audio
                    controls
                    autoPlay
                    className="w-full max-w-md"
                    src={selected.url}
                  >
                    您的浏览器不支持音频播放。
                  </audio>
                </div>
              )}

              {(selected.type === "movie" || (selected.url && isVideo(selected.url))) && (
                <div className="w-full">
                  <video
                    controls
                    autoPlay
                    className="w-full max-h-[60vh] object-contain bg-black"
                    src={selected.url}
                  >
                    您的浏览器不支持视频播放。
                  </video>
                </div>
              )}

              {selected.type === "photo" && selected.cover && !isVideo(selected.url || "") && (
                <div className="w-full">
                  <div className="w-full img-placeholder">
                    <img
                      src={selected.cover}
                      alt={selected.title}
                      className="w-full max-h-[60vh] object-contain"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Body */}
            <div className="p-4 space-y-4">
              <div>
                <h2 className="text-lg font-bold text-gray-100 font-mono">{selected.title}</h2>
                <span className="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-dark-700 text-neon-blue font-mono">
                  {selected.type}
                </span>
              </div>

              {selected.description && (
                <div>
                  <div className="text-[10px] text-gray-600 font-mono mb-1">// description</div>
                  <p className="text-sm text-gray-400 font-mono leading-relaxed">{selected.description}</p>
                </div>
              )}

              {selected.url && (
                <div>
                  <div className="text-[10px] text-gray-600 font-mono mb-1">
                    {selected.url !== selected.cover ? "// source" : "// url"}
                  </div>
                  <a
                    href={selected.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-accent font-mono underline break-all hover:text-accent-dim transition-colors"
                  >
                    {selected.url}
                  </a>
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
