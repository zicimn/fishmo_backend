# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vue 3 + TypeScript + Vite frontend for **Fish Platform** — a community content platform with articles, user management, comments, links, and favorites. Connects to a Python backend at `http://127.0.0.1:8000` via Vite dev proxy.

## Commands

```bash
npm run dev          # Start dev server (http://localhost:5173, binds 0.0.0.0)
npm run build        # Full production build: type-check then vite build
npm run build-only   # Vite build only, skip type-check
npm run preview      # Vite preview of production build
npm run type-check   # vue-tsc type checking only
npm run lint         # Run oxlint then ESLint (both auto-fix)
npm run format       # Prettier format src/
```

Note: `#` prefix comments in package.json scripts use `npm-run-all2` (`run-p` = parallel, `run-s` = sequential).

## Architecture

```
src/
├── main.ts              # App bootstrap: createApp → Pinia → Router → mount
├── App.vue              # Root layout: collapsible sidebar + top bar (search/user/dark-mode) + <router-view>
├── router/index.ts      # 16 routes (HomePage, Login, Register, ArticleDetail, etc.)
├── stores/user.ts       # Pinia auth store (id/username/token persisted in localStorage)
├── api/
│   ├── request.ts       # Axios instance: baseURL=/api, 10s timeout, auth Bearer interceptor, response logging
│   ├── article.ts       # Article CRUD, links, comments, favorites, home articles/comments — all endpoints as a typed object
│   └── user.ts          # Login, register, profile update, password reset, avatar, sendCode
├── views/               # 16 page components (one per route, lazy-loaded)
├── components/          # Shared UI components (gitignored)
└── assets/              # Static files: CSS, images, fonts (gitignored)
```

**Alias:** `@/` → `src/` (configured in vite.config.ts)

**Dev proxy:** Vite proxies `/api` and `/upload` → `http://127.0.0.1:8000` (handles CORS in dev)

## Routes (16 total)

| Path | View | Auth required? |
|---|---|---|
| `/` | HomePage | No |
| `/login` | LoginPage | No |
| `/register` | RegisterPage | No |
| `/forgot-password` | ForgotPasswordPage | No |
| `/article/:id` | ArticleDetail | No |
| `/search/:word` | SearchResults | No |
| `/publish` | PublishArticle | Yes |
| `/edit/:id` | EditArticle | Yes |
| `/articles` | UserArticles | Yes |
| `/control` | ControlPanel | Yes |
| `/links` | UserLinks | Yes |
| `/favorite` | FavoritePage | Yes |
| `/tools` | ToolsPage | Yes |
| `/user-home` | Redirect → `/user/{id}` | Yes (→/login) |
| `/user/:userId` | UserHome | No* |
| `/announcement` | AnnouncementPage | No |

\* `/user/:userId` shows a user's profile (anyone can view); edit/delete features are only visible to the profile owner via `isViewingOther` computed guard.

Auth is enforced at the API level (401 response) rather than with navigation guards — the sidebar simply hides login-required links when not authenticated.

## State & Auth Flow

- `useUserStore` (Pinia, `defineStore`) holds `id`, `username`, `token`, backed by localStorage
- `isLoggedIn` getter checks `!!token`
- Axios request interceptor attaches `Authorization: Bearer <token>` to every request
- Login response shape: `{ id, username, access_token }` — stored via `userStore.login()`
- Logout clears store + localStorage; consumer should call `router.push('/')` to redirect
- No route guard middleware — unauthenticated API calls return 401 handled per-call

## Layout (App.vue)

The root component is a three-zone layout:
1. **Sidebar** (fixed left, 250px / collapsible to 64px) — nav links with Chinese-character icons, collapses via `isCollapsed` ref
2. **Top bar** (fixed top, inside main-content) — platform title "Fish Mo", search bar, dark mode toggle, "个人主页" link (→ `/user/{id}`), "退出登录" button, username
3. **Content** (scrollable) — `<router-view />` via slot

State refs: `isCollapsed`, `isDarkMode`, `searchQuery`.

## Personal Profile Page (`UserHome.vue`)

The most complex view — a two-column layout with sidebar menu:

**Left sidebar:** Avatar + navigation menu (帖子, 评论, 链接, 收藏, 编辑资料, 退出登录)

**Right content area:** User info card + dynamic content switching via `activeTab`:
- **帖子** — `fetchHomeArticles(targetUserId)` from `GET /home/article/{userId}`
- **评论** — `fetchHomeComments(targetUserId)` from `GET /home/comment/{userId}`
- **链接** — `articleApi.getUserLinks()` from `GET /user/article/getlinklist`
- **收藏** — `request.get('/user/favorite/get_list')`
- **编辑资料** — inline form with avatar upload (base64), username/email/password/bio update, account deletion

