<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/api/request'
import { articleApi } from '@/api/article'
import { userApi } from '@/api/user'
import type { HomeArticleItem, HomeCommentItem, LinkResponse } from '@/api/article'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// Active tab for sidebar navigation
const activeTab = ref<'posts' | 'comments' | 'links' | 'favorites' | 'edit'>('posts')

// 优先使用路由参数 userId(/user/5)，其次是查询参数(?userId=5)，最后用当前登录用户 ID
const targetUserId = computed(() => {
  const param = Number(route.params.userId || route.query.userId)
  if (param > 0) return param
  return userStore.id || 0
})

const userInfo = ref({
  username: '',
  email: '',
  avatar: '',
  bio: '',
  article_count: 0
})
const loading = ref(true)

// --- 文章列表 ---
const homeArticles = ref<HomeArticleItem[]>([])
const homeArticlesLoading = ref(false)
const homeArticlesError = ref('')
const homeArticlesPage = ref(1)
const homeArticlesPageSize = ref(5)

const fetchHomeArticles = async () => {
  if (!targetUserId.value) return
  homeArticlesLoading.value = true
  homeArticlesError.value = ''
  try {
    const response = await articleApi.getHomeArticles(targetUserId.value, homeArticlesPage.value, homeArticlesPageSize.value)
    homeArticles.value = response.data?.articles || []
  } catch (err) {
    homeArticlesError.value = '加载文章失败'
    homeArticles.value = []
    console.error(err)
  } finally {
    homeArticlesLoading.value = false
  }
}

const handleHomeArticlesPrev = () => {
  if (homeArticlesPage.value > 1) {
    homeArticlesPage.value--
    fetchHomeArticles()
  }
}

const handleHomeArticlesNext = () => {
  homeArticlesPage.value++
  fetchHomeArticles()
}

// --- 评论列表 ---
const homeComments = ref<HomeCommentItem[]>([])
const homeCommentsLoading = ref(false)
const homeCommentsError = ref('')
const homeCommentsPage = ref(1)
const homeCommentsPageSize = ref(5)

const fetchHomeComments = async () => {
  if (!targetUserId.value) return
  homeCommentsLoading.value = true
  homeCommentsError.value = ''
  try {
    const response = await articleApi.getHomeComments(targetUserId.value, homeCommentsPage.value, homeCommentsPageSize.value)
    homeComments.value = response.data?.comments || []
  } catch (err) {
    homeCommentsError.value = '加载评论失败'
    homeComments.value = []
    console.error(err)
  } finally {
    homeCommentsLoading.value = false
  }
}

const handleHomeCommentsPrev = () => {
  if (homeCommentsPage.value > 1) {
    homeCommentsPage.value--
    fetchHomeComments()
  }
}

const handleHomeCommentsNext = () => {
  homeCommentsPage.value++
  fetchHomeComments()
}

const deleteArticleLoading = ref<number | null>(null)

const handleDeleteArticle = async (id: number) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  deleteArticleLoading.value = id
  try {
    await articleApi.deleteArticle(id)
    fetchHomeArticles()
  } catch (err) {
    console.error('删除失败:', err)
  } finally {
    deleteArticleLoading.value = null
  }
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString()

// --- 链接列表 ---
const userLinks = ref<LinkResponse[]>([])
const userLinksLoading = ref(false)
const userLinksError = ref('')
const userLinksPage = ref(1)
const userLinksPageSize = ref(10)

const fetchUserLinks = async () => {
  if (!targetUserId.value) return
  userLinksLoading.value = true
  userLinksError.value = ''
  try {
    const response = await articleApi.getUserLinks(userLinksPage.value, userLinksPageSize.value)
    userLinks.value = response.data.links || []
  } catch (err) {
    userLinksError.value = '加载链接失败'
    userLinks.value = []
    console.error(err)
  } finally {
    userLinksLoading.value = false
  }
}

// --- 收藏列表 ---
interface FavoriteArticle {
  id: number
  title: string
  category: string
  created_at: string
  views: number
  likes: number
}

