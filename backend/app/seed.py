"""Seed the database with demo data."""
from datetime import datetime, timezone
from app.database import engine, SessionLocal, Base
from app.models import Article, Comment, ToolItem, MediaItem

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(Article).count() > 0:
    print("> Database already has data, skipping seed.")
    db.close()
    exit(0)

print("> Seeding demo data...")

articles_data = [
    Article(
        title="深入理解 Rust 的所有权系统",
        summary="Rust 的所有权系统是它最独特的特性之一，本文深入浅出地讲解其核心概念与实战技巧。",
        content="""## 引言

Rust 的所有权系统在编译时保证了内存安全，无需垃圾回收器。本文将从基础概念出发，逐步深入到高级用法。

## 所有权规则

1. Rust 中每一个值都有一个所有者（owner）
2. 同一时间只能有一个所有者
3. 当所有者离开作用域，值将被丢弃

## 借用与引用

借用（borrowing）是通过引用（reference）来实现的。引用允许你访问值而不获取其所有权。

\`\`\`rust
fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s);
    println!("'{s}' 的长度是 {len}");
}

fn calculate_length(s: &String) -> usize {
    s.len()
}
\`\`\`

## 生命周期

生命周期是 Rust 用来确保引用始终有效的机制。生命周期注解描述了多个引用之间的关系。

\`\`\`rust
fn longest<\'a>(x: &\'a str, y: &\'a str) -> &\'a str {
    if x.len() > y.len() { x } else { y }
}
\`\`\`

## 总结

所有权、借用和生命周期是 Rust 的核心概念，掌握它们就能写出安全高效的代码。""",
        author="NEXUS",
        category="Tech",
        tags="Rust,编程,内存安全,系统编程",
        views=1423,
        created_at=datetime(2026, 6, 15, tzinfo=timezone.utc),
    ),
    Article(
        title="构建高性能微服务架构的十个原则",
        summary="微服务架构设计不仅仅是拆分服务，更是一套完整的工程实践。本文总结了十个关键设计原则。",
        content="""## 1. 单一职责原则\n\n每个服务只负责一个业务领域。\n\n## 2. 去中心化数据管理\n\n每个服务拥有自己的数据库，避免共享存储。\n\n## 3. 弹性设计\n\n通过熔断器、重试和超时机制来应对故障。\n\n## 4. 可观测性\n\n集中化日志、指标和链路追踪是分布式系统的必备设施。\n\n## 5. 自动化部署\n\n持续集成和持续部署是微服务成功的关键。\n\n## 6. API 优先\n\n通过良好设计的 API 契约来保证服务间的兼容性。\n\n## 7. 无状态服务\n\n尽可能保持服务无状态，状态委派给外部存储。\n\n## 8. 限流与保护\n\n使用令牌桶或漏桶算法保护后端服务。\n\n## 9. 版本管理\n\n通过 API 版本化来实现平滑升级。\n\n## 10. 安全第一\n\n服务间通信必须加密，使用 OAuth2/JWT 进行认证授权。""",
        author="NEXUS",
        category="Architecture",
        tags="微服务,架构,分布式,后端设计",
        views=892,
        created_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
    ),
    Article(
        title="从零实现一个 KV 存储引擎",
        summary="用 Go 语言手写一个迷你 LSM-Tree 存储引擎，理解现代数据库的核心原理。",
        content="""## LSM-Tree 简介\n\nLSM-Tree (Log-Structured Merge-Tree) 是许多现代数据库的核心数据结构。\n\n## 核心思想\n\n将写入操作先缓存在内存中的 MemTable，达到阈值后冻结为不可变的 SSTable，后台进行合并压缩。\n\n## 实现步骤\n\n### 1. MemTable (内存表)\n\n通常使用跳表 (SkipList) 或 B 树来实现有序存储。\n\n### 2. WAL (预写日志)\n\n写入 MemTable 之前先写入 WAL，保证崩溃恢复。\n\n### 3. SSTable (有序字符串表)\n\n磁盘上的不可变数据文件，包含数据块和索引块。\n\n### 4. Compaction (压缩)\n\n后台线程定期合并多个 SSTable，清理过期数据。\n\n## 总结\n\n虽然只是一个玩具实现，但足以让你理解分布式数据库的底层原理。""",
        author="NEXUS",
        category="Tech",
        tags="Go,数据库,LSM-Tree,存储引擎",
        views=2156,
        created_at=datetime(2026, 5, 28, tzinfo=timezone.utc),
    ),
    Article(
        title="2026 独立游戏开发日记",
        summary="记录我开发第一款像素风独立游戏的全过程——从构思到发售的经历与感悟。",
        content="""## 缘起\n\n2025 年底，我决定辞职全职开发一款独立游戏。\n\n## 游戏设计\n\n像素风格的 Roguelike 地牢探险游戏，核心玩法是时间回溯系统。\n\n## 技术选型\n\n- 引擎: Godot 4\n- 语言: GDScript\n- 美术: Aseprite (像素画)\n\n## 发售\n\n2026 年 4 月在 Steam 发售，首周销量 3000 份。""",
        author="NEXUS",
        category="Life",
        tags="游戏开发,独立游戏,Godot,像素风",
        views=3401,
        created_at=datetime(2026, 5, 15, tzinfo=timezone.utc),
    ),
    Article(
        title="密码学入门: 对称加密与非对称加密",
        summary="通俗易懂地讲解现代密码学的基础知识，包括 AES、RSA、ECC 等常用算法。",
        content="""## 为什么需要加密？\n\n解决了三个问题：机密性、完整性、身份认证。\n\n## 对称加密\n\n加密和解密使用相同的密钥。\n\n### AES\n目前最广泛使用的对称加密算法。\n\n## 非对称加密\n\n使用公钥和私钥对。\n\n### RSA\n基于大整数分解难题。\n\n### ECC\n在同等安全级别下使用更短的密钥。""",
        author="NEXUS",
        category="Tech",
        tags="密码学,安全,AES,RSA,加密",
        views=1678,
        created_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
    ),
    Article(
        title="我的极简 VIM 配置哲学",
        summary="一份经过五年打磨的 VIM 配置，追求极简与高效，不依赖重型插件。",
        content="""## 核心哲学\n\n- 尽量使用 VIM 内置功能\n- 只安装真正提升效率的插件\n- 不把 VIM 变成 IDE\n\n## 核心插件\n\n- vim-tiny: 文件浏览器\n- vim-commentary: 快速注释\n- fzf.vim: 模糊搜索\n- vim-surround: 编辑包围字符""",
        author="NEXUS",
        category="Tech",
        tags="VIM,编辑器,配置,效率",
        views=2345,
        created_at=datetime(2026, 3, 8, tzinfo=timezone.utc),
    ),
    Article(
        title="切尔诺贝利: 错误、谎言与牺牲",
        summary="重看 HBO 剧集《切尔诺贝利》，结合历史资料，谈谈对技术、官僚体制和人性的思考。",
        content="""## 技术的傲慢\n\n切尔诺贝利事故的根本原因是反应堆设计本身就存在致命缺陷。\n\n## 体制的沉默\n\n信息的不透明导致了更大的灾难。\n\n## 英雄与凡人\n\n那些冲在第一线的消防员、矿工、飞行员，他们知道自己在走向死亡，但还是去了。""",
        author="NEXUS",
        category="Review",
        tags="切尔诺贝利,影评,历史,思考",
        views=4210,
        created_at=datetime(2026, 2, 14, tzinfo=timezone.utc),
    ),
    Article(
        title="用 Python 实现一个实时音频可视化工具",
        summary="利用 PyAudio 和 NumPy 从零实现频谱可视化，让你的音乐在屏幕上绽放。",
        content="""## 技术栈\n\nPyAudio + NumPy + Pygame\n\n## 核心原理\n\n1. 从声卡捕获 PCM 音频数据\n2. 使用 FFT 将时域信号转换为频域\n3. 将频域数据映射为柱状图的振幅""",
        author="NEXUS",
        category="Tech",
        tags="Python,音频,可视化,FFT",
        views=987,
        created_at=datetime(2026, 1, 22, tzinfo=timezone.utc),
    ),
    Article(
        title="2025 年度书单与阅读笔记",
        summary="去年读的 30 本书里，精选 10 本最值得推荐的，涵盖技术、科幻、哲学和文学。",
        content="""## 技术类\n\n### 《设计数据密集型应用》— Martin Kleppmann\n分布式系统领域的必读之作。\n\n### 《计算机程序的构造与解释》(SICP)\n经典中的经典。\n\n## 科幻类\n\n### 《莱博维茨的赞歌》\n后末日启示录风格。\n\n## 文学类\n\n### 《百年孤独》— 加西亚·马尔克斯\n魔幻现实主义的巅峰。""",
        author="NEXUS",
        category="Life",
        tags="书单,阅读,推荐,2025",
        views=5678,
        created_at=datetime(2026, 1, 5, tzinfo=timezone.utc),
    ),
    Article(
        title="音乐制作入门: 用 DAW 编曲的基本流程",
        summary="从零开始学习电子音乐制作，了解 DAW 的基本操作和编曲思路。",
        content="""## 选择 DAW\n\n- Ableton Live: 电子音乐制作首选\n- FL Studio: 适合编曲入门\n- Logic Pro: Mac 用户的好选择\n\n## 基本流程\n\n节奏编写 → 和弦进行 → 旋律 → 编曲 → 混音 → 母带""",
        author="NEXUS",
        category="Life",
        tags="音乐,编曲,DAW,电子音乐",
        views=756,
        created_at=datetime(2025, 12, 10, tzinfo=timezone.utc),
    ),
]

