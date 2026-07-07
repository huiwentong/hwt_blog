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

export default function My() {
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [filter, setFilter] = useState<MediaFilter>("all");

  useEffect(() => {
    const type = filter === "all" ? undefined : filter;
    api.getMedia(type).then(setMedia).catch(() => {});
  }, [filter]);

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
          {media.map((item) => (
            <div key={item.id} className="terminal-card rounded-lg overflow-hidden group">
              <div className="aspect-video bg-dark-800 flex items-center justify-center text-4xl text-dark-600 overflow-hidden">
                {item.cover ? (
                  <img src={item.cover} alt={item.title} className="w-full h-full object-cover" />
                ) : (
                  <span>{item.type === "music" ? "?" : item.type === "photo" ? "?" : "?"}</span>
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
          ))}
        </div>
      )}
    </div>
  );
}
