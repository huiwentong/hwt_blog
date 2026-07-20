import { useState, useEffect, useRef } from "react";
import { api } from "../api";
import type { ArticleMeta, SiteInfo } from "../types";

interface HomeProps {
  onNavigate: (page: "home" | "articles" | "article" | "tool" | "my" | "about", id?: number) => void;
}

// ─── Matrix Rain Canvas ─────────────────────────────────────────
function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const canvasRef2 = useRef<HTMLCanvasElement>(null);
  const mouseX = useRef<number>(window.innerWidth / 2);
  const mouseY = useRef<number>(window.innerHeight / 2);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseX.current = e.clientX;
      mouseY.current = e.clientY;
    };

    window.addEventListener(
      "mousemove",
      handleMouseMove
    );


    const canvas = canvasRef.current;
    const canvas2 = canvasRef2.current;
    if (!canvas || !canvas2) return;
    const ctx = canvas.getContext("2d");
    const ctx2 = canvas2.getContext("2d");
    const radius = 300;
    if (!ctx || !ctx2) return;

    let animId: number;
    let cols: number;
    const chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789<>/{}[]|&^%$#@!";

    function resize() {
      if (!canvas || !canvas2) return;
      if (!ctx || !ctx2) return;
      const dpr = window.devicePixelRatio || 1;

      canvas.width =
          window.innerWidth * dpr;
      canvas.height =
          window.innerHeight * dpr;

      canvas.style.width =
          window.innerWidth + "px";
      canvas.style.height =
          window.innerHeight + "px";

      canvas2.width =
          window.innerWidth * dpr;
      canvas2.height =
          window.innerHeight * dpr;

      canvas2.style.width =
          window.innerWidth + "px";
      canvas2.style.height =
          window.innerHeight + "px";


      ctx.scale(dpr, dpr);
      ctx2.scale(dpr, dpr);
      cols = Math.floor(canvas.width / 16);
    }

    const drops: number[] = [];
    const speeds: number[] = [];
    const brightness: number[] = [];

    function init() {
      resize();
      drops.length = 0;
      speeds.length = 0;
      brightness.length = 0;
      for (let i = 0; i < cols; i++) {
        drops[i] = Math.floor(Math.random() * -30);
        speeds[i] = 0.5 + Math.random() * 1.2;
        brightness[i] = 0.3 + Math.random() * 0.7;
      }
    }

    init();

    function draw() {
      if (!canvas || !ctx || !canvas2 || !ctx2) return;
      ctx.fillStyle = "rgba(10, 10, 15, 0.01)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx2.clearRect(0,0,canvas.width, canvas.height);

      const gradient = ctx2.createRadialGradient(
        Number(mouseX.current),
        Number(mouseY.current),
        0,
        Number(mouseX.current),
        Number(mouseY.current),
        radius   
      );
      gradient.addColorStop(0,"rgba(0,255,65,0.2)");
      gradient.addColorStop(0.6,"rgba(0,255,65,0.04)");
      gradient.addColorStop(1,"rgba(0,255,65,0)");
      ctx2.fillStyle = gradient;
      ctx2.beginPath();
      ctx2.arc(Number(mouseX.current),Number(mouseY.current),radius,0,Math.PI * 2);
      ctx2.fill();


      for (let i = 0; i < drops.length; i++) {
        const x = i * 16;
        const y = drops[i] * 18;

        // const dx = (x - Number(mouseX)) / window.innerWidth;
        // const dy = (y - Number(mouseY)) / window.innerHeight;
        // const dist = Math.sqrt(dx * dx + dy * dy);
        // const alpha = dist < 0.15 ? 0.08 : brightness[i] * 0.6;
        const alpha = brightness[i] * 0.6;

        ctx.font = "14px monospace";
        const char = chars[Math.floor(Math.random() * chars.length)];

        if (drops[i] * 18 > 0) {
          ctx.fillStyle = `rgba(0, 255, 65, ${alpha * 0.3})`;
          ctx.fillText(char, x, y - 18);
        }

        ctx.fillStyle = `rgba(0, 255, 65, ${alpha})`;
        ctx.fillText(char, x, y);

        drops[i] += speeds[i];
        if (drops[i] * 18 > canvas.height + 20) {
          drops[i] = Math.floor(Math.random() * -10);
          const gradientRect = ctx.createLinearGradient(x, 0, x, canvas.height);
          gradientRect.addColorStop(0,"rgba(10, 10, 15, 0.8)");
          gradientRect.addColorStop(0.7,"rgba(10, 10, 15, 0.5)");
          gradientRect.addColorStop(1,"rgba(10, 10, 15, 0.3)");
          ctx.fillStyle = gradientRect;
          ctx.fillRect(x, 0, 16, canvas.height);
        }
      }

      animId = requestAnimationFrame(draw);
    }

    draw();

    const handleResize = () => init();
    window.addEventListener("resize", handleResize);
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener(
        "mousemove",
        handleMouseMove
      );
    };
  }, []);

  return (
    <>
      <canvas
        ref={canvasRef2}
        className="fixed inset-0 w-full h-full pointer-events-none"
        style={{ zIndex: 1, opacity: 0.5 }}
      />
      <canvas
        ref={canvasRef}
        className="fixed inset-0 w-full h-full pointer-events-none"
        style={{ zIndex: 0, opacity: 0.5 }}
      />
    </>
  );
}