const favorites = ref<FavoriteArticle[]>([])
const favoritesLoading = ref(false)
const favoritesError = ref('')
const favoritesPage = ref(1)
const favoritesPageSize = ref(10)

const fetchFavorites = async () => {
  if (!targetUserId.value) return
  favoritesLoading.value = true
  favoritesError.value = ''
  try {
    const response = await request.get('/user/favorite/get_list', {
      params: { id: targetUserId.value, page: favoritesPage.value, size: favoritesPageSize.value }
    })
    favorites.value = response.data?.favorites || []
  } catch (err) {
    favoritesError.value = '加载收藏失败'
    favorites.value = []
    console.error(err)
  } finally {
    favoritesLoading.value = false
  }
}

// --- 编辑资料 ---
const newUsername = ref('')
const newEmail = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const newBio = ref('')
const editError = ref('')
const editSuccess = ref('')
const editLoading = ref(false)

const avatarUrl = ref('/upload/avatars/default_avatar.webp')
const avatarInput = ref<HTMLInputElement | null>(null)
const avatarLoading = ref(false)

const loadAvatar = async () => {
  try {
    const response = await userApi.getInfo()
    if (response.data && response.data.avatar) {
      avatarUrl.value = response.data.avatar + '?t=' + new Date().getTime()
    }
  } catch (err) {
    console.error('获取头像失败:', err)
  }
}

const handleAvatarChange = () => avatarInput.value?.click()

const handleAvatarFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    editError.value = '头像文件大小不能超过5MB'
    return
  }
  if (!file.type.startsWith('image/')) {
    editError.value = '请选择图片文件'
    return
  }
  avatarLoading.value = true
  editError.value = ''
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64Data = e.target?.result as string
      if (!base64Data) { avatarLoading.value = false; return }
      try {
        const response = await userApi.updateAvatar(base64Data)
        if (response.data?.user?.avatar) {
          const newAvatar = response.data.user.avatar + '?t=' + new Date().getTime()
          avatarUrl.value = newAvatar
          userInfo.value.avatar = newAvatar
          editSuccess.value = '头像更新成功'
        }
      } catch {
        editError.value = '更新头像失败'
      } finally { avatarLoading.value = false }
    }
    reader.readAsDataURL(file)
  } catch {
    editError.value = '图片读取失败'
    avatarLoading.value = false
  }
}

const handleUpdate = async () => {
  if (newPassword.value && newPassword.value !== confirmPassword.value) {
    editError.value = '新密码不匹配'
    return
  }
  editLoading.value = true
  editError.value = ''
  editSuccess.value = ''
  try {
    await userApi.update({
      new_username: newUsername.value || undefined,
      new_email: newEmail.value || undefined,
      new_password: newPassword.value || undefined,
      new_bio: newBio.value || undefined
    })
    editSuccess.value = '资料更新成功'
    if (newUsername.value) userStore.username = newUsername.value
  } catch {
    editError.value = '更新资料失败'
  } finally { editLoading.value = false }
}

const handleDeleteAccount = async () => {
  if (!confirm('您确定要删除您的账户吗？此操作不可撤销。')) return
  editLoading.value = true
  editError.value = ''
  editSuccess.value = ''
  try {
    await userApi.delete(true)
    userStore.logout()
    window.location.href = '/'
  } catch {
    editError.value = '删除账户失败'
  } finally { editLoading.value = false }
}

const isViewingOther = computed(() => {
  const param = Number(route.params.userId)
  return param > 0 && param !== userStore.id
})

const fetchUserInfo = async () => {
  try {
    const params = targetUserId.value ? { user_id: targetUserId.value } : {}
    const response = await request.get('/home/', { params })
    const data = response.data
    userInfo.value = {
      username: data.username || '',
      email: data.email || '',
      avatar: data.avatar || '',
      bio: data.bio || '',
      article_count: data.article_count || 0
    }
  } catch (err) {
    console.error('获取用户信息失败:', err)
  }
}

