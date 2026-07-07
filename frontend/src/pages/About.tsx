import { useState, useEffect } from "react";

const easterEgg = [
  "> init system...",
  "> loading identity matrix...",
  "> NEXUS core v1.0 detected.",
  "> ",
  '> 我是一个热爱代码、音乐与电影的独立开发者。',
  "> 我相信技术是表达思想的终极媒介。",
  "> 这个博客是我数字生活的剪影——",
  "> 每一行代码都是一首诗，每一段文字都是一次冒险。",
  "> ",
  '> "The best way to predict the future is to invent it."',
  ">   — Alan Kay",
  "> ",
  "> SYSTEM SIGNATURE:",
  "> ┌──────────────────────────────┐",
  "> │  NEXUS_BLOG / v1.0           │",
  "> │  ARCH: x64_dark              │",
  "> │  STATUS: ONLINE              │",
  "> │  UPTIME: ∞                   │",
  "> └──────────────────────────────┘",
  "> ",
  "> $ shutdown --easter-egg",
];

export default function About() {
  const [lines, setLines] = useState<string[]>([]);
  const [lineIndex, setLineIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (lineIndex < easterEgg.length) {
      const timer = setTimeout(() => {
        setLines((prev) => [...prev, easterEgg[lineIndex]]);
        setLineIndex((i) => i + 1);
      }, 200);
      return () => clearTimeout(timer);
    } else {
      setIsComplete(true);
    }
  }, [lineIndex]);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <span className="text-accent font-mono text-lg">❯ ABOUT</span>
        <div className="flex-1 h-px bg-dark-700" />
      </div>

      {!isComplete && (
        <div className="mb-6 terminal-card rounded-lg p-4">
          <p className="text-xs text-gray-500 font-mono">
            $ system_boot_sequence initiated...
            <span className="animate-pulse text-accent"> _</span>
          </p>
        </div>
      )}

      <div className="terminal-card rounded-lg p-6 md:p-8 min-h-[300px]">
        <div className="text-xs md:text-sm text-gray-400 font-mono leading-relaxed whitespace-pre-wrap">
          {lines.map((line, i) => (
            <div key={i} className={line.startsWith("> \"") ? "text-neon-purple" : line.includes("NEXUS") || line.includes("STATUS") || line.includes("ARCH") || line.includes("UPTIME") ? "text-accent" : ""}>
              {line}
            </div>
          ))}
          {!isComplete && (
            <span className="animate-pulse text-accent">▌</span>
          )}
        </div>

        {isComplete && (
          <div className="mt-8 pt-4 border-t border-dark-700">
            <button
              onClick={() => {
                setLines([]);
                setLineIndex(0);
                setIsComplete(false);
              }}
              className="text-xs font-mono text-gray-500 hover:text-accent transition-colors"
            >
              $ reboot_sequence()
            </button>
            <p className="text-xs text-gray-600 font-mono mt-4">
              © 2026 NEXUS BLOG — Made with ❤ and lots of caffeine.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
