import re

path = r"D:\Git_repository\hwt_blog\frontend\src\components\Navbar.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_logo = """        {/* Logo */}
        <button
          onClick={() => onNavigate("home")}
          className="flex items-center gap-2 text-accent font-bold text-lg tracking-widest glitch-text"
        >
          <span>HWT</span>
          <span className="text-xs text-gray-500 border border-dark-600 px-1 py-0.5 rounded">
            v1.0
          </span>
        </button>"""

new_logo = """        {/* Logo */}
        <button
          onClick={() => onNavigate("home")}
          className="group relative flex items-center gap-2 font-bold tracking-widest"
          onMouseDown={(e) => {
            const el = e.currentTarget;
            el.classList.remove("animate-logo-click");
            void el.offsetWidth;
            el.classList.add("animate-logo-click");
          }}
        >
          {/* Background glow */}
          <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-accent/10 via-transparent to-neon-blue/10 blur-xl" />

          {/* HWT letters with individual bounce */}
          <span className="relative text-lg text-accent inline-flex gap-0.5">
            {"HWT".split("").map((letter, i) => (
              <span
                key={i}
                className="inline-block animate-logo-bounce hover:scale-125 transition-transform duration-200"
                style={{ animationDelay: `${i * 0.15}s` }}
              >
                {letter}
              </span>
            ))}
          </span>

          {/* v1.0 badge */}
          <span className="relative text-[10px] text-gray-500 border border-dark-600 px-1.5 py-0.5 rounded-sm font-mono tracking-normal transition-all duration-300 group-hover:border-accent/40 group-hover:text-accent/60 group-hover:bg-accent/5 group-hover:scale-105">
            v1.0
          </span>

          {/* Click ripple */}
          <span className="absolute inset-0 rounded-lg pointer-events-none overflow-hidden">
            <span className="absolute inset-0 rounded-lg bg-accent/0 group-active:bg-accent/20 transition-colors duration-150" />
          </span>
        </button>"""

content = content.replace(old_logo, new_logo)

# Add keyframe animations via a style tag or tailwind config
# Inject @keyframes into the component via a <style> tag
# Find a good place - after the imports
old_imports = """import { useState } from "react";"""
new_imports = """import { useState } from "react";

const LOGO_STYLES = `
@keyframes logo-bounce {
  0%, 100% { transform: translateY(0) scaleY(1) scaleX(1); }
  15% { transform: translateY(-3px) scaleY(0.85) scaleX(1.15); }
  30% { transform: translateY(0) scaleY(1.1) scaleX(0.95); }
  45% { transform: translateY(-1px) scaleY(0.95) scaleX(1.05); }
  60% { transform: translateY(0) scaleY(1) scaleX(1); }
}
@keyframes logo-click {
  0% { transform: scale(1); }
  20% { transform: scale(0.85); }
  40% { transform: scale(1.15); }
  60% { transform: scale(0.95); }
  80% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
`;"""

content = content.replace(old_imports, new_imports)

# Add style tag injection and animation class
# Find the return statement and add style tag at the top
old_return = """  return ("""
new_return = """  return (
      <style>{LOGO_STYLES}</style>"""

content = content.replace(old_return, new_return)

# Add the animate-logo-click class via tailwind or inline
# We defined it in keyframes, but need to trigger it. We'll use inline style or classList.

# Actually, the onMouseDown already uses classList.add("animate-logo-click")
# But this class isn't defined in Tailwind's config, so we need to add it
# Let's add the class definition inline

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Navbar logo redesigned with animations")