for a in articles_data:
    db.add(a)
db.flush()

comments_data = [
    Comment(article_id=1, author="RustFan", content="写得很清楚，对我理解所有权很有帮助！"),
    Comment(article_id=1, author="CodeWanderer", content="NLL 让借用检查器变得更智能了。"),
    Comment(article_id=3, author="DBGeek", content="好文！LSM-Tree 确实改变了数据库领域的格局。"),
    Comment(article_id=3, author="GoDev", content="用 Go 实现 LSM-Tree 是个好主意。"),
    Comment(article_id=4, author="IndieDev", content="同为独立开发者，感同身受。"),
    Comment(article_id=7, author="HistoryBuff", content="推荐看看《凌晨三点的切尔诺贝利》。"),
    Comment(article_id=9, author="Bookworm", content="《百年孤独》我读了四遍，每次都有新的发现。"),
]

for c in comments_data:
    db.add(c)
db.flush()

tools_data = [
    ToolItem(name="Mark2HTML", description="Markdown 一键转换为美观的 HTML 文档。", url="https://github.com/nexus/mark2html", icon="📝", category="utility"),
    ToolItem(name="CodeSnap", description="漂亮的代码截图工具，支持多种主题。", url="https://github.com/nexus/codesnap", icon="📸", category="developer"),
    ToolItem(name="IPalette", description="智能配色方案生成器。", url="https://github.com/nexus/ipalette", icon="🎨", category="design"),
    ToolItem(name="LogTail", description="轻量级日志查看器，支持实时 tail 和过滤。", url="https://github.com/nexus/logtail", icon="📋", category="developer"),
    ToolItem(name="TinyDB", description="嵌入式 JSON 文档数据库，纯 Python 实现。", url="https://github.com/nexus/tinydb", icon="🗄️", category="database"),
    ToolItem(name="FastProxy", description="高性能 HTTP/HTTPS 代理工具。", url="https://github.com/nexus/fastproxy", icon="🌐", category="network"),
]

