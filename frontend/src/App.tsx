import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import MusicPlayer from "./components/MusicPlayer";
import Home from "./pages/Home";
import beianIcon from "./assets/45bd15b41889aff0c91de802c6f86ef7.png";
import ArticleList from "./pages/ArticleList";
import ArticleDetail from "./pages/ArticleDetail";
import Tool from "./pages/Tool";
import My from "./pages/My";
import About from "./pages/About";

export type Page = "home" | "articles" | "article" | "tool" | "my" | "about";

function App() {
  const [page, setPage] = useState<Page>("home");
  const [articleId, setArticleId] = useState<number | null>(null);

  useEffect(() => {
    document.title = "惠文通的技术分享-博客空间";
  }, []);

  const navigate = (p: Page, id?: number) => {
    setPage(p);
    if (id !== undefined) setArticleId(id);
    window.scrollTo(0, 0);
  };

  const renderPage = () => {
    switch (page) {
      case "home":
        return <Home onNavigate={navigate} />;
      case "articles":
        return <ArticleList onNavigate={navigate} />;
      case "article":
        return articleId ? <ArticleDetail id={articleId} onBack={() => navigate("articles")} onNavigate={(p, id) => navigate(p as Page, id)} /> : <ArticleList onNavigate={navigate} />;
      case "tool":
        return <Tool />;
      case "my":
        return <My />;
      case "about":
        return <About />;
      default:
        return <Home onNavigate={navigate} />;
    }
  };

  return (
    <div className="scanlines min-h-screen flex flex-col">
      <Navbar currentPage={page} onNavigate={navigate} />
      <MusicPlayer />
      <main className={page === "home" ? "flex-1 w-full" : "flex-1 w-full max-w-7xl mx-auto px-4 py-8"}>
        {renderPage()}
      </main>
      <footer className="border-t border-dark-500 bg-dark-900/80 py-4 text-center text-sm text-gray-300">
        <span className="text-accent">?</span>惠文通的技术分享 HWT BLOG v1.0 — Built with
        React + FastAPI &nbsp;|&nbsp; <span className="text-accent">_</span>
        <div className="mt-2 flex flex-wrap justify-center items-center gap-2">
          <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-accent transition-colors duration-200">
            京ICP备2026044069号-1
          </a>&nbsp;&nbsp;
          <img
            src={beianIcon}
            alt="公安备案图标"
            className="w-4 h-4"
          />
          <a href="https://beian.mps.gov.cn/#/query/webSearch" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-accent transition-colors duration-200">
            京公网安备11010502062039号
          </a>
        </div>
      </footer>
    </div>
  );
}

export default App;
