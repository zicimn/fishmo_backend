# Fish Mo — 社区内容平台

一个前后端分离的社区内容平台：用户注册登录、发布/编辑/删除文章、评论、收藏、文章外链（Reference 链接）、搜索、工具箱（图片压缩、每日运势）、公告（更新栏）与个人主页。

- **后端**：`backend/` — Python FastAPI + SQLAlchemy（异步）+ MySQL + Redis
- **前端**：`frontend - 副本/` — Vue 3 + TypeScript + Vite（含一套后端的副本代码，见下方说明）
- **数据库**：`web0.sql` — MySQL 建表 + 示例数据

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端框架 | FastAPI 0.133 + Uvicorn |
| ORM / 数据库 | SQLAlchemy 2.0（异步） + aiomysql + MySQL 5.7 |
| 缓存 | Redis 7（版本号失效策略） |
| 认证 | JWT（python-jose，HS256）+ Argon2 密码哈希（passlib） |
| 邮件验证 | QQ SMTP（465 SSL），验证码存 Redis，5 分钟有效 |
| 图片处理 | Pillow（转 WebP / 压缩 / 头像裁剪） |
| 前端 | Vue 3.5 + Vue Router 5 + Pinia 3 + Vite 7 + TypeScript |
| HTTP | Axios（Bearer Token 拦截器） |
| 渲染 | markdown-it + DOMPurify |

---

## 目录结构

```
item_1/
├── backend/              # Python 后端
│   ├── main.py           # FastAPI 入口，挂载路由 / 静态目录 / CORS
│   ├── config.py         # 数据库、JWT、SMTP、Redis 配置
│   ├── cache.py          # Redis 缓存封装（版本化缓存键）
│   ├── logger.py         # 日志配置（logs/app.log + 控制台）
│   ├── shemas.py         # Pydantic 请求/响应模型
│   ├── route/            # 路由（user / article / search / tools / home / announcement）
│   ├── model/            # SQLAlchemy 模型（User / Article / Comment / ...）
│   ├── utils/            # 工具函数（登录校验 / 邮件 / 图片 / 排序 / 头像）
│   ├── Example/          # 示例配置参考（Ecache.py / Econfig.py）
│   └── requirements.txt  # Python 依赖
│
├── frontend - 副本/      # 前端（Vue3 + TS + Vite）
│   ├── src/
│   │   ├── main.ts       # 入口：createApp → Pinia → Router → mount
│   │   ├── App.vue       # 根布局：顶栏导航 + 搜索 + 暗色模式 + 路由视图
│   │   ├── router/       # 16 条路由（懒加载）
│   │   ├── stores/       # Pinia：用户认证状态（localStorage 持久化）
│   │   ├── api/          # Axios 实例 + 类型化 API 封装
│   │   ├── views/        # 16 个页面组件
│   │   ├── components/   # 共享组件（gitignored）
│   │   └── assets/       # 静态资源：CSS / 背景图
│   ├── main.py           # ⚠️ 后端代码副本（与 backend 相同，仅行尾差异）
│   ├── route/ model/ utils/ shemas.py requirements.txt  # ⚠️ 同上
│   ├── package.json / vite.config.ts / index.html
│   └── CLAUDE.md         # 前端开发规范文档（很详细）
│
├── upload/               # 静态上传目录（头像 / 文章图片 / 运势图）
├── logs/                 # 运行日志
├── web0.sql              # MySQL 建表脚本 + 示例数据
└── requirements.txt      # 根目录依赖清单
```

> **说明**：`frontend - 副本/` 是前端的可运行副本，里面同时拷入了一份后端 Python 代码（`main.py`、`route/`、`model/`、`utils/`、`shemas.py`、`requirements.txt`）。经比对，这份副本与 `backend/` 的 Python 代码内容一致（仅 CRLF/LF 换行符差异），`frontend/` 目录下另有一份更旧的前端版本。

---

## 后端说明（backend）

### 架构

- **入口** `main.py`：FastAPI 应用，开启全量 CORS，挂载 `/upload` 静态目录（自动创建 `avatars/`、`article/`、`fate/` 子目录），注册 6 个路由前缀。
- **异步数据库** `config.py`：`mysql+aiomysql://...`，连接池 10 / 溢出 20，`get_db()` 依赖注入自动 commit/rollback。
- **Redis 缓存** `cache.py`：键格式 `prefix:v版本:参数`；所有列表/搜索接口通过 `search_version` 全局版本号实现失效——任何写操作都会 `update_version()` 自增，旧缓存立即整体过期。

