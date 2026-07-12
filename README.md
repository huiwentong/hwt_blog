# HWT BLOG — 暗黑极客空间

一个全栈博客网站 + 管理后端系统。前端使用 React + TypeScript + Tailwind CSS + Vite，后端使用 FastAPI + SQLite，管理端使用 PySide6，容器化使用 Podman/Docker。

---

## 项目结构

```
myblog/
├── frontend/                      # 前端 (React + Vite + Tailwind)
│   ├── src/
│   │   ├── components/            # Navbar, Sidebar, ArticleCard
│   │   ├── pages/                 # Home, ArticleList, ArticleDetail, Tool, My, About
│   │   ├── types/index.ts         # TypeScript 类型定义
│   │   ├── api/index.ts           # API 客户端
│   │   ├── App.tsx                # 主应用 + 页面路由
│   │   ├── main.tsx               # 入口
│   │   └── index.css              # Tailwind v4 + 暗黑极客主题 + Alibaba PuHuiTi 字体
│   ├── Dockerfile                 # 多阶段构建 (Node → Nginx)
│   └── nginx.conf                 # Nginx 配置 (含 API 反向代理)
├── backend/                       # 后端 (FastAPI + SQLite)
│   ├── app/
│   │   ├── main.py                # FastAPI 入口 + 自动 migration
│   │   ├── models.py              # SQLAlchemy 数据模型
│   │   ├── schemas.py             # Pydantic 校验 + UA 解析 (OS/浏览器)
│   │   ├── database.py            # SQLite 连接
│   │   ├── seed.py                # 种子数据 (10 文章 + 评论含 UA 信息)
│   │   └── routers/               # articles, comments, tools, media
│   ├── pyproject.toml             # uv 配置
│   └── Dockerfile
├── manager/                       # 管理后端系统 (PySide6)
│   ├── main.py                    # GUI 入口
│   ├── start.bat                  # 快速启动脚本 (双击运行)
│   ├── pyproject.toml             # uv 配置
│   └── app/
│       ├── db_manager.py          # 数据库 CRUD + 自动建表
│       ├── validation.py          # 表单校验规则
│       ├── main_window.py         # 主窗口 + 数据库选择器
│       └── widgets/
│           ├── article_tab.py     # 文章管理 (表单 + 表格 + 右键删除)
│           ├── tool_tab.py        # 工具管理
│           ├── media_tab.py       # 媒体管理 (音乐/照片/电影)
│           ├── db_selector.py     # SQLite 文件选择器
│           └── style.py           # 暗黑主题 QSS 样式
├── docker-compose.yml             # 容器一键部署
└── README.md
```

---

## 快速启动

### 方式一: 容器化部署

```bash
podman-compose up --build
# 或
docker compose up --build
```
#### 更新容器
```bash
podman build -t hwt-frontend:latest -f frontend/Dockerfile frontend/

# 2. 重新构建后端镜像（如果需要）
podman build -t hwt-backend:latest -f backend/Dockerfile backend/

# 3. 重启容器
podman-compose down
podman-compose up -d
```


访问 http://localhost

### 方式二: 本地开发

#### 后端

```bash
cd backend
uv sync
uv run python -m app.seed            # 首次：填充种子数据
uv run uvicorn app.main:app --reload  # http://localhost:8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173 (自动代理 /api → localhost:8000)
```

#### 管理后端 (桌面 GUI)

```bash
cd manager
uv sync
uv run main.py         # 或双击 start.bat
```

默认连接 `../backend/hwt_blog.db`，也可通过「浏览…」切换其他 SQLite 文件。

---

## 导航页面

| 页面    | 路由       | 说明                             |
|---------|------------|----------------------------------|
| HOME    | home       | 综合主页，时间轴展示最新文章      |
| ARTICLE | articles   | 博客文章列表 (分类过滤 + 搜索)    |
| TOOL    | tool       | 自研工具分享                     |
| MY      | my         | 音乐 / 照片 / 电影               |
| ABOUT   | about      | 彩蛋页面，终端启动动画            |

---

## 功能特性

### 前端

| 特性 | 说明 |
|------|------|
| 暗黑极客风格 | CRT 扫描线、霓虹绿 accent、monospace 全局字体、terminal-card 悬停发光 |
| Alibaba PuHuiTi 字体 | 首页标题使用阿里巴巴普惠体 Bold |
| 时间轴文章流 | 每个卡片带 timeline dot 连接线 |
| Markdown 渲染 | 文章正文使用 `marked` 库渲染，支持代码块高亮、表格、引用等 |
| 评论元数据 | 每条评论显示 IP 地址、操作系统 (🪟/🍎/🐧)、浏览器 (🌐) |
| 分类过滤 + 搜索 | ARTICLE 页面支持按分类切换和全文关键词搜索 |
| 响应式布局 | 桌面导航栏 + 移动端汉堡菜单 |

### 后端

| 特性 | 说明 |
|------|------|
| RESTful API | articles / comments / tools / media / site-info / health |
| 自动 migration | 启动时自动 ALTER TABLE 添加新列、修复 NULL 值 |
| UA 解析 | 从 User-Agent 提取操作系统和浏览器信息 |
| 评论捕获 | 自动记录评论者 IP (支持 X-Forwarded-For) |
| 浏览量统计 | 每次 GET 详情自动 +1，`server_default` 确保数据库级默认值 |

### 管理后端 (桌面 GUI)

| 特性 | 说明 |
|------|------|
| 数据库选择器 | 支持浏览 / 输入任意 .db 路径 |
| 文章管理 | 添加 + 校验 (必填字段红色阻止、标签缺失黄色警告) |
| 工具管理 | 添加 + 校验 (URL 格式检查) |
| 媒体管理 | 添加音乐/照片/电影 |
| 数据列表 | 实时显示最近记录，支持右键菜单删除 (二次确认) |
| 暗黑主题 | PySide6 QSS 样式，风格与前端一致 |

---

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/site-info` | 站点统计 (文章数/浏览量/评论数/分类) |
| GET | `/api/articles` | 文章列表 (?page, ?limit, ?category) |
| GET | `/api/articles/:id` | 文章详情 (自动 +1 浏览) |
| GET/POST | `/api/articles/:id/comments` | 评论列表 / 新增评论 |
| GET | `/api/tools` | 工具列表 |
| GET | `/api/media` | 媒体列表 (?type=music\|photo\|movie) |

---

## 技术栈

- **前端**: React 19, TypeScript 6, Tailwind CSS 4, Vite 8, marked
- **后端**: FastAPI, SQLAlchemy, SQLite, Pydantic, uvicorn
- **管理端**: PySide6 (Qt for Python)
- **容器**: Podman / Docker, Nginx
- **包管理**: npm (前端), uv (后端 + 管理端)