const loadUserData = async () => {
  loading.value = true
  await fetchUserInfo()
  if (!isViewingOther.value) loadAvatar()
  if (targetUserId.value) {
    homeArticlesPage.value = 1
    homeCommentsPage.value = 1
    userLinksPage.value = 1
    favoritesPage.value = 1
    fetchHomeArticles()
    fetchHomeComments()
    fetchUserLinks()
    fetchFavorites()
  }
  loading.value = false
}

onMounted(loadUserData)

// 同一组件内路由参数变化时重新加载（如 /user/5 → /user/3）
watch(() => route.params.userId, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    loadUserData()
  }
})
</script>

<template>
  <div class="user-home-page">
    <div v-if="loading" class="loading-state">
      <span>加载中...</span>
    </div>

    <div v-else class="user-layout">
      <!-- ===== Left Sidebar: Avatar + Navigation ===== -->
      <aside class="user-sidebar">
        <div class="sidebar-avatar-wrapper" :title="userInfo.username">
          <img
            :src="userInfo.avatar || '/default-avatar.png'"
            :alt="userInfo.username"
            class="sidebar-avatar"
          />
        </div>

        <div class="sidebar-divider" />

        <nav class="sidebar-menu">
          <button
            class="menu-item"
            :class="{ active: activeTab === 'posts' }"
            @click="activeTab = 'posts'"
          >
            <span class="menu-indicator" />
            <span class="menu-label">帖子</span>
          </button>

          <button
            class="menu-item"
            :class="{ active: activeTab === 'comments' }"
            @click="activeTab = 'comments'"
          >
            <span class="menu-indicator" />
            <span class="menu-label">评论</span>
          </button>

          <button
            class="menu-item"
            :class="{ active: activeTab === 'links' }"
            @click="activeTab = 'links'"
          >
            <span class="menu-indicator" />
            <span class="menu-label">链接</span>
          </button>

          <button
            class="menu-item"
            :class="{ active: activeTab === 'favorites' }"
            @click="activeTab = 'favorites'"
          >
            <span class="menu-indicator" />
            <span class="menu-label">收藏</span>
          </button>

          <button
            v-if="!isViewingOther"
            class="menu-item"
            :class="{ active: activeTab === 'edit' }"
            @click="activeTab = 'edit'"
          >
            <span class="menu-indicator" />
            <span class="menu-label">编辑资料</span>
          </button>

          <button
            v-if="!isViewingOther"
            class="menu-item menu-logout"
            @click="userStore.logout(); router.push('/')"
          >
            <span class="menu-indicator" />
            <span class="menu-label">退出登录</span>
          </button>
        </nav>
      </aside>

      <!-- ===== Right Column: User Info + Content ===== -->
      <main class="user-content">
        <!-- User Info Card -->
        <div class="user-info-card">
          <h1 class="info-username">{{ userInfo.username }}</h1>
          <div class="info-details">
            <p v-if="userInfo.email" class="info-email">{{ userInfo.email }}</p>
            <p v-if="userInfo.bio" class="info-bio">{{ userInfo.bio }}</p>
            <p v-if="!userInfo.email && !userInfo.bio" class="info-bio muted">暂无个人简介</p>
          </div>
          <div class="info-stat">
            <span class="stat-item">
              <span class="stat-value">{{ userInfo.article_count }}</span>
              <span class="stat-label">篇文章</span>
            </span>
          </div>
        </div>

        <!-- Dynamic Content Area -->
        <div class="content-area">
          <!-- 帖子 Section -->
          <div v-if="activeTab === 'posts'" class="content-section">
            <div class="section-header">
              <h2 class="section-title">{{ isViewingOther ? `${userInfo.username} 的文章` : '我的文章' }}</h2>
              <router-link v-if="!isViewingOther" to="/publish" class="add-btn">+ 发布文章</router-link>
            </div>
            <div v-if="homeArticlesLoading" class="loading-state">加载中...</div>
            <div v-else-if="homeArticlesError" class="error-msg">{{ homeArticlesError }}</div>
            <div v-else>
              <div class="article-list">
                <div v-for="article in homeArticles" :key="'ha-' + article.id" class="article-card">
                  <div class="article-card-top">
                    <router-link :to="`/article/${article.id}`" class="article-title">{{ article.title }}</router-link>
                    <div v-if="!isViewingOther" class="article-actions">
                      <router-link :to="`/edit/${article.id}`" class="action-btn edit-btn">编辑</router-link>
                      <button class="action-btn delete-btn" @click="handleDeleteArticle(article.id)">删除</button>
                    </div>
                  </div>
                  <div class="article-meta">
                    <span class="article-category">{{ article.category }}</span>
                    <span class="article-date">{{ formatDate(article.created_at) }}</span>
                  </div>
                  <div class="article-stats">
                    <span class="stat-view">{{ article.views }} views</span>
                    <span class="stat-like">{{ article.likes }} likes</span>
                  </div>
                </div>
                <div v-if="homeArticles.length === 0" class="empty-state">暂无文章</div>
              </div>
              <div class="pagination-bar">
                <button @click="handleHomeArticlesPrev" :disabled="homeArticlesPage === 1" class="page-btn">上一页</button>
                <span class="page-info">第 {{ homeArticlesPage }} 页</span>
                <button @click="handleHomeArticlesNext" :disabled="homeArticles.length < homeArticlesPageSize" class="page-btn">下一页</button>
              </div>
            </div>
          </div>

          <!-- 评论 Section -->
          <div v-else-if="activeTab === 'comments'" class="content-section">
            <div class="section-header">
              <h2 class="section-title">{{ isViewingOther ? `${userInfo.username} 的评论` : '我的评论' }}</h2>
            </div>
            <div v-if="homeCommentsLoading" class="loading-state">加载中...</div>
            <div v-else-if="homeCommentsError" class="error-msg">{{ homeCommentsError }}</div>
            <div v-else>
              <div class="comment-list">
                <div v-for="(comment, index) in homeComments" :key="'hc-' + index" class="comment-card">
                  <div class="comment-content">{{ comment.content }}</div>
                  <div class="comment-footer">
                    <router-link :to="`/article/${comment.article_id}`" class="comment-link">查看原文 #{{ comment.article_id }}</router-link>
                    <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  </div>
                </div>
                <div v-if="homeComments.length === 0" class="empty-state">暂无评论</div>
              </div>
              <div class="pagination-bar">
                <button @click="handleHomeCommentsPrev" :disabled="homeCommentsPage === 1" class="page-btn">上一页</button>
                <span class="page-info">第 {{ homeCommentsPage }} 页</span>
                <button @click="handleHomeCommentsNext" :disabled="homeComments.length < homeCommentsPageSize" class="page-btn">下一页</button>
              </div>
            </div>
          </div>

          <!-- 链接 Section -->
          <div v-else-if="activeTab === 'links'" class="content-section">
            <div class="section-header">
              <h2 class="section-title">{{ isViewingOther ? `${userInfo.username} 的链接` : '我的链接' }}</h2>
            </div>
            <div v-if="userLinksLoading" class="loading-state">加载中...</div>
            <div v-else-if="userLinksError" class="error-msg">{{ userLinksError }}</div>
            <div v-else>
              <div class="links-list">
                <div v-for="link in userLinks" :key="link.id" class="link-card">
                  <div class="link-info">
                    <a :href="link.url" target="_blank" rel="noopener noreferrer" class="link-url">{{ link.title || link.url }}</a>
                    <span class="link-url-full">{{ link.url }}</span>
                  </div>
                  <span class="link-article">文章 #{{ link.article_id }}</span>
                </div>
                <div v-if="userLinks.length === 0" class="empty-state">暂无链接</div>
              </div>
              <div class="pagination-bar">
                <button @click="userLinksPage > 1 && (userLinksPage--, fetchUserLinks())" :disabled="userLinksPage === 1" class="page-btn">上一页</button>
                <span class="page-info">第 {{ userLinksPage }} 页</span>
                <button @click="userLinksPage++, fetchUserLinks()" :disabled="userLinks.length < userLinksPageSize" class="page-btn">下一页</button>
              </div>
            </div>
          </div>

          <!-- 收藏 Section -->
          <div v-else-if="activeTab === 'favorites'" class="content-section">
            <div class="section-header">
              <h2 class="section-title">{{ isViewingOther ? `${userInfo.username} 的收藏` : '我的收藏' }}</h2>
            </div>
            <div v-if="favoritesLoading" class="loading-state">加载中...</div>
            <div v-else-if="favoritesError" class="error-msg">{{ favoritesError }}</div>
            <div v-else>
              <div class="article-list">
                <div v-for="fav in favorites" :key="'fav-' + fav.id" class="article-card">
                  <router-link :to="`/article/${fav.id}`" class="article-title">{{ fav.title }}</router-link>
                  <div class="article-meta">
                    <span class="article-category">{{ fav.category }}</span>
                    <span class="article-date">{{ formatDate(fav.created_at) }}</span>
                  </div>
                  <div class="article-stats">
                    <span class="stat-view">{{ fav.views }} views</span>
                    <span class="stat-like">{{ fav.likes }} likes</span>
                  </div>
                </div>
                <div v-if="favorites.length === 0" class="empty-state">暂无收藏</div>
              </div>
            </div>
          </div>

          <!-- 编辑资料 Section -->
          <div v-else-if="activeTab === 'edit'" class="content-section">
            <div class="section-header">
              <h2 class="section-title">编辑资料</h2>
            </div>

            <form @submit.prevent="handleUpdate" class="edit-profile">
              <!-- 头像 -->
              <section class="edit-card">
                <div class="edit-card-header">
                  <h3 class="edit-card-title">头像</h3>
                  <p class="edit-card-desc">点击头像更换</p>
                </div>
                <div class="edit-card-body">
                  <div class="edit-avatar-section">
                    <div class="edit-avatar-wrapper" @click="handleAvatarChange">
                      <img :src="avatarUrl" alt="头像" class="edit-avatar" :class="{ loading: avatarLoading }" />
                      <div v-if="!avatarLoading" class="edit-avatar-overlay"><span>更换头像</span></div>
                      <div v-else class="edit-avatar-loading"><span>上传中...</span></div>
                    </div>
                    <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarFileSelect" />
                    <p class="edit-avatar-hint">支持 jpg、png、webp，大小不超过 5MB</p>
                  </div>
                </div>
              </section>

              <!-- 基本信息 -->
              <section class="edit-card">
                <div class="edit-card-header">
                  <h3 class="edit-card-title">基本信息</h3>
                  <p class="edit-card-desc">用户名、邮箱与个人简介</p>
                </div>
                <div class="edit-card-body">
                  <div class="edit-form">
                    <div class="edit-form-group">
                      <label for="newUsername">新用户名（可选）</label>
                      <input type="text" id="newUsername" v-model="newUsername" :disabled="editLoading" placeholder="输入新用户名" />
                    </div>
                    <div class="edit-form-group">
                      <label for="newEmail">新邮箱（可选）</label>
                      <input type="email" id="newEmail" v-model="newEmail" :disabled="editLoading" placeholder="输入新邮箱" />
                    </div>
                    <div class="edit-form-group">
                      <label for="newBio">个人简介（可选）</label>
                      <textarea id="newBio" v-model="newBio" rows="4" :disabled="editLoading" placeholder="介绍一下自己..."></textarea>
                    </div>
                  </div>
                </div>
              </section>

              <!-- 修改密码 -->
              <section class="edit-card">
                <div class="edit-card-header">
                  <h3 class="edit-card-title">修改密码</h3>
                  <p class="edit-card-desc">如不修改请留空</p>
                </div>
                <div class="edit-card-body">
                  <div class="edit-form">
                    <div class="edit-form-group">
                      <label for="newPassword">新密码（可选）</label>
                      <input type="password" id="newPassword" v-model="newPassword" :disabled="editLoading" autocomplete="new-password" placeholder="••••••••" />
                    </div>
                    <div class="edit-form-group">
                      <label for="confirmPassword">确认新密码</label>
                      <input type="password" id="confirmPassword" v-model="confirmPassword" :disabled="editLoading" autocomplete="new-password" placeholder="••••••••" />
                    </div>
                  </div>
                </div>
              </section>

              <!-- 危险区域 -->
              <section class="edit-card edit-card-danger">
                <div class="edit-card-header">
                  <h3 class="edit-card-title">危险区域</h3>
                  <p class="edit-card-desc">请谨慎操作</p>
                </div>
                <div class="edit-card-body">
                  <div class="edit-delete-section">
                    <p>此操作不可撤销。您的账户和所有相关数据将被永久删除。</p>
                    <button type="button" class="edit-delete-btn" @click="handleDeleteAccount" :disabled="editLoading">
                      {{ editLoading ? '处理中...' : '删除账户' }}
                    </button>
                  </div>
                </div>
              </section>

              <!-- 提交 -->
              <div class="edit-form-footer">
                <div v-if="editError" class="edit-msg error-msg">{{ editError }}</div>
                <div v-if="editSuccess" class="edit-msg success-msg">{{ editSuccess }}</div>
                <button type="submit" class="edit-submit-btn" :disabled="editLoading">
                  {{ editLoading ? '更新中...' : '保存修改' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* =======================================================
   UserHome — Two-column taste-skill layout
   ======================================================= */

.user-home-page {
  min-height: 100dvh;
  padding: 2rem 2.5rem;
}

/* ----- Loading state ----- */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #71717A;
  font-size: 0.95rem;
  font-weight: 500;
  letter-spacing: 0.01em;
}

/* ----- Two-column layout ----- */
.user-layout {
  display: flex;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  align-items: flex-start;
}

/* =======================================================
   Left Sidebar
   ======================================================= */
.user-sidebar {
  position: sticky;
  top: 2rem;
  flex-shrink: 0;
  width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1.5rem 1.75rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

/* Avatar */
.sidebar-avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(59, 130, 246, 0.1));
}