### API 一览（前缀 `/api`）

| 模块 | 端点 | 说明 |
|---|---|---|
| 用户 | `POST /user/login` | 登录，返回 JWT |
| 用户 | `POST /user/register` | 注册（需邮箱验证码） |
| 用户 | `GET /user/info` | 获取个人信息 |
| 用户 | `PUT /user/update` | 更新资料（昵称/邮箱/密码/简介/头像 base64） |
| 用户 | `DELETE /user/delete` | 注销账号（需 `ok=true` 确认） |
| 用户 | `POST /user/send_code` · `POST /user/retrieve` | 发送验证码 / 重置密码 |
| 用户 | `GET /user/article/get_list` | 我的文章列表（分页，Redis 缓存） |
| 用户 | `GET /user/article/getlinklist` | 我提交的外链列表 |
| 用户 | `GET /user/favorite/get_list` | 我的收藏列表 |
| 文章 | `POST /article/publish/` | 发布文章（图片转 WebP 后落盘） |
| 文章 | `GET /article/visit/{id}` | 文章详情（浏览量 +1，私有文章仅作者可见） |
| 文章 | `GET /article/` | 文章列表（分类 / 排序 `created_at`、`views`、`likes` / 分页） |
| 文章 | `PUT /article/edit/{id}` · `DELETE /article/delete/{id}` | 编辑 / 删除（需 `ok=true`） |
| 外链 | `POST /article/{id}/submit_link` · `GET /article/{id}/links` · `DELETE /article/{id}/deleted/{link_id}` | 文章的 Reference 外链 CRUD |
| 评论 | `GET /article/{id}/comment` · `POST /article/{id}/comments` · `DELETE /article/commment/remove/{id}` | 评论列表 / 发表 / 删除 |
| 收藏 | `POST /article/favorite/add/{id}` · `DELETE /article/favorite/remove/{id}` | 收藏 / 取消收藏 |
| 搜索 | `GET /search/{word}` | 全文模糊搜索，标题命中权重 3、正文 1 |
| 首页 | `GET /home/` · `/home/article/{uid}` · `/home/comment/{uid}` | 用户主页信息 / 文章 / 评论 |
| 工具 | `POST /tools/compression` | 图片压缩（最多 10 张，webp/jpg/png，Pillow） |
| 工具 | `GET /tools/diviation` | 每日运势（随机签文，每人每天缓存） |
| 公告 | `GET /announcement/` · `GET /announcement/browse/{id}` | 公告列表 / 详情 |

### 数据模型（`model/`）

`User`、`Article`（含 JSON 图片数组、浏览量/点赞量、可见状态）、`ArticleLink`（文章外链）、`Comment`、`Like`、`Favorite`、`Announcement`。草稿（`Draft`）模型与路由已注释，未启用。

### 工具函数（`utils/`）

- `verify_user.py`：JWT 解码取用户 id（401 处理）
- `verify_email.py`：SMTP 发信 + Redis 验证码校验
- `convert_image.py`：base64 图片转 WebP/JPEG/PNG（透明通道处理）
- `avatar_utils.py`：base64 头像保存为 WebP（800×800 上限）、URL 规范化、旧头像删除
- `article_utils.py`：文章图片落盘至 `upload/article/{id}/`
- `sort_column.py`：排序字段白名单校验 + 构建排序表达式

### 配置（`config.py`）

> ⚠️ **注意**：`config.py` 中直接写有明文数据库密码、QQ SMTP 授权码与 JWT `SECRET_KEY`，且 `.gitignore` 未忽略它。**上线前请务必把敏感信息移到环境变量或本地配置中，勿提交到公开仓库。**

- `ASYNC_DATABASE_URL`：默认本地 `root:fwioe77@localhost:3306/web0`
- `SMTP_*`：QQ 邮箱发信（`smtp.qq.com:465`）
- `SECRET_KEY` / `ALGORITHM`：JWT 签名

---

## 前端说明（frontend - 副本）

### 架构

