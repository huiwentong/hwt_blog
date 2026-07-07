import { useState, useEffect } from "react";
import { api } from "../api";
import type { ToolItem } from "../types";

export default function Tool() {
  const [tools, setTools] = useState<ToolItem[]>([]);

  useEffect(() => {
    api.getTools().then(setTools).catch(() => {});
  }, []);

  return (
    <div>
      <div className="flex items-center gap-3 mb-8">
        <span className="text-accent font-mono text-lg">? TOOLS</span>
        <div className="flex-1 h-px bg-dark-700" />
        <span className="text-xs text-gray-600 font-mono">{tools.length} tools</span>
      </div>

      <section className="mb-8">
        <p className="text-gray-500 font-mono text-xs leading-relaxed">
          &gt; 自己开发的一些小工具分享，每一个都经过精心打磨。
        </p>
      </section>

      {tools.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4 text-dark-600">?</div>
          <p className="text-gray-600 font-mono text-sm">// No tools shared yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tools.map((tool) => (
            <a
              key={tool.id}
              href={tool.url}
              target="_blank"
              rel="noopener noreferrer"
              className="terminal-card rounded-lg p-5 hover:border-accent transition-all group"
            >
              <div className="text-2xl mb-3">{tool.icon}</div>
              <h3 className="text-sm font-bold text-gray-100 mb-2 font-mono group-hover:text-accent transition-colors">
                {tool.name}
              </h3>
              <p className="text-xs text-gray-500 font-mono leading-relaxed">
                {tool.description}
              </p>
              <div className="mt-3">
                <span className="text-xs px-2 py-0.5 rounded bg-dark-700 text-neon-blue font-mono">
                  {tool.category}
                </span>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