.sidebar-avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.95);
  display: block;
}

/* Divider */
.sidebar-divider {
  width: 48px;
  height: 1px;
  background: rgba(226, 232, 240, 0.7);
  margin: 1.5rem 0;
  flex-shrink: 0;
}

/* Navigation menu */
.sidebar-menu {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.7rem 1rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: #52525B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.menu-indicator {
  width: 3px;
  height: 18px;
  border-radius: 3px;
  background: transparent;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.menu-label {
  transition: color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.menu-item:hover {
  background: rgba(59, 130, 246, 0.06);
  color: #18181B;
}

.menu-item:hover .menu-indicator {
  background: rgba(59, 130, 246, 0.25);
}

.menu-item.active {
  color: #3B82F6;
  background: rgba(59, 130, 246, 0.08);
  font-weight: 600;
}

.menu-item.active .menu-indicator {
  background: #3B82F6;
}

.menu-item:active {
  transform: scale(0.98);
}

/* --- Logout button in menu --- */
.menu-logout {
  margin-top: auto;
  color: #E11D48 !important;
  border-top: 1px solid rgba(226, 232, 240, 0.4);
  padding-top: 0.75rem !important;
  margin-top: 0.75rem;
  width: 100%;
  font-family: inherit;
  font-size: inherit;
  text-align: left;
}

.menu-logout:hover {
  background: rgba(225, 29, 72, 0.08) !important;
  color: #E11D48 !important;
}

.menu-logout .menu-indicator {
  background: rgba(225, 29, 72, 0.25) !important;
}

/* =======================================================
   Right Column — Content
   ======================================================= */
.user-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ----- User Info Card ----- */
.user-info-card {
  padding: 1.75rem 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.info-username {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #18181B;
  letter-spacing: -0.025em;
  margin: 0 0 0.5rem;
}

.info-details {
  margin-bottom: 1rem;
}

.info-email {
  font-size: 0.875rem;
  color: #3B82F6;
  margin: 0 0 0.25rem;
  font-weight: 500;
}

.info-bio {
  font-size: 0.9rem;
  color: #71717A;
  margin: 0;
  line-height: 1.6;
}

.info-bio.muted {
  font-style: italic;
  opacity: 0.7;
}

.info-stat {
  display: flex;
  gap: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 0.35rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #18181B;
  line-height: 1;
}

.stat-label {
  font-size: 0.825rem;
  color: #A1A1AA;
  font-weight: 500;
}

/* ----- Dynamic Content Area ----- */
.content-area {
  min-height: 300px;
}

.content-section {
  animation: fadeSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  margin-bottom: 1.25rem;
}

.section-title {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #18181B;
  letter-spacing: -0.015em;
  margin: 0;
}

/* ----- Article card actions ----- */
.add-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 1rem;
  background: #3B82F6;
  color: #F9FAFB;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.add-btn:hover {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.add-btn:active {
  transform: scale(0.97);
}

.article-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.article-actions {
  display: flex;
  gap: 0.4rem;
  flex-shrink: 0;
}

.action-btn {
  padding: 0.25rem 0.65rem;
  border-radius: 0.4rem;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid transparent;
}

.edit-btn {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
  border-color: rgba(59, 130, 246, 0.2);
}

.edit-btn:hover {
  background: #3B82F6;
  color: #F9FAFB;
  transform: translateY(-1px);
}

.delete-btn {
  background: rgba(225, 29, 72, 0.1);
  color: #E11D48;
  border-color: rgba(225, 29, 72, 0.2);
}

.delete-btn:hover {
  background: #E11D48;
  color: #F9FAFB;
  transform: translateY(-1px);
}

.action-btn:active {
  transform: scale(0.95);
}

/* ----- Error ----- */
.error-msg {
  text-align: center;
  padding: 1.5rem 1rem;
  color: #E11D48;
  background: rgba(225, 29, 72, 0.06);
  border: 1px solid rgba(225, 29, 72, 0.15);
  border-radius: 0.75rem;
  font-size: 0.9rem;
}

/* --- Link card --- */
.links-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.link-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 1.25rem 1.5rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.link-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
}

.link-info {
  flex: 1;
  min-width: 0;
}

.link-url {
  display: block;
  font-weight: 600;
  color: #3B82F6;
  text-decoration: none;
  font-size: 0.95rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s;
}

.link-url:hover {
  color: #2563EB;
  text-decoration: underline;
}

.link-url-full {
  display: block;
  font-size: 0.8rem;
  color: #94A3B8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-article {
  flex-shrink: 0;
  margin-left: 1rem;
  font-size: 0.8rem;
  color: #71717A;
  background: rgba(59, 130, 246, 0.08);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

/* ----- Empty state ----- */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #A1A1AA;
  font-size: 0.9rem;
}

/* ----- Article List ----- */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.article-card {
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
  border-color: rgba(59, 130, 246, 0.2);
}

.article-title {
  display: block;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #18181B;
  text-decoration: none;
  margin-bottom: 0.5rem;
  letter-spacing: -0.01em;
  line-height: 1.4;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-title:hover {
  color: #3B82F6;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}

.article-category {
  font-size: 0.75rem;
  font-weight: 600;
  color: #3B82F6;
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.08);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.article-date {
  font-size: 0.8rem;
  color: #A1A1AA;
}

.article-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.775rem;
  color: #A1A1AA;
}

.stat-view,
.stat-like {
  position: relative;
}

.stat-view::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #D4D4D8;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.stat-like::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #D4D4D8;
  margin-right: 0.5rem;
  vertical-align: middle;
}

/* ----- Comment List ----- */
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.comment-card {
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.08);
}