// ─── Mouse-tracking spotlight ───────────────────────────────────
// function Spotlight({ mouseX, mouseY }: { mouseX: number; mouseY: number }) {
//   return (
//     <div
//       className="fixed pointer-events-none"
//       style={{
//         left: mouseX - 300,
//         top: mouseY - 300,
//         width: 600,
//         height: 600,
//         background: `radial-gradient(circle at center, rgba(0, 255, 65, 0.04) 0%, transparent 70%)`,
//         zIndex: 1,
//         transition: "left 0.15s ease-out, top 0.15s ease-out",
//       }}
//     />
//   );
// }

// ─── Typewriter text ────────────────────────────────────────────
function TypewriterText({ text, className }: { text: string; className?: string }) {
  const [displayed, setDisplayed] = useState("");
  // const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayed("");
    // setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        // setDone(true);
      }
    }, 50);
    return () => clearInterval(interval);
  }, [text]);

  return (
    <span className={className}>
      {displayed}
      {<span className="animate-blink text-accent">_</span>}
    </span>
  );
}

// ─── Floating particles (CSS) ───────────────────────────────────
function FloatingParticles() {
  const particles = useRef<{ id: number; x: number; y: number; size: number; delay: number; dur: number; char: string }[]>([]);

  if (particles.current.length === 0) {
    const chars = "<>/{}[]&/*-+=#@!?%$";
    for (let i = 0; i < 18; i++) {
      particles.current.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: 10 + Math.random() * 16,
        delay: Math.random() * 8,
        dur: 6 + Math.random() * 8,
        char: chars[Math.floor(Math.random() * chars.length)],
      });
    }
  }

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 2 }}>
      {particles.current.map((p) => (
        <div
          key={p.id}
          className="absolute text-accent/20 font-mono"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            fontSize: p.size,
            animation: `float-particle ${p.dur}s ease-in-out ${p.delay}s infinite`,
          }}
        >
          {p.char}
        </div>
      ))}
    </div>
  );
}

