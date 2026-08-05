# Fish Mo — 社区内容平台

一个前后端分离的社区内容平台：用户注册登录、发布/编辑/删除文章、评论、收藏、文章外链（Reference 链接）、全文搜索、工具箱（图片压缩、每日运势）、公告（更新栏）与个人主页。

- **后端**：`backend/` — Python FastAPI + SQLAlchemy 2.0（异步）+ MySQL + Redis
- **前端**：`frontend/` — Vue 3 + TypeScript + Vite（16 条路由，懒加载）

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端框架 | FastAPI 0.133 + Uvicorn（reload 模式） |
| ORM / 数据库 | SQLAlchemy 2.0（异步）+ aiomysql + MySQL 5.7（库名 `web0`） |
| 缓存 | Redis 7（redis.asyncio，版本号失效策略） |
| 认证 | JWT（python-jose，HS256）+ Argon2 密码哈希（passlib） |
| 邮件验证 | QQ SMTP（`smtp.qq.com:465`）+ Resend API 双通道，验证码存 Redis |
| 图片处理 | Pillow（转 WebP / 压缩 / 头像裁剪） |
| 数据校验 | Pydantic v2 |
| 可观测性 | Sentry SDK + 本地日志（`logs/app.log`） |
| 前端框架 | Vue 3.5 + Vue Router 5 + Pinia 3 + Vite 7 + TypeScript 5.9 |
| HTTP | Axios（`Bearer` Token 拦截器，10s 超时） |
| 渲染 | markdown-it + DOMPurify |

---

## 目录结构

```
item_1/
├── backend/                    # Python 后端
│   ├── requirements.txt        # Python 依赖（唯一依赖清单）
│   ├── FileStruct.md           # 目录结构参考文档
│   ├── app/
│   │   ├── main.py             # 入口：FastAPI 实例、CORS、挂载 /upload、注册 6 个路由
│   │   ├── api/v1/             # 路由层（user / article / search / tools / home / announcement / draft）
│   │   ├── config/             # ⚠️ 基础设施配置（db / cache / security / logger，被 .gitignore 忽略）
│   │   ├── model/              # SQLAlchemy ORM 模型（User / Article / ArticleLink / ...）
│   │   ├── schemas/            # Pydantic v2 请求/响应模型（user / article / comment / ...）
│   │   └── utils/              # 工具函数（JWT 校验 / 邮件 / 图片 / 排序 / 头像）
│   ├── Example/                # 配置参考示例（Ecache.py / Econfig.py）
│   └── other/func.py           # 遗留辅助函数（当前代码中 import 已注释）
│
├── frontend/                   # 前端（Vue3 + TS + Vite）
│   ├── src/
│   │   ├── main.ts             # 入口：createApp → Pinia → Router → mount
│   │   ├── App.vue             # 根布局：侧栏 + 顶栏（搜索 / 暗色模式）+ 路由视图
│   │   ├── router/             # 16 条路由（懒加载）
│   │   ├── stores/             # Pinia：user 认证状态（localStorage 持久化）
│   │   ├── api/                # Axios 实例 + 类型化 API 封装（request / article / user）
│   │   ├── views/              # 16 个页面组件（+ 2 个脚手架遗留组件）
│   │   ├── components/         # 脚手架遗留组件（HelloWorld 等，未使用）
│   │   └── assets/             # 静态资源：CSS / 背景图
│   ├── package.json / vite.config.ts / index.html / CLAUDE.md（前端开发规范）
│   └── dist/                   # 生产构建产物（gitignored）
│
└── .venv/                      # Python 虚拟环境（gitignored）
```


## 后端说明（backend）

### 架构

- **入口** `app/main.py`：FastAPI 应用，开启全量 CORS，挂载 `/upload` 静态目录（自动创建 `avatars/`、`article/`、`fate/` 子目录），注册 6 个路由；`python app/main.py` 即以 reload 模式启动 Uvicorn。
- **数据库** `app/config/db.py`：`mysql+aiomysql://...`，连接池 10 / 溢出 20、`pool_pre_ping` 保活；`get_db()` 依赖注入自动 commit/rollback。
- **Redis 缓存** `app/config/cache.py`：键格式 `prefix:v版本:参数`；列表/搜索接口通过 `search_version` 全局版本号实现失效——任何写操作调用 `update_version()` 自增，旧缓存立即整体过期。
- **安全配置** `app/config/security.py`：硬编码了 JWT `SECRET_KEY`、QQ SMTP 授权码、Resend API Key、数据库与 Redis 密码（见下方「注意事项」）。

### API 一览

