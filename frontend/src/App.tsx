import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import ArticleList from "./pages/ArticleList";
import ArticleDetail from "./pages/ArticleDetail";
import Tool from "./pages/Tool";
import My from "./pages/My";
import About from "./pages/About";

type Page = "home" | "articles" | "article" | "tool" | "my" | "about";

function App() {
  const [page, setPage] = useState<Page>("home");
  const [articleId, setArticleId] = useState<number | null>(null);

  useEffect(() => {
    document.title = "NEXUS BLOG — 暗黑极客空间";
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
        return articleId ? <ArticleDetail id={articleId} onBack={() => navigate("articles")} /> : <ArticleList onNavigate={navigate} />;
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
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8">
        {renderPage()}
      </main>
      <footer className="border-t border-dark-700 py-4 text-center text-xs text-gray-600">
        <span className="text-accent">?</span> NEXUS BLOG v1.0 — Built with
        React + FastAPI &nbsp;|&nbsp; <span className="text-accent">_</span>
      </footer>
    </div>
  );
}

export default App;