// ─── Article item with scroll reveal ────────────────────────────
function ArticleItem({
  article,
  index,
  onClick,
}: {
  article: ArticleMeta;
  index: number;
  onClick: (id: number) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`group cursor-pointer transition-all duration-700 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
      }`}
      style={{ transitionDelay: `${index * 100}ms` }}
      onClick={() => onClick(article.id)}
    >
      <div className="relative overflow-hidden rounded-xl border border-dark-700/60 bg-dark-900/40 backdrop-blur-sm p-6 hover:border-accent/40 hover:shadow-[0_0_30px_rgba(0,255,65,0.08)] transition-all duration-500">
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none">
          <div className="absolute top-0 -left-[100%] w-full h-full bg-gradient-to-r from-transparent via-accent/5 to-transparent skew-x-[-20deg] group-hover:animate-shine" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 text-xs text-gray-500 mb-3 font-mono">
            <span className="inline-flex items-center gap-1.5 text-accent">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              {article.created_at?.split("T")[0] || "unknown"}
            </span>
            <span className="text-dark-600">|</span>
            <span className="text-neon-blue">{article.category}</span>
            <span className="text-dark-600">|</span>
            <span className="text-gray-600">{article.views} views</span>
          </div>

          <h3 className="text-xl md:text-2xl font-bold text-gray-100 group-hover:text-accent transition-colors duration-300 mb-3 font-mono tracking-tight">
            {article.title}
          </h3>

          <p className="text-sm text-gray-400 leading-relaxed mb-4 line-clamp-2">
            {article.summary}
          </p>

          <div className="flex items-center justify-between">
            <div className="flex gap-2 flex-wrap">
              {article.tags?.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="px-2.5 py-1 text-xs rounded-full border border-neon-purple/20 bg-neon-purple/5 text-neon-purple font-mono hover:bg-neon-purple/15 transition-colors"
                >
                  #{tag}
                </span>
              ))}
            </div>
            <span className="text-xs text-gray-600 font-mono">
              {article.author}
            </span>
          </div>
        </div>

        <div className="absolute top-3 right-3 text-dark-700/30 text-xs font-mono select-none">
          [{String(index + 1).padStart(2, "0")}]
        </div>
      </div>
    </div>
  );
}

// ─── Scroll Indicator ───────────────────────────────────────────
function ScrollIndicator() {
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      if (window.scrollY > 100) setHidden(true);
      else setHidden(false);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div
      className={`absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 transition-opacity duration-700 ${
        hidden ? "opacity-0 pointer-events-none" : "opacity-100"
      }`}
      style={{ zIndex: 5 }}
    >
      <span className="text-xs text-gray-600 font-mono tracking-widest">SCROLL</span>
      <div className="scroll-arrow" />
    </div>
  );
}

// ─── Stats counter ──────────────────────────────────────────────
function AnimatedCounter({ target, label }: { target: number; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [count, setCount] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.5 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    let start = 0;
    const duration = 1500;
    const step = 16;
    const totalSteps = duration / step;
    const increment = target / totalSteps;
    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, step);
    return () => clearInterval(timer);
  }, [visible, target]);

  return (
    <div ref={ref} className="text-center">
      <div className="text-2xl md:text-3xl font-bold text-accent font-mono">
        {visible ? count : 0}
      </div>
      <div className="text-xs text-gray-500 font-mono mt-1 tracking-wider">{label}</div>
    </div>
  );
}