**Key computed:** `isViewingOther` — checks if `route.params.userId !== userStore.id`; hides 编辑/删除/退出 when viewing another user's page.

**Route reuse:** When navigating between `/user/5` and `/user/3`, the component is reused — a `watch(() => route.params.userId)` triggers `loadUserData()` to re-fetch.

## API Patterns

All API calls return Axios responses directly. Two API modules:

- `src/api/article.ts` — `articleApi` object with all article/comment/link/favorite/home endpoints
- `src/api/user.ts` — `userApi` object with auth and profile endpoints

```ts
import { articleApi } from '@/api/article'

// List with pagination
const response = await articleApi.list(page, size, category, sort, order)
articles.value = response.data?.items || []

// Create — navigate on success
const { data } = await articleApi.publish({ title, category, content, images })
router.push(`/article/${data.id}`)

// Error handling
try {
  await articleApi.edit(id, payload)
} catch (err) {
  error.value = '用户-facing error message'
}
```

All api objects export plain functions returning AxiosPromise — no wrapper, no interceptor beyond request.ts.

## Content Rendering

Articles and announcements use Markdown via `markdown-it` + `DOMPurify`:

```ts
const md = new MarkdownIt({ html: true, linkify: true, typographer: true })
const renderedContent = computed(() => {
  if (!content.value) return ''
  return DOMPurify.sanitize(md.render(content.value))
})
// Template: <div class="markdown-content" v-html="renderedContent" />
```

### TOC from Markdown Headings (ArticleDetail.vue)

Article headings are extracted for a sidebar table of contents:

1. **`renderedContent` computed** — After `md.render()`, a regex injects `id="heading-0"` etc. into `<h1>`–`<h3>` tags so TOC items can scroll to them.
2. **`tocItems` computed** — Parses raw markdown (`/^(#{1,3})\s+(.+)$/gm`) into `{ id, text, level }[]`.
3. **Scrolling** — `scrollToHeading(index)` uses `document.getElementById()` + `element.scrollIntoView({ behavior: 'smooth' })`.

This is independent of `markdown-it` plugins — just string post-processing.

## ArticleDetail.vue Layout

The article page uses a **two-column layout** with a sticky left sidebar (`max-width: 1260px` container):

| Zone | Width | Content |
|---|---|---|
| Left sidebar | 220px | Author avatar (square, 10px radius) + name, table of contents, comment previews (first 10 chars) |
| Main content | `flex: 1` | Article body (markdown), links section, comments section |

The sidebar is `position: sticky; top: 6rem` and collapses to a horizontal card on mobile (<768px). The visit API response returns `{ title, content, images, author_id, author_name, author_avatar, views }` — all used directly without extra user-info API calls.

## Design System

Taste-skill design tokens applied project-wide:

| Token | Value |
|---|---|
| Primary text | `#18181B` (Zinc-950) |
| Secondary text | `#71717A` |
| Accent | `#3B82F6` (Electric Blue) |
| Accent hover | `#2563EB` |
| Success | `#10B981` (Emerald) |
| Error | `#E11D48` (Deep Rose) |
| Card bg | `rgba(255,255,255,0.7)` + `backdrop-blur(24px)` |
| Card border | `rgba(226,232,240,0.5)` |
| Card shadow | `0 20px 40px -15px rgba(0,0,0,0.05)` |
| Card radius | `1.25rem` |
| Input/button radius | `0.5rem` |
| Transition | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Font stack | `'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` |

**Rules when modifying styles:**
- Never use pure `#000` or `#fff` — use Zinc scale
- Never use `ease` transitions — use the cubic-bezier above
- Never use `h-screen` — use `min-h-[100dvh]`
- Do not modify `<script>` / `<script setup>` blocks when doing visual-only changes
- `src/assets/` and `src/components/` are gitignored — changes there won't be tracked

## Important Notes

- Node version requirement: `^20.19.0 || >=22.12.0` (enforced in package.json `engines`)
- The app runs at `http://0.0.0.0:5173` in dev mode — use `localhost:5173` to access
- `src/assets/` and `src/components/` are in `.gitignore` but must exist locally for the app to function
- Backend must be running at `127.0.0.1:8000` for API calls to work
- Vite dev proxy handles CORS during development (no need for `Access-Control-Allow-Origin` headers)
- Build chunks: `vendor` (vue/router/pinia) and `axios` are manually separated via `rollupOptions.output.manualChunks`
- Linting uses both oxlint (fast Rust-based) and eslint (with Vue/TS plugins), run sequentially
- Vite 7, Vue 3.5, vue-router 5, Pinia 3, TypeScript ~5.9
- Dark mode is toggled via CSS class on `.app` + `filter: brightness(0.7) contrast(1.1)`