.comment-content {
  font-size: 0.925rem;
  color: #18181B;
  line-height: 1.65;
  margin-bottom: 0.75rem;
  word-break: break-word;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.comment-link {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.comment-link:hover {
  color: #2563EB;
}

.comment-date {
  color: #A1A1AA;
}

/* ----- Pagination ----- */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem 0;
}

.page-btn {
  padding: 0.45rem 1.1rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: #18181B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 0.825rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(59, 130, 246, 0.3);
  color: #3B82F6;
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-btn:active:not(:disabled) {
  transform: scale(0.96);
}

.page-info {
  font-size: 0.825rem;
  color: #71717A;
  font-weight: 600;
  letter-spacing: 0.01em;
}

/* =======================================================
   Edit Profile
   ======================================================= */
.edit-profile {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Card-based form sections */
.edit-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  padding: 1.75rem 2rem;
  transition: border-color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.edit-card-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
}

.edit-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #18181B;
  letter-spacing: -0.015em;
  margin: 0;
}

.edit-card-desc {
  font-size: 0.8rem;
  color: #A1A1AA;
  margin: 0;
  white-space: nowrap;
}

.edit-card-body {
  min-width: 0;
}

.edit-card-danger {
  border-color: rgba(225, 29, 72, 0.2);
}

.edit-card-danger .edit-card-header {
  border-bottom-color: rgba(225, 29, 72, 0.15);
}

.edit-card-danger .edit-card-title {
  color: #E11D48;
}

.edit-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.edit-avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.edit-avatar-wrapper:hover {
  transform: scale(1.05);
}

.edit-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-avatar.loading { opacity: 0.5; }

.edit-avatar-overlay,
.edit-avatar-loading {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #F9FAFB;
  font-size: 0.85rem;
  font-weight: 600;
}

.edit-avatar-wrapper:hover .edit-avatar-overlay { opacity: 1; }
.edit-avatar-loading { opacity: 1; background: rgba(0, 0, 0, 0.7); }

.edit-avatar-hint {
  font-size: 0.75rem;
  color: #94A3B8;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.edit-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.edit-form-group label {
  font-weight: 600;
  font-size: 0.875rem;
  color: #18181B;
}

.edit-form-group input,
.edit-form-group textarea {
  padding: 0.65rem 0.9rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
  font-family: inherit;
}

.edit-form-group input:focus,
.edit-form-group textarea:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.edit-form-group textarea { resize: vertical; min-height: 80px; }

.edit-form-group input::placeholder,
.edit-form-group textarea::placeholder {
  color: #A1A1AA;
}

.edit-msg {
  text-align: center;
  padding: 0.65rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.success-msg {
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.edit-submit-btn {
  padding: 0.65rem 1.25rem;
  background: #3B82F6;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.edit-submit-btn:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.edit-submit-btn:disabled {
  background: rgba(161, 161, 170, 0.6);
  cursor: not-allowed;
}

.edit-form-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.edit-form-footer .edit-msg {
  flex: 1;
  min-width: 180px;
  margin: 0;
}

.edit-delete-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.edit-delete-section p {
  flex: 1;
  min-width: 220px;
  font-size: 0.85rem;
  color: #71717A;
  margin: 0;
  line-height: 1.5;
}

.edit-delete-btn {
  padding: 0.65rem 1.25rem;
  background: #E11D48;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.edit-delete-btn:hover:not(:disabled) {
  background: #BE123C;
  transform: translateY(-2px);
}

.edit-delete-btn:disabled {
  background: rgba(161, 161, 170, 0.6);
  cursor: not-allowed;
}

/* =======================================================
   Responsive: stack columns on smaller screens
   ======================================================= */
@media (max-width: 820px) {
  .user-home-page {
    padding: 1.25rem;
  }

  .user-layout {
    flex-direction: column;
    gap: 1.25rem;
  }

  .user-sidebar {
    position: static;
    width: 100%;
    padding: 1.5rem 1.25rem 1.25rem;
  }

  .sidebar-avatar-wrapper {
    width: 80px;
    height: 80px;
  }

  .sidebar-menu {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.25rem;
  }

  .menu-item {
    width: auto;
    padding: 0.5rem 0.9rem;
  }

  .menu-indicator {
    display: none;
  }

  .user-info-card {
    padding: 1.25rem 1.25rem;
  }

  .info-username {
    font-size: 1.25rem;
  }

  .edit-card {
    padding: 1.25rem;
  }

  .edit-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    margin-bottom: 1.25rem;
  }

  .edit-delete-section {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
}
</style>