- `main.ts`：`createApp → Pinia → Router → mount`
- `App.vue`：顶栏导航（品牌 + 首页/发布/更新栏 + 搜索框 + 暗色模式 + 个人主页/退出）、路由视图、毛玻璃卡片设计系统
- `api/request.ts`：Axios 实例，`baseURL=/api`，10s 超时，请求拦截器自动附加 `Authorization: Bearer <token>`
- `api/article.ts` / `api/user.ts`：类型化 API 封装
- `stores/user.ts`：Pinia 认证状态（`id`/`username`/`token`），localStorage 持久化，`isLoggedIn` 由 token 判断

### 路由（16 条）

| 路径 | 页面 | 认证 |
|---|---|---|
| `/` | 首页（文章列表，分类/排序/分页） | 否 |
| `/login` `/register` `/forgot-password` | 登录 / 注册 / 忘记密码 | 否 |
| `/article/:id` | 文章详情（Markdown + 目录 + 外链 + 评论 + 收藏） | 否 |
| `/search/:word` | 搜索结果 | 否 |
| `/publish` `/edit/:id` | 发布 / 编辑文章 | 是 |
| `/articles` `/control` | 我的文章 / 管理面板 | 是 |
| `/links` `/favorite` | 我的外链 / 我的收藏 | 是 |
| `/tools` | 工具箱（图片压缩、今日运势） | 是 |
| `/user-home` `/user/:userId` | 个人主页（重定向 / 用户主页） | 视情况 |
| `/announcement` | 更新栏（公告） | 否 |

### 关键功能

- **Markdown 渲染**：`markdown-it`（开启 html/linkify/typographer）+ `DOMPurify` 消毒；`ArticleDetail` 从标题解析目录（TOC），锚点平滑滚动
- **文章详情双栏布局**：左侧粘性栏（作者信息 + 目录 + 评论预览），右侧正文 + 外链 + 评论区
- **个人主页**（`UserHome`）：左侧头像导航菜单，右侧按标签切换（帖子/评论/链接/收藏/编辑资料），`isViewingOther` 判断是否本人，防止越权编辑
- **工具箱**：图片压缩（多图、质量滑杆、webp/jpg/png 输出、批量下载）、每日运势（随机签文 + 配图）
- **暗色模式**：`filter: brightness(0.7) contrast(1.1)` 全局降暗
- 认证在 API 层（401）而非路由守卫：未登录时侧栏/顶栏隐藏受限入口

---

## 数据库（web0.sql）

共 7 张表，含示例数据：

| 表 | 说明 |
|---|---|
| `user` | 用户（用户名/邮箱唯一索引、密码哈希、头像、简介、状态、是否管理员） |
| `article` | 文章（标题、作者、分类、正文、图片 JSON、浏览量/点赞量、可见状态；作者/分类/时间索引） |
| `article_link` | 文章外链（文章 ID、提交者、URL、标题） |
| `comment` | 评论（文章/用户索引） |
| `favorite` | 收藏（`user_id`+`article_id` 唯一索引） |
| `like` | 点赞记录（唯一约束防重复） |
| `announcement` | 公告（标题、正文、时间） |

---

## 运行指南

### 前置依赖

- MySQL 5.7+（导入 `web0.sql`）
- Redis（默认 `localhost:6379`，无密码）
- Python 3.10+ / Node.js `^20.19 || >=22.12`

### 后端

```bash
cd backend
pip install -r requirements.txt   # 或从根目录 requirements.txt 安装
# 1) 修改 config.py 中的数据库连接、SMTP、SECRET_KEY
# 2) 导入数据库：mysql -uroot -p < ../web0.sql
python main.py                     # 启动于 http://127.0.0.1:8000（reload 模式）
```

### 前端

```bash
cd "frontend - 副本"
npm install
npm run dev        # 开发服务器 http://localhost:5173
npm run build      # 类型检查 + 生产构建
```

开发模式下 Vite 将 `/api` 与 `/upload` 代理到 `http://127.0.0.1:8000`，无需额外处理 CORS。

---

## 注意事项

- `config.py` 含明文敏感信息，上线前请脱敏。
- `src/assets/`、`src/components/` 在 `.gitignore` 中，但本地运行必须存在（否则页面报错）。
- 后端与 `frontend - 副本/` 内的 Python 代码互为副本，改代码时两边需同步（建议以 `backend/` 为唯一事实来源，副本仅用于部署）。
- 部分接口（如删除）带 `ok=true` 确认参数，防止误删。
- `upload/` 目录由后端运行时自动创建，生产环境需保证其写权限。
