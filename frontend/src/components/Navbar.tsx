import { useState } from "react";

type Page = "home" | "articles" | "article" | "tool" | "my" | "about";

interface NavbarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

const navItems: { key: Page; label: string; icon: string }[] = [
  { key: "home", label: "HOME", icon: "?" },
  { key: "articles", label: "ARTICLE", icon: "≡" },
  { key: "tool", label: "TOOL", icon: "?" },
  { key: "my", label: "MY", icon: "?" },
  { key: "about", label: "ABOUT", icon: "?" },
];

const LOGO_STYLES = `
@keyframes logo-bounce {
  0%, 100% { transform: translateY(0) scaleY(1) scaleX(1); }
  15% { transform: translateY(-4px) scaleY(0.8) scaleX(1.2); }
  30% { transform: translateY(0) scaleY(1.1) scaleX(0.9); }
  45% { transform: translateY(-2px) scaleY(0.95) scaleX(1.05); }
  60% { transform: translateY(0) scaleY(1) scaleX(1); }
}
@keyframes logo-click {
  0% { transform: scale(1); }
  15% { transform: scale(0.8) rotate(-3deg); }
  30% { transform: scale(1.2) rotate(2deg); }
  50% { transform: scale(0.9) rotate(-1deg); }
  70% { transform: scale(1.05); }
  100% { transform: scale(1) rotate(0deg); }
}
@keyframes logo-glow {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 0px rgba(0, 255, 255, 0)); }
  50% { filter: brightness(1.3) drop-shadow(0 0 8px rgba(0, 255, 255, 0.4)); }
}
.animate-logo-bounce { animation: logo-bounce 2.5s ease-in-out infinite; }
.animate-logo-click { animation: logo-click 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55) forwards; }
.animate-logo-glow { animation: logo-glow 3s ease-in-out infinite; }
`;

export default function Navbar({ currentPage, onNavigate }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogoClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const btn = e.currentTarget;
    btn.classList.remove("animate-logo-click");
    void btn.offsetWidth;
    btn.classList.add("animate-logo-click");
    onNavigate("home");
  };

  return (
    <>
      <style>{LOGO_STYLES}</style>
      <header className="sticky top-0 z-50 bg-dark-950/90 backdrop-blur-md border-b border-dark-700">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          {/* Logo */}
          <button
            onClick={handleLogoClick}
            className="group relative flex items-center gap-2 font-bold tracking-widest"
          >
            {/* Background glow on hover */}
            <span className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-500 bg-gradient-to-r from-accent/15 via-transparent to-neon-blue/15 blur-xl scale-110 group-hover:scale-125" />

            {/* Animated glow ring */}
            <span className="absolute -inset-2 rounded-xl border border-accent/0 group-hover:border-accent/20 transition-all duration-500 group-hover:animate-logo-glow" />

            {/* HWT letters with individual Q-bounce */}
            <span className="relative text-xl text-accent inline-flex gap-0.5">
              {"HWT".split("").map((letter, i) => (
                <span
                  key={i}
                  className="inline-block animate-logo-bounce hover:scale-[1.4] hover:text-white transition-all duration-200 cursor-pointer"
                  style={{ animationDelay: `${i * 0.2}s` }}
                >
                  {letter}
                </span>
              ))}
            </span>

            {/* v1.0 badge */}
            <span className="relative text-[10px] text-gray-500 border border-dark-600 px-1.5 py-0.5 rounded-sm font-mono tracking-normal transition-all duration-300 group-hover:border-accent/50 group-hover:text-accent/70 group-hover:bg-accent/10 group-hover:scale-110 group-hover:shadow-[0_0_12px_-2px_rgba(0,255,255,0.2)]">
              v1.0
            </span>

            {/* Click ripple overlay */}
            <span className="absolute inset-0 rounded-lg pointer-events-none overflow-hidden">
              <span className="absolute inset-0 rounded-lg bg-accent/0 group-active:bg-accent/25 transition-colors duration-150" />
            </span>
          </button>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive =
                currentPage === item.key ||
                (item.key === "articles" &&
                  (currentPage === "article" || currentPage === "articles"));
              return (
                <button
                  key={item.key}
                  onClick={() => onNavigate(item.key)}
                  className={`px-3 py-2 text-sm font-mono tracking-wider transition-all duration-200 rounded ${
                    isActive
                      ? "text-accent bg-dark-800 neon-border"
                      : "text-gray-400 hover:text-gray-200 hover:bg-dark-800/50"
                  }`}
                >
                  <span className="mr-1.5">{item.icon}</span>
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Mobile hamburger */}
          <button
            className="md:hidden text-gray-300 p-2"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <span className="font-mono text-lg">{menuOpen ? "?" : "?"}</span>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-dark-700 bg-dark-900">
            {navItems.map((item) => {
              const isActive = currentPage === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => {
                    onNavigate(item.key);
                    setMenuOpen(false);
                  }}
                  className={`block w-full text-left px-6 py-3 font-mono text-sm tracking-wider ${
                    isActive
                      ? "text-accent bg-dark-800"
                      : "text-gray-400 hover:text-gray-200 hover:bg-dark-800/50"
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              );
            })}
          </div>
        )}
      </header>
    </>
  );
}