// ─── Main Home Component ────────────────────────────────────────
export default function Home({ onNavigate }: HomeProps) {
  const [articles, setArticles] = useState<ArticleMeta[]>([]);
  const [siteInfo, setSiteInfo] = useState<SiteInfo | null>(null);
  // const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [showArticles, setShowArticles] = useState(false);
  const heroRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.getArticles(1, 100).then((d) => setArticles(d.items)).catch(() => {});
    api.getSiteInfo().then(setSiteInfo).catch(() => {});
  }, []);

  // const handleMouseMove = useCallback((e: MouseEvent) => {
  //   setMousePos({ x: e.clientX, y: e.clientY });
  // }, []);

  // useEffect(() => {
  //   window.addEventListener("mousemove", handleMouseMove);
  //   return () => window.removeEventListener("mousemove", handleMouseMove);
  // }, [handleMouseMove]);

  useEffect(() => {
    const onScroll = () => {
      if (window.scrollY > window.innerHeight * 0.2) {
        setShowArticles(true);
      }
    };
    // Also check immediately in case the page loads already scrolled down
    if (window.scrollY > window.innerHeight * 0.2) {
      setShowArticles(true);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const totalArticles = siteInfo?.total_articles ?? 0;
  const totalViews = siteInfo?.total_views ?? 0;

  return (
    <div className="relative">
      <MatrixRain />
      {/* <Spotlight mouseX={mousePos.x} mouseY={mousePos.y} /> */}

      <section
        ref={heroRef}
        className="relative flex flex-col items-center justify-center min-h-screen px-4"
        style={{ zIndex: 3 }}
      >
        <FloatingParticles />

        <div className="relative max-w-4xl mx-auto text-center" style={{ zIndex: 4 }}>
          <div className="mb-6 inline-flex items-center gap-3 px-4 py-2 border border-accent/20 rounded-full bg-dark-900/60 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
            <span className="text-accent text-xs font-mono tracking-[0.2em]">
              SYSTEM_INITIALIZED
            </span>
            <span className="w-2 h-2 rounded-full bg-accent/40" />
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold font-mono tracking-tight mb-6">
            <span className="text-gray-100 glitch-text" data-text="HWT">
              HWT
            </span>
            <span className="text-accent glitch-text mx-2" data-text=">">
              &gt;
            </span>
            <span className="text-gray-100 glitch-text" data-text="BLOG">
              BLOG
            </span>
          </h1>

          <div className="h-8 mb-8">
            <TypewriterText
              text="$惠文通的 代码 · 文字 · 音乐与电影的聚合作品。"
              className="text-gray-400 font-mono text-sm md:text-base tracking-wider"
            />
          </div>

          <div className="flex flex-wrap justify-center gap-4 mt-8">
            <button
              onClick={() => onNavigate("articles")}
              className="group relative px-8 py-3 bg-accent/10 border border-accent/40 rounded-full text-accent font-mono text-sm tracking-wider overflow-hidden transition-all duration-300 hover:bg-accent/20 hover:border-accent hover:shadow-[0_0_30px_rgba(0,255,65,0.15)]"
            >
              <span className="relative z-10">$ explore_posts()</span>
              <div className="absolute inset-0 bg-gradient-to-r from-accent/0 via-accent/10 to-accent/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
            </button>
            <button
              onClick={() => onNavigate("about")}
              className="px-8 py-3 border border-dark-600 rounded-full text-gray-400 font-mono text-sm tracking-wider transition-all duration-300 hover:border-gray-500 hover:text-gray-200 hover:bg-dark-800/50"
            >
              $ about_me()
            </button>
          </div>
        </div>

        <ScrollIndicator />
      </section>

      <section
        className={`relative py-24 px-4 transition-all duration-1000 ${
          showArticles ? "opacity-100" : "opacity-0"
        }`}
        style={{ zIndex: 3 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-3 gap-8 md:gap-16">
            <AnimatedCounter target={totalArticles} label="ARTICLES" />
            <AnimatedCounter target={totalViews} label="VIEWS" />
            <AnimatedCounter target={3} label="CATEGORIES" />
          </div>
        </div>
      </section>

      <section
        className={`relative pb-48 px-4 transition-all duration-1000 ${
          showArticles ? "opacity-100 translate-y-0" : "opacity-0 translate-y-16"
        }`}
        style={{ zIndex: 3 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-10">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent" />
            <span className="text-accent font-mono text-sm tracking-[0.3em] flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              LATEST_POSTS
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
            </span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent" />
          </div>

          <div className="space-y-5">
            {articles.length === 0 ? (
              <div className="text-center py-20">
                <div className="text-5xl mb-4 text-dark-600 font-mono">{">>>"}</div>
                <p className="text-gray-600 font-mono text-sm">// No posts yet. Stay tuned.</p>
              </div>
            ) : (
              articles.map((article, i) => (
                <ArticleItem
                  key={article.id}
                  article={article}
                  index={i}
                  onClick={(id) => onNavigate("article", id)}
                />
              ))
            )}
          </div>

          {articles.length > 0 && (
            <div className="text-center mt-10">
              <button
                onClick={() => onNavigate("articles")}
                className="group relative px-10 py-3 bg-transparent border border-dark-600 rounded-lg text-gray-400 font-mono text-sm tracking-wider overflow-hidden transition-all duration-300 hover:border-accent/50 hover:text-accent"
              >
                <span className="relative z-10">$ view_all_posts()</span>
                <div className="absolute inset-0 bg-gradient-to-r from-accent/0 via-accent/5 to-accent/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              </button>
            </div>
          )}
        </div>
      </section>

      <div
        className="fixed bottom-0 left-0 w-full h-32 pointer-events-none"
        style={{
          background: "linear-gradient(to top, rgba(10,10,15,1) 0%, transparent 100%)",
          zIndex: 2,
        }}
      />
    </div>
  );
}
