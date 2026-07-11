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

export default function Navbar({ currentPage, onNavigate }: NavbarProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-dark-950/90 backdrop-blur-md border-b border-dark-700">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <button
          onClick={() => onNavigate("home")}
          className="flex items-center gap-2 text-accent font-bold text-lg tracking-widest glitch-text"
        >
          <span>HWT</span>
          <span className="text-xs text-gray-500 border border-dark-600 px-1 py-0.5 rounded">
            v1.0
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
  );
}
