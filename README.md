# NEXUS BLOG — 暗黑极客空间

一个全栈博客网站项目，前端使用 React + TypeScript + Tailwind CSS + Vite，后端使用 FastAPI + SQLite，容器化使用 Podman/Docker。

## 项目结构

`
myblog/
├── frontend/                  # 前端 (React + Vite + Tailwind)
│   ├── src/
│   │   ├── components/        # 共享组件 (Navbar, Sidebar, ArticleCard)
│   │   ├── pages/             # 页面 (Home, ArticleList, ArticleDetail, Tool, My, About)
│   │   ├── types/             # TypeScript 类型定义
│   │   ├── api/               # API 客户端
│   │   ├── App.tsx            # 主应用 + 路由
│   │   ├── main.tsx           # 入口
│   │   └── index.css          # Tailwind + 暗黑极客主题
│   ├── Dockerfile             # 多阶段构建 (Node → Nginx)
│   └── nginx.conf             # Nginx 配置 (含 API 反向代理)
├── backend/                   # 后端 (FastAPI + SQLite)
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── models.py          # SQLAlchemy 数据模型
│   │   ├── schemas.py         # Pydantic 数据校验
│   │   ├── database.py        # 数据库连接
│   │   ├── seed.py            # 种子数据
│   │   └── routers/           # API 路由
│   │       ├── articles.py    # 文章 API
│   │       ├── comments.py    # 评论 API
│   │       ├── tools.py       # 工具 API
│   │       └── media.py       # 媒体 API
│   ├── pyproject.toml         # uv 项目配置
│   └── Dockerfile             # Python 容器化
├── docker-compose.yml         # Podman Compose 一键部署
└── README.md
`

## 快速启动

### 方式一: 容器化部署 (推荐)

前提: 安装 [Podman](https://podman.io/) 和 [podman-compose](https://github.com/containers/podman-compose) (或 Docker Compose)

`ash
# 一键启动
podman-compose up --build

# 或使用 Docker
docker compose up --build
`

访问 http://localhost

### 方式二: 本地开发

#### 后端

`ash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
`

首次启动数据库为空，运行种子数据:

`ash
uv run python -m app.seed
`

#### 前端

`ash
cd frontend
npm install
npm run dev
`

前端开发服务器会代理 /api 请求到后端 (http://localhost:5173)。

## 导航页面

| 页面 | 路由 | 说明 |
|------|------|------|
| HOME | home | 综合主页，时间轴展示最新文章 |
| ARTICLE | articles | 博客文章列表与详情页 |
| TOOL | tool | 自研工具分享 |
| MY | my | 音乐 / 照片 / 电影 |
| ABOUT | about | 彩蛋页面，终端启动动画 |

## 技术栈

- **前端**: React 19, TypeScript 6, Tailwind CSS 4, Vite 8
- **后端**: FastAPI, SQLAlchemy, SQLite, Pydantic
- **容器**: Podman / Docker, Nginx (静态资源服务)
- **包管理**: npm (前端), uv (后端)