| 模块 | 端点 | 说明 |
|---|---|---|
| 用户 | `POST /api/user/login` | 登录，返回 JWT + 头像 |
| 用户 | `POST /api/user/register` | 注册（需邮箱验证码） |
| 用户 | `GET /api/user/info` | 获取个人信息 |
| 用户 | `PUT /api/user/update` | 更新资料（昵称/邮箱/密码/简介/头像 base64） |
| 用户 | `DELETE /api/user/delete` | 注销账号（需 `ok=true` 确认） |
| 用户 | `POST /api/user/send_code` · `POST /api/user/retrieve` | 发送验证码 / 重置密码 |
| 用户 | `GET /api/user/article/get_list` | 我的文章列表（分页，Redis 缓存） |
| 用户 | `GET /api/user/article/getlinklist` | 我提交的外链列表 |
| 用户 | `GET /api/user/favorite/get_list` | 我的收藏列表 |
| 文章 | `POST /api/article/publish/` | 发布文章（图片转 WebP 后落盘） |
| 文章 | `GET /api/article/visit/{id}` | 文章详情（浏览量 +1） |
| 文章 | `GET /api/article/` | 文章列表（分类 / 排序 `created_at`、`views`、`likes` / 分页） |
| 文章 | `PUT /api/article/edit/{id}` · `DELETE /api/article/delete/{id}` | 编辑 / 删除（需 `ok=true`） |
| 外链 | `POST /api/article/{id}/submit_link` · `GET /api/article/{article_id}/links` · `DELETE /api/article/{article_id}/deleted/{link_id}` | 文章 Reference 外链 CRUD |
| 评论 | `GET /api/article/{id}/comment` · `POST /api/article/{id}/comments` · `DELETE /api/article/commment/remove/{id}` | 评论列表 / 发表 / 删除 |
| 收藏 | `POST /api/article/favorite/add/{id}` · `DELETE /api/article/favorite/remove/{id}` | 收藏 / 取消收藏 |
| 搜索 | `GET /api/search/{word}` | 全文模糊搜索，标题命中权重 3、正文 1 |
| 首页 | `GET /api/home/` · `/api/home/article/{user_id}` · `/api/home/comment/{user_id}` | 用户主页信息 / 文章 / 评论 |
| 工具 | `POST /api/tools/compression` | 图片压缩（最多 10 张，webp/jpg/png，Pillow） |
| 工具 | `GET /api/tools/diviation` | 每日运势（随机签文，每人每天缓存） |
| 公告 | `GET /api/announcement/` · `GET /api/announcement/browse/{id}` | 公告列表 / 详情 |

> 草稿（`draft`）路由与模型均以注释形式存在，功能未启用。

### 数据模型（`app/model/`）

`User`、`Article`（含 JSON 图片数组、浏览量/点赞量、`status` 可见状态）、`ArticleLink`（文章外链）、`Comment`、`Like`、`Favorite`、`Announcement`。对应表名：`user`、`article`、`article_link`、`comment`、`like`、`favorite`、`announcement`。

### 工具函数（`app/utils/`）

- `verify_user.py`：JWT 解码取用户 id（401 处理）
- `verify_email.py`：SMTP 发信 + Redis 验证码校验
- `convert_image.py`：base64 图片转 WebP/JPEG/PNG（透明通道处理）
- `avatar_utils.py`：base64 头像保存为 WebP（800×800 上限）、URL 规范化、旧头像删除
- `article_utils.py`：文章图片落盘（按文章 ID 组织目录）
- `sort_column.py`：排序字段白名单校验 + 构建排序表达式

---

## 前端说明（frontend）

### 架构

- `main.ts`：`createApp → Pinia → Router → mount`
- `App.vue`：顶栏导航 + 侧栏（品牌、首页/发布/更新栏、搜索框、暗色模式、个人主页/退出）+ 路由视图，毛玻璃卡片设计系统
- `api/request.ts`：Axios 实例，`baseURL=/api`，10s 超时，请求拦截器自动附加 `Authorization: Bearer <token>`
- `api/article.ts` / `api/user.ts`：类型化 API 封装
- `stores/user.ts`：Pinia 认证状态（`id`/`username`/`token`），localStorage 持久化，`isLoggedIn` 由 token 判断
- `vite.config.ts`：开发代理 `/api`、`/upload` → `http://127.0.0.1:8000`

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


## 运行指南

### 前置依赖

- MySQL 5.7+（默认连接库 `web0`）
- Redis（默认 `localhost:6379`，无密码）
- Python 3.10+ / Node.js `^20.19 || >=22.12`

### 1. 初始化数据库

`web0.sql` 为数据库导出文件（已被 gitignore），使用 MySQL 客户端导入即可获得完整表结构与数据。

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
# 补齐 app/config/ 下的本地配置（db.py / cache.py / security.py / logger.py）
# 参照 backend/Example/Econfig.py、Ecache.py，修改数据库连接、SMTP、SECRET_KEY
python app/main.py          # 启动于 http://127.0.0.1:8000（reload 模式）
```

> ⚠️ `app/config/` 已被 `.gitignore` 忽略，克隆仓库后需手动创建该目录及 4 个配置文件（本项目在本地保留有一份），否则后端无法启动。

### 3. 前端

```bash
cd frontend
npm install
npm run dev        # 开发服务器 http://localhost:5173
npm run build      # 类型检查 + 生产构建（产物在 dist/）
```

开发模式下 Vite 将 `/api`、`/upload` 代理到 `http://127.0.0.1:8000`，无需额外处理 CORS。

---

## 注意事项
- **配置缺失**：`backend/app/config/` 被 gitignore，仓库中不含该目录；新环境需参照 `backend/Example/` 自建。
- **删除保护**：部分接口（如删除文章/账号）带 `ok=true` 确认参数，防止误删。
- **遗留文件**：`frontend/` 中保留的脚手架组件/视图未被引用，可清理；`v0/` 为旧版快照，仅供回溯。
