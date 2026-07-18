const fs = require("fs");
let content = fs.readFileSync("src/pages/Home.tsx", "utf8");
const old = fs.readFileSync("src/pages/Home.tsx", "utf8").match(/  useEffect\(\(\) => \{\n    const hero = heroRef\.current;\n    if \(!hero\) return;\n    const observer = new IntersectionObserver\(\n      \(\[entry\]\) => \{\n        if \(!entry\.isIntersecting\) \{\n          setShowArticles\(true\);\n        \}\n      \},\n      \{ threshold: 0 \}\n    \);\n    observer\.observe\(hero\);\n    return \(\) => observer\.disconnect\(\);\n  \}, \[\]\);/);
if (old && old[0]) {
  const newStr = `  useEffect(() => {
    const onScroll = () => {
      if (window.scrollY > window.innerHeight * 0.7) {
        setShowArticles(true);
      }
    };
    if (window.scrollY > window.innerHeight * 0.7) {
      setShowArticles(true);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);`;
  content = content.replace(old[0], newStr);
  fs.writeFileSync("src/pages/Home.tsx", content, "utf8");
  console.log("OK");
} else {
  console.log("NOT FOUND");
}