<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')
const isDarkMode = ref(
  window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
)
const isCollapsed = ref(true)

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
  }
})

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/search/${searchQuery.value.trim()}`)
    searchQuery.value = ''
  }
}
</script>

<template>
  <div class="app" :class="{ 'dark-mode': isDarkMode }">
    <div class="layout">
      <!-- ===== Top Navigation Bar ===== -->
      <header class="navbar">
        <div class="navbar-inner">
          <router-link to="/" class="navbar-brand" aria-label="Fish Mo 首页">
            <span class="brand-mark">
              <img src="/favicon.ico" alt="Fish Mo" class="brand-icon" />
            </span>
            <span class="brand-text">Fish Mo</span>
          </router-link>

          <nav
            class="navbar-links"
            :class="{ 'is-open': !isCollapsed }"
            @click="isCollapsed = true"
          >
            <router-link to="/" class="nav-link">首页</router-link>
            <router-link to="/publish" class="nav-link">发布帖子</router-link>
            <router-link to="/announcement" class="nav-link">更新栏</router-link>
            <template v-if="userStore.isLoggedIn">
              <router-link to="/tools" class="nav-link">工具</router-link>
            </template>
            <template v-else>
              <router-link to="/login" class="nav-link">登录</router-link>
              <router-link to="/register" class="nav-link">注册</router-link>
            </template>
          </nav>

          <div class="navbar-actions">
            <div class="search-box">
              <svg
                class="search-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="7"></circle>
                <line x1="16.5" y1="16.5" x2="21" y2="21"></line>
              </svg>
              <input
                type="text"
                v-model="searchQuery"
                placeholder="搜索文章..."
                class="search-input"
                @keyup.enter="handleSearch"
              />
              <button @click="handleSearch" class="search-btn" aria-label="搜索">搜索</button>
            </div>

            <button
              class="icon-btn"
              @click="toggleDarkMode"
              :title="isDarkMode ? '切换亮色' : '切换暗色'"
              aria-label="切换主题"
            >
              <svg
                v-if="isDarkMode"
                class="icon-sun"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"></path>
              </svg>
              <svg
                v-else
                class="icon-moon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
              </svg>
            </button>

            <template v-if="userStore.isLoggedIn">
              <router-link :to="`/user/${userStore.id}`" class="nav-profile">
                <span class="nav-profile-dot" aria-hidden="true"></span>
                <span class="nav-profile-text">个人主页</span>
              </router-link>
              <button @click="userStore.logout()" class="logout-btn">退出登录</button>
            </template>

            <button
              class="hamburger"
              @click="toggleSidebar"
              :title="isCollapsed ? '展开菜单' : '收起菜单'"
              aria-label="展开菜单"
              :aria-expanded="!isCollapsed"
            >
              <span class="hamburger-bar" :class="{ 'is-open': !isCollapsed }"></span>
              <span class="hamburger-bar" :class="{ 'is-open': !isCollapsed }"></span>
              <span class="hamburger-bar" :class="{ 'is-open': !isCollapsed }"></span>
            </button>
          </div>
        </div>
      </header>

      <!-- ===== Content ===== -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    'Geist',
    'Inter',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    sans-serif;
  line-height: 1.65;
  color: #18181b;
  background: url('@/assets/background.jpg') no-repeat center center fixed;
  background-size: cover;
  min-height: 100dvh;
  overflow: hidden;
}

.app {
  min-height: 100dvh;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.app.dark-mode {
  filter: brightness(0.7) contrast(1.1);
}

.layout {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* =======================================================
   Top Navigation Bar
   ======================================================= */
.navbar {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.navbar-inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* ----- Brand ----- */
.navbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.25rem 0.5rem;
  margin-left: -0.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.navbar-brand:hover {
  background: rgba(59, 130, 246, 0.06);
}

.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 0.625rem;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  flex-shrink: 0;
}

.brand-icon {
  width: 30px;
  height: 30px;
  object-fit: contain;
  display: block;
}

.brand-text {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #18181b;
  white-space: nowrap;
}

/* ----- Primary nav links ----- */
.navbar-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.nav-link {
  position: relative;
  padding: 0.5rem 0.875rem;
  border-radius: 0.625rem;
  text-decoration: none;
  color: #52525b;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.005em;
  white-space: nowrap;
  transition:
    color 0.3s cubic-bezier(0.16, 1, 0.3, 1),
    background-color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-link::after {
  content: '';
  position: absolute;
  left: 0.875rem;
  right: 0.875rem;
  bottom: 2px;
  height: 2px;
  border-radius: 2px;
  background: #3b82f6;
  transform: scaleX(0);
  transform-origin: center;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-link:hover {
  background: rgba(59, 130, 246, 0.08);
  color: #18181b;
}

.nav-link:hover::after {
  transform: scaleX(1);
}

.nav-link:active {
  transform: scale(0.97);
}

.nav-link.router-link-exact-active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  font-weight: 600;
}

.nav-link.router-link-exact-active::after {
  transform: scaleX(1);
}

/* ----- Right actions ----- */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-left: auto;
  flex-shrink: 0;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 320px;
  min-width: 0;
  flex-shrink: 1;
  height: 38px;
  padding: 0 0.5rem 0 0.875rem;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 0.5rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.search-box:focus-within {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.search-icon {
  width: 16px;
  height: 16px;
  color: #71717a;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-size: 0.9rem;
  color: #18181b;
  outline: none;
  font-family: inherit;
}

.search-input::placeholder {
  color: #a1a1aa;
}

.search-btn {
  height: 28px;
  padding: 0 0.875rem;
  border: none;
  border-radius: 0.5rem;
  background: #3b82f6;
  color: #f9fafb;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.search-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.search-btn:active {
  transform: scale(0.97);
}

.icon-btn {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 0.5rem;
  border: 1px solid rgba(226, 232, 240, 0.7);
  background: rgba(255, 255, 255, 0.6);
  color: #52525b;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.1);
}

.icon-btn:active {
  transform: scale(0.94);
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

.nav-profile {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  height: 38px;
  padding: 0 0.875rem;
  border-radius: 0.5rem;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.18);
  color: #3b82f6;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-profile:hover {
  background: #3b82f6;
  color: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px -2px rgba(59, 130, 246, 0.4);
}

.nav-profile:active {
  transform: scale(0.97);
}

.nav-profile-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.logout-btn {
  height: 38px;
  padding: 0 0.875rem;
  border-radius: 0.5rem;
  background: none;
  border: 1px solid rgba(225, 29, 72, 0.25);
  color: #e11d48;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  white-space: nowrap;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.logout-btn:hover {
  background: #e11d48;
  color: #f9fafb;
  transform: translateY(-1px);
}

.logout-btn:active {
  transform: scale(0.97);
}

/* ----- Hamburger (mobile) ----- */
.hamburger {
  display: none;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(226, 232, 240, 0.7);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.hamburger:hover {
  background: rgba(255, 255, 255, 0.9);
}

.hamburger-bar {
  display: block;
  width: 16px;
  height: 2px;
  border-radius: 2px;
  background: #18181b;
  transform-origin: center;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.hamburger-bar.is-open:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.hamburger-bar.is-open:nth-child(2) {
  opacity: 0;
  transform: scaleX(0);
}

.hamburger-bar.is-open:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}

/* =======================================================
   Content
   ======================================================= */
.content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 2rem;
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.35) transparent;
}

.content::-webkit-scrollbar {
  width: 8px;
}

.content::-webkit-scrollbar-track {
  background: transparent;
}

.content::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.35);
  border-radius: 4px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.55);
}

/* 毛玻璃卡片样式 (shared global, used by views) */
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 2rem;
  margin: 0 auto;
  max-width: 960px;
}

/* =======================================================
   Dark mode
   ======================================================= */
.app.dark-mode .navbar {
  background: rgba(30, 30, 30, 0.55);
  border-bottom-color: rgba(255, 255, 255, 0.1);
  box-shadow: none;
}

.app.dark-mode .brand-mark {
  background: rgba(40, 40, 40, 0.6);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: none;
}

.app.dark-mode .brand-text {
  color: rgba(255, 255, 255, 0.92);
}

.app.dark-mode .navbar-brand:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .nav-link {
  color: rgba(255, 255, 255, 0.72);
}

.app.dark-mode .nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
}

.app.dark-mode .nav-link.router-link-exact-active {
  background: rgba(59, 130, 246, 0.25);
  color: rgba(147, 197, 253, 0.95);
}

.app.dark-mode .search-box {
  background: rgba(40, 40, 40, 0.45);
  border-color: rgba(255, 255, 255, 0.12);
}

.app.dark-mode .search-box:focus-within {
  border-color: rgba(59, 130, 246, 0.7);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

.app.dark-mode .search-input {
  color: rgba(255, 255, 255, 0.92);
}

.app.dark-mode .search-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.app.dark-mode .search-icon {
  color: rgba(255, 255, 255, 0.5);
}

.app.dark-mode .icon-btn {
  background: rgba(40, 40, 40, 0.45);
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.8);
}

.app.dark-mode .icon-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: rgba(147, 197, 253, 0.95);
  box-shadow: none;
}

.app.dark-mode .nav-profile {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
  color: rgba(147, 197, 253, 0.9);
}

.app.dark-mode .nav-profile:hover {
  background: #3b82f6;
  color: #f9fafb;
}

.app.dark-mode .logout-btn {
  border-color: rgba(225, 29, 72, 0.4);
  color: rgba(251, 113, 133, 0.9);
}

.app.dark-mode .logout-btn:hover {
  background: #e11d48;
  color: #f9fafb;
}

.app.dark-mode .hamburger {
  background: rgba(40, 40, 40, 0.45);
  border-color: rgba(255, 255, 255, 0.12);
}

.app.dark-mode .hamburger-bar {
  background: rgba(255, 255, 255, 0.9);
}

.app.dark-mode .glass-card {
  background: rgba(40, 40, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* Legacy global helpers kept for any view references */
.username {
  font-weight: 700;
  color: #18181b;
  white-space: nowrap;
}

.app.dark-mode .username {
  color: rgba(255, 255, 255, 0.9);
}

.app.dark-mode .logout-link {
  color: rgba(255, 102, 102, 0.9) !important;
}

.app.dark-mode .logout-link:hover {
  background: rgba(225, 29, 72, 0.15) !important;
}

/* =======================================================
   Responsive
   ======================================================= */
@media (max-width: 1100px) {
  .navbar-inner {
    gap: 1rem;
  }

  .nav-link {
    padding: 0.5rem 0.75rem;
  }

  .search-box {
    width: 240px;
  }
}

@media (max-width: 960px) {
  .navbar-inner {
    height: 56px;
    padding: 0 1rem;
    gap: 0.75rem;
  }

  .navbar-links {
    position: absolute;
    top: calc(100% + 8px);
    left: 1rem;
    right: 1rem;
    flex-direction: column;
    align-items: stretch;
    gap: 0.25rem;
    padding: 0.625rem;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(226, 232, 240, 0.7);
    border-radius: 1rem;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.12);
    opacity: 0;
    transform: translateY(-6px);
    pointer-events: none;
    transition:
      opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1),
      transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .navbar-links.is-open {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
  }

  .nav-link {
    width: 100%;
    text-align: left;
    padding: 0.625rem 0.875rem;
  }

  .nav-link::after {
    display: none;
  }

  .search-box {
    width: auto;
    flex: 1;
    max-width: none;
  }

  .nav-profile-text {
    display: none;
  }

  .nav-profile {
    width: 38px;
    padding: 0;
    justify-content: center;
  }

  .hamburger {
    display: inline-flex;
  }

  .content {
    padding: 1.25rem;
  }

  .app.dark-mode .navbar-links {
    background: rgba(30, 30, 30, 0.85);
    border-color: rgba(255, 255, 255, 0.12);
  }
}

@media (max-width: 560px) {
  .brand-text {
    display: none;
  }

  .search-btn {
    display: none;
  }

  .logout-btn {
    padding: 0 0.625rem;
    font-size: 0.8rem;
  }

  .content {
    padding: 1rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
</style>