for t in tools_data:
    db.add(t)
db.flush()

media_data = [
    MediaItem(title="Midnight Express", type="music", description="电子氛围音乐，适合深夜写代码时听。", url="", cover="", created_at=datetime(2026, 6, 1, tzinfo=timezone.utc)),
    MediaItem(title="Cyberpunk 2077 摄影集", type="photo", description="夜之城的光与影。", url="", cover="", created_at=datetime(2026, 5, 10, tzinfo=timezone.utc)),
    MediaItem(title="银翼杀手 2049", type="movie", description="近十年来最好的科幻片之一。", url="", cover="", created_at=datetime(2026, 4, 15, tzinfo=timezone.utc)),
    MediaItem(title="像素都市", type="music", description="Chiptune 风格电子曲。", url="", cover="", created_at=datetime(2026, 3, 20, tzinfo=timezone.utc)),
    MediaItem(title="雪国列车 (剧版)", type="movie", description="反乌托邦题材经典。", url="", cover="", created_at=datetime(2026, 2, 8, tzinfo=timezone.utc)),
    MediaItem(title="东京夜景", type="photo", description="2025 年东京旅行随拍。", url="", cover="", created_at=datetime(2026, 1, 12, tzinfo=timezone.utc)),
]

for m in media_data:
    db.add(m)
db.flush()

db.commit()
db.close()
print("> Seed complete! 10 articles, 7 comments, 6 tools, 6 media items.")
