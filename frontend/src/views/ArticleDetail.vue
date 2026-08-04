<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { articleApi, type ArticleDetailResponse, type LinkRequest, type LinkResponse, type CommentRequest, type CommentResponse } from '@/api/article'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

// Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// Heading counter for TOC ID injection
let headingCounter = 0

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const articleId = ref(Number(route.params.id))
const article = ref<ArticleDetailResponse>({
  title: '',
  content: '',
  images: [],
  author_id: 0,
  author_name: '',
  author_avatar: '',
  views: 0
})
const loading = ref(true)
const error = ref('')
const avatarError = ref(false)

function onAvatarError() {
  avatarError.value = true
}

watch(article, () => { avatarError.value = false }, { deep: true })

// 渲染后的 Markdown 内容
const renderedContent = computed(() => {
  if (!article.value.content) return ''
  headingCounter = 0
  let html = md.render(article.value.content)
  // Inject IDs into headings for TOC smooth-scrolling
  html = html.replace(/<h([1-3])([^>]*)>/gi, (match, level, attrs) => {
    const id = `heading-${headingCounter++}`
    const clean = attrs.replace(/\s+id="[^"]*"/gi, '').trim()
    return clean ? `<h${level} ${clean} id="${id}">` : `<h${level} id="${id}">`
  })
  return DOMPurify.sanitize(html)
})

// 链接相关
const links = ref<LinkResponse[]>([])
const linksLoading = ref(false)
const linksError = ref('')
const showLinks = ref(false)
const showAddLinkForm = ref(false)
const newLink = ref<LinkRequest>({
  url: '',
  title: ''
})
const addLinkLoading = ref(false)
const addLinkError = ref('')
const addLinkSuccess = ref('')

// 收藏相关
const isFavorite = ref(false)
const favoriteLoading = ref(false)

// 评论相关
const comments = ref<CommentResponse[]>([])
const commentsLoading = ref(false)
const commentsError = ref('')
const showComments = ref(true)
const newComment = ref<CommentRequest>({
  content: ''
})
const addCommentLoading = ref(false)
const addCommentError = ref('')
const addCommentSuccess = ref('')

// 删除评论相关
const deleteCommentLoading = ref<number | null>(null)
const deleteCommentError = ref('')
const deleteCommentSuccess = ref('')

const fetchArticle = async () => {
  loading.value = true
  error.value = ''
  try {
    console.log('Fetching article with id:', articleId.value)
    const response = await articleApi.visit(articleId.value)
    console.log('Article response:', response.data)
    console.log('Article images:', response.data.images)
    console.log('Article images type:', typeof response.data.images)
    console.log('Article images is array:', Array.isArray(response.data.images))
    console.log('Author avatar value:', response.data.author_avatar, 'type:', typeof response.data.author_avatar)
    article.value = response.data
  } catch (err: unknown) {
    console.error('Error loading article:', err)
    if (err instanceof Error) {
      error.value = `加载文章失败: ${err.message}`
    } else {
      error.value = '加载文章失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}

const fetchLinks = async () => {
  if (!showLinks.value) return

  linksLoading.value = true
  linksError.value = ''
  try {
    const response = await articleApi.getLinks(articleId.value)
    links.value = response.data.links
  } catch (err) {
    linksError.value = '加载不出来'
    console.error(err)
  } finally {
    linksLoading.value = false
  }
}

const fetchComments = async () => {
  if (!showComments.value) return

  commentsLoading.value = true
  commentsError.value = ''
  try {
    const response = await articleApi.getComments(articleId.value)
    comments.value = response.data.comments || []
  } catch (err) {
    commentsError.value = '加载不出来'
    console.error(err)
  } finally {
    commentsLoading.value = false
  }
}

const handleAddLink = async () => {
  if (!newLink.value.url) {
    addLinkError.value = '请输入链接地址'
    return
  }

  addLinkLoading.value = true
  addLinkError.value = ''
  addLinkSuccess.value = ''
  try {
    await articleApi.submitLink(articleId.value, newLink.value)
    addLinkSuccess.value = 'Link added successfully'
    newLink.value = {
      url: '',
      title: ''
    }
    // 重新获取链接列表
    await fetchLinks()
  } catch (err) {
    addLinkError.value = '加载不出来'
    console.error(err)
  } finally {
    addLinkLoading.value = false
  }
}

const handleAddComment = async () => {
  if (!newComment.value.content) {
    addCommentError.value = '请输入评论内容'
    return
  }

  addCommentLoading.value = true
  addCommentError.value = ''
  addCommentSuccess.value = ''
  try {
    await articleApi.submitComment(articleId.value, newComment.value)
    addCommentSuccess.value = '评论发布成功'
    newComment.value = {
      content: ''
    }
    // 重新获取评论列表
    await fetchComments()
  } catch (err) {
    addCommentError.value = '发布评论失败'
    console.error(err)
  } finally {
    addCommentLoading.value = false
  }
}

const handleDeleteComment = async (commentId: number) => {
  if (!confirm('确定要删除这条评论吗？')) return

  deleteCommentLoading.value = commentId
  deleteCommentError.value = ''
  deleteCommentSuccess.value = ''
  try {
    const response = await articleApi.deleteComment(commentId)
    deleteCommentSuccess.value = response.data?.msg || '评论删除成功'
    // 重新获取评论列表
    await fetchComments()
  } catch (err) {
    deleteCommentError.value = '删除评论失败'
    console.error(err)
  } finally {
    deleteCommentLoading.value = null
  }
}

const handleEdit = () => {
  router.push(`/edit/${articleId.value}`)
}

const toggleLinks = () => {
  showLinks.value = !showLinks.value
  if (showLinks.value) {
    fetchLinks()
  }
}

const handleFavorite = async () => {
  if (!userStore.isLoggedIn) {
    alert('请先登录')
    return
  }

  favoriteLoading.value = true

  try {
    if (isFavorite.value) {
      await articleApi.removeFavorite(articleId.value)
      isFavorite.value = false
    } else {
      await articleApi.addFavorite(articleId.value)
      isFavorite.value = true
    }
  } catch (err) {
    console.error('收藏操作失败:', err)
    alert('收藏操作失败')
  } finally {
    favoriteLoading.value = false
  }
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return '未知时间'
    }
    return date.toLocaleString()
  } catch {
    return '未知时间'
  }
}

// --- TOC & Sidebar interactions ---
interface TocItem {
  id: string
  text: string
  level: number
}
const tocItems = computed(() => {
  if (!article.value.content) return []
  const items: TocItem[] = []
  const regex = /^(#{1,3})\s+(.+)$/gm
  let match: RegExpExecArray | null
  while ((match = regex.exec(article.value.content)) !== null) {
    const headingText = match[2]
    const headingLevel = match[1]
    if (headingText !== undefined && headingLevel !== undefined) {
      items.push({
        id: 'heading-' + items.length,
        text: headingText.trim(),
        level: headingLevel.length
      })
    }
  }
  return items
})

function scrollToHeading(index: number) {
  document.getElementById(`heading-${index}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function scrollToComments() {
  document.getElementById('comments-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(() => {
  fetchArticle()
  fetchComments()
})
</script>

<template>
  <div class="article-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="article-layout">
      <!-- Article Sidebar: Author, TOC, Comment Previews -->
      <aside class="article-sidebar">
        <!-- Author Card -->
        <div class="sidebar-section">
          <router-link :to="`/user/${article.author_id}`" class="sidebar-author-card">
            <div class="sidebar-avatar-wrapper">
              <img
                v-if="article.author_avatar && !avatarError"
                :src="article.author_avatar"
                :alt="article.author_name"
                class="sidebar-avatar"
                @error="onAvatarError"
              />
              <div v-else class="sidebar-avatar-placeholder" aria-hidden="true">
                {{ article.author_name?.charAt(0) || '?' }}
              </div>
            </div>
            <span class="sidebar-author-name">{{ article.author_name }}</span>
          </router-link>
        </div>

        <div class="sidebar-divider" v-if="tocItems.length > 0"></div>

        <!-- Table of Contents -->
        <div class="sidebar-section" v-if="tocItems.length > 0">
          <h4 class="sidebar-section-title">目录</h4>
          <nav class="toc-list">
            <button
              v-for="(item, index) in tocItems"
              :key="item.id"
              class="toc-item"
              :class="'toc-level-' + item.level"
              @click="scrollToHeading(index)"
            >
              {{ item.text }}
            </button>
          </nav>
        </div>

        <div class="sidebar-divider" v-if="tocItems.length > 0 && comments.length > 0"></div>

        <!-- Comment Previews -->
        <div class="sidebar-section">
          <h4 class="sidebar-section-title">评论列表</h4>
          <div v-if="comments.length === 0" class="sidebar-empty-state">
            <span>暂无评论</span>
          </div>
          <div v-else class="comment-previews-list">
            <button
              v-for="comment in comments.slice(0, 5)"
              :key="comment.id"
              class="comment-preview-item"
              @click="scrollToComments"
            >
              <span class="comment-preview-text">{{ comment.content.substring(0, 10) }}{{ comment.content.length > 10 ? '...' : '' }}</span>
              <span class="comment-preview-author">{{ comment.name }}</span>
            </button>
            <button class="comment-preview-all" @click="scrollToComments">
              查看全部 {{ comments.length }} 条评论 →
            </button>
          </div>
        </div>
      </aside>

      <!-- Main content area -->
      <main class="article-main">
        <div class="article-body">
          <div class="article-header">
            <h1>{{ article.title }}</h1>
            <div class="header-actions">
              <span v-if="article.views" class="views">浏览量: {{ article.views }}</span>
              <button
                v-if="userStore.isLoggedIn && article.author_id === userStore.id"
                class="edit-button"
                @click="handleEdit"
              >
                编辑文章
              </button>
            </div>
          </div>
          <div class="content markdown-content" v-html="renderedContent">
          </div>
          <div v-if="article.images.length > 0" class="article-images">
            <img
              v-for="(image, index) in article.images"
              :key="index"
              :src="image + '?t=' + new Date().getTime()"
              alt="Article image"
              class="article-image"
            />
          </div>
        </div>

        <!-- 链接部分 -->
        <div class="links-section">
          <div class="links-header">
            <button class="toggle-links-button" @click="toggleLinks">
              <span class="btn-icon">{{ showLinks ? '⊟' : '⊞' }}</span>
              {{ showLinks ? '隐藏链接' : '显示链接' }}
            </button>

            <!-- 添加链接按钮 -->
            <div class="add-link-section">
              <button class="add-link-button" @click="showAddLinkForm = !showAddLinkForm">
                <span class="btn-icon">{{ showAddLinkForm ? '✕' : '+' }}</span>
                {{ showAddLinkForm ? '取消' : '添加链接' }}
              </button>

              <!-- 添加收藏按钮 -->
              <button
                class="favorite-button"
                :class="{ 'favorited': isFavorite }"
                @click="handleFavorite"
                :disabled="favoriteLoading"
              >
                <span class="btn-icon">{{ isFavorite ? '★' : '☆' }}</span>
                {{ isFavorite ? '已收藏' : '添加收藏' }}
              </button>

              <div v-if="showAddLinkForm" class="add-link-form">
                <div v-if="addLinkError" class="add-link-error">{{ addLinkError }}</div>
                <div v-if="addLinkSuccess" class="add-link-success">{{ addLinkSuccess }}</div>
                <div class="form-group">
                  <label for="link-url">链接地址</label>
                  <input
                    type="url"
                    id="link-url"
                    v-model="newLink.url"
                    placeholder="输入链接地址"
                    :disabled="addLinkLoading"
                  />
                </div>
                <div class="form-group">
                  <label for="link-title">标题（可选）</label>
                  <input
                    type="text"
                    id="link-title"
                    v-model="newLink.title"
                    placeholder="输入链接标题"
                    :disabled="addLinkLoading"
                  />
                </div>
                <button
                  class="submit-link-button"
                  @click="handleAddLink"
                  :disabled="addLinkLoading"
                >
                  {{ addLinkLoading ? '添加中...' : '添加链接' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="showLinks" class="links-container">
            <div v-if="linksLoading" class="links-loading">加载链接中...</div>
            <div v-else-if="linksError" class="links-error">{{ linksError }}</div>
            <div v-else>
              <!-- 链接列表 -->
              <div v-if="links.length === 0" class="no-links">暂无链接。</div>
              <div v-else class="links-list">
                <div v-for="link in links" :key="link.id" class="link-item">
                  <div class="link-info">
                    <a :href="link.url" target="_blank" rel="noopener noreferrer" class="link-url">
                      {{ link.title || link.url }}
                    </a>
                    <span class="link-url-full">{{ link.url }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 评论部分 -->
        <div id="comments-section" class="comments-section">
          <!-- 评论输入框 -->
          <div class="add-comment-section">
            <div class="form-group">
              <textarea
                v-model="newComment.content"
                placeholder="请输入您的评论"
                rows="3"
                :disabled="addCommentLoading"
              ></textarea>
              <button
                class="submit-comment-button"
                @click="handleAddComment"
                :disabled="addCommentLoading"
              >
                {{ addCommentLoading ? '发布中...' : '发表' }}
              </button>
            </div>
            <div v-if="addCommentError" class="add-comment-error">{{ addCommentError }}</div>
            <div v-if="addCommentSuccess" class="add-comment-success">{{ addCommentSuccess }}</div>
            <div v-if="!userStore.isLoggedIn" class="login-prompt">
              请 <router-link to="/login">登录</router-link> 后发表评论
            </div>
          </div>

          <div class="comments-header">
            <h3>评论</h3>
          </div>

          <div v-if="showComments" class="comments-container">
            <div v-if="commentsLoading" class="comments-loading">加载评论中...</div>
            <div v-else-if="commentsError" class="comments-error">{{ commentsError }}</div>
            <div v-else>
              <!-- 评论列表 -->
              <div v-if="comments.length === 0" class="no-comments">暂无评论，快来发表第一条评论吧！</div>
              <div v-else class="comments-list">
                <div v-for="comment in comments" :key="comment.id" class="comment-item">
                  <div class="comment-header">
                    <span class="comment-author">{{ comment.name }}</span>
                    <div class="comment-actions">
                      <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                      <button
                        v-if="userStore.isLoggedIn && comment.name === userStore.username"
                        class="delete-comment-button"
                        @click="handleDeleteComment(comment.id)"
                        :disabled="deleteCommentLoading === comment.id"
                      >
                        {{ deleteCommentLoading === comment.id ? '删除中...' : '删除' }}
                      </button>
                    </div>
                  </div>
                  <div class="comment-content">
                    {{ comment.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.article-detail {
  min-height: 80vh;
  padding: 2rem 0;
  max-width: 1260px;
  margin: 0 auto;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(100, 149, 237, 0.6) rgba(255, 255, 255, 0.3);
}

.article-detail::-webkit-scrollbar {
  width: 8px;
}

.article-detail::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.article-detail::-webkit-scrollbar-thumb {
  background: rgba(100, 149, 237, 0.6);
  border-radius: 4px;
}

.article-detail::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 149, 237, 0.8);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #71717A;
}

.error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem 1.5rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(225, 29, 72, 0.15);
}

/* ===== Layout ===== */
.article-layout {
  display: flex;
  gap: 48px;
  align-items: flex-start;
  width: 100%;
}

/* ===== Article Sidebar ===== */
.article-sidebar {
  position: sticky;
  top: 6rem;
  flex-shrink: 0;
  width: 220px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.4);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  padding: 1.25rem 0;
  max-height: calc(100vh - 6rem);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(24, 24, 27, 0.1) transparent;
}

.sidebar-section {
  padding: 0 1.25rem;
}

.sidebar-author-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sidebar-author-card:hover {
  opacity: 0.75;
}

.sidebar-avatar-wrapper {
  width: 88px;
  height: 88px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1.5px solid rgba(24, 24, 27, 0.06);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sidebar-author-card:hover .sidebar-avatar-wrapper {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.sidebar-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.sidebar-avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%);
  color: #fff;
  font-size: 1.35rem;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  user-select: none;
}

.sidebar-author-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #18181B;
  letter-spacing: 0.02em;
  line-height: 1.3;
  text-align: center;
  word-break: break-word;
}

/* Sidebar horizontal divider */
.article-sidebar .sidebar-divider {
  width: 100%;
  height: 1px;
  margin: 1rem 0;
  background: linear-gradient(
    to right,
    transparent,
    rgba(24, 24, 27, 0.06) 15%,
    rgba(24, 24, 27, 0.06) 85%,
    transparent
  );
  flex-shrink: 0;
}

/* Section title */
.sidebar-section-title {
  margin: 0 0 0.75rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #71717A;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ===== TOC ===== */
.toc-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  position: relative;
}

.toc-item {
  display: block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-radius: 6px;
  padding: 7px 12px 7px 12px;
  font-size: 0.8rem;
  font-weight: 450;
  color: #52525B;
  line-height: 1.4;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.toc-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 2px;
  height: 50%;
  background: #3B82F6;
  border-radius: 0 2px 2px 0;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toc-item:hover {
  background: rgba(59, 130, 246, 0.06);
  color: #3B82F6;
  padding-left: 16px;
}

.toc-item:hover::before {
  transform: translateY(-50%) scaleY(1);
}

.toc-item:active {
  transform: scale(0.98);
}

.toc-item.active {
  background: rgba(59, 130, 246, 0.08);
  color: #3B82F6;
  font-weight: 500;
  padding-left: 16px;
}

.toc-item.active::before {
  transform: translateY(-50%) scaleY(1);
}

.toc-level-1 {
  padding-left: 12px;
  font-weight: 550;
  color: #18181B;
}

.toc-level-1:hover,
.toc-level-1.active {
  padding-left: 16px;
}

.toc-level-2 {
  padding-left: 28px;
}

.toc-level-2:hover,
.toc-level-2.active {
  padding-left: 32px;
}

.toc-level-3 {
  padding-left: 44px;
  font-size: 0.75rem;
}

.toc-level-3:hover,
.toc-level-3.active {
  padding-left: 48px;
}

/* ===== Comment Previews ===== */
.comment-previews-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comment-preview-item {
  display: flex;
  flex-direction: column;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.comment-preview-item:hover {
  background: rgba(59, 130, 246, 0.06);
}

.comment-preview-item:active {
  transform: scale(0.98);
}

.comment-preview-text {
  font-size: 0.78rem;
  color: #52525B;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.comment-preview-author {
  font-size: 0.65rem;
  color: #A1A1AA;
  margin-top: 1px;
}

.comment-preview-all {
  display: inline-block;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  border-radius: 6px;
  padding: 8px 10px;
  margin-top: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #3B82F6;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.comment-preview-all:hover {
  background: rgba(59, 130, 246, 0.06);
  color: #2563EB;
}

.sidebar-empty-state {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  font-size: 0.78rem;
  color: #A1A1AA;
  font-weight: 400;
}

/* ===== Main Content ===== */
.article-main {
  flex: 1;
  min-width: 0;
}

.article-body {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 2rem;
  margin-bottom: 2rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 1rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(24, 24, 27, 0.06);
}

h1 {
  margin: 0;
  color: #18181B;
  flex: 1;
  font-size: 1.85rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.03em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.views {
  font-size: 0.8rem;
  color: #71717A;
  font-weight: 450;
  white-space: nowrap;
  background: rgba(113, 113, 122, 0.08);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.edit-button {
  padding: 0.5rem 1.125rem;
  background: #18181B;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.edit-button:hover {
  background: #27272A;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 24, 27, 0.15);
}

.article-images {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(24, 24, 27, 0.06);
}

.article-image {
  max-width: 100%;
  max-height: 320px;
  object-fit: cover;
  border-radius: 0.75rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-image:hover {
  transform: scale(1.02);
}

.content {
  font-size: 1.05rem;
  line-height: 1.8;
  letter-spacing: 0.02em;
  color: #27272A;
  margin-bottom: 0;
  overflow-y: auto;
}

/* Markdown 内容样式 — refined typography with taste-skill design */
.markdown-content {
  font-size: 1.05rem;
  line-height: 1.8;
  letter-spacing: 0.02em;
  color: #27272A;
  overflow-y: auto;
}

.markdown-content h1 {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(24, 24, 27, 0.06);
  color: #18181B;
}

.markdown-content h2 {
  font-size: 1.5rem;
  font-weight: 650;
  letter-spacing: -0.02em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  color: #18181B;
}

.markdown-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
  color: #27272A;
}

.markdown-content p {
  margin-bottom: 1.25rem;
  line-height: 1.8;
  color: #27272A;
}

.markdown-content strong {
  font-weight: 650;
  color: #18181B;
}

.markdown-content em {
  font-style: italic;
  color: #27272A;
}

.markdown-content del {
  text-decoration: line-through;
  color: #A1A1AA;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 1.25rem;
}

.markdown-content li {
  margin-bottom: 0.5rem;
  line-height: 1.75;
}

.markdown-content code {
  padding: 0.2em 0.4em;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 4px;
  font-size: 0.85em;
  font-family: 'JetBrains Mono', 'Fira Code', monospace, 'Geist', 'Inter', sans-serif;
  color: #3B82F6;
  font-weight: 500;
}

.markdown-content pre {
  padding: 1.25rem 1.5rem;
  background: #18181B;
  border-radius: 0.75rem;
  overflow-x: auto;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(24, 24, 27, 0.1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
  font-size: 0.875rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace, 'Geist', 'Inter', sans-serif;
  color: #E4E4E7;
  font-weight: 400;
}

.markdown-content a {
  color: #3B82F6;
  text-decoration: none;
  background-image: linear-gradient(#3B82F6, #3B82F6);
  background-position: 0% 100%;
  background-repeat: no-repeat;
  background-size: 0% 1px;
  transition: background-size 0.3s cubic-bezier(0.16, 1, 0.3, 1),
              color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  text-underline-offset: 2px;
}

.markdown-content a:hover {
  background-size: 100% 1px;
  color: #2563EB;
}

.markdown-content blockquote {
  border-left: 3px solid #3B82F6;
  padding: 0.75rem 1.25rem;
  margin: 1.5rem 0;
  color: #52525B;
  font-style: italic;
  background: rgba(59, 130, 246, 0.04);
  border-radius: 0 0.5rem 0.5rem 0;
}

.markdown-content hr {
  border: none;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(24, 24, 27, 0.08),
    transparent
  );
  margin: 2.5rem 0;
}

.markdown-content img {
  max-width: 100%;
  border-radius: 0.75rem;
  margin: 2rem auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  display: block;
}

.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.markdown-content th,
.markdown-content td {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(24, 24, 27, 0.08);
  text-align: left;
}

.markdown-content th {
  background: rgba(24, 24, 27, 0.03);
  font-weight: 600;
  color: #18181B;
}

/* 链接部分样式 */
.links-section {
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 1.5rem;
}

.links-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.toggle-links-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(24, 24, 27, 0.04);
  color: #52525B;
  border: 1px solid rgba(24, 24, 27, 0.08);
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 0.01em;
  align-self: flex-start;
}

.toggle-links-button:hover {
  background: rgba(24, 24, 27, 0.06);
  border-color: rgba(24, 24, 27, 0.12);
  color: #18181B;
  transform: translateY(-1px);
}

.toggle-links-button .btn-icon {
  font-size: 0.75rem;
  opacity: 0.7;
}

.links-container {
  margin-top: 1rem;
}

.links-loading,
.no-links {
  text-align: center;
  padding: 1.5rem 1rem;
  color: #71717A;
  font-size: 0.9rem;
}

.links-error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(225, 29, 72, 0.15);
  margin-bottom: 1rem;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0;
}

.link-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(226, 232, 240, 0.4);
  border-radius: 0.75rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.link-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.08);
  border-color: rgba(226, 232, 240, 0.7);
}

.link-info {
  flex: 1;
}

.link-url {
  display: block;
  font-weight: 500;
  color: #18181B;
  text-decoration: none;
  margin-bottom: 0.35rem;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.link-url:hover {
  color: #3B82F6;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.link-url-full {
  font-size: 0.85rem;
  color: #71717A;
  word-break: break-all;
}

.add-link-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.add-link-button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.125rem;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 0.01em;
}

.add-link-button:hover {
  background: #2563EB;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.add-link-button:active {
  transform: scale(0.97);
}

.add-link-button .btn-icon {
  font-size: 0.9rem;
  font-weight: 700;
  line-height: 1;
}

.favorite-button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1.125rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.85), rgba(217, 119, 6, 0.85));
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: 0.01em;
}

.favorite-button:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(245, 158, 11, 1), rgba(217, 119, 6, 1));
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25);
}

.favorite-button:active:not(:disabled) {
  transform: scale(0.97);
}

.favorite-button.favorited {
  background: linear-gradient(135deg, rgba(225, 29, 72, 0.85), rgba(190, 18, 60, 0.85));
}

.favorite-button.favorited:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(225, 29, 72, 1), rgba(190, 18, 60, 1));
  box-shadow: 0 4px 14px rgba(225, 29, 72, 0.25);
}

.favorite-button:disabled {
  background: rgba(113, 113, 122, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.favorite-button .btn-icon {
  font-size: 0.85rem;
  line-height: 1;
}

.add-link-form {
  width: 100%;
  margin-top: 0.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(226, 232, 240, 0.4);
  border-radius: 0.75rem;
}

.form-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #18181B;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #A1A1AA;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: rgba(255, 255, 255, 0.8);
}

.form-group textarea {
  resize: none;
}

.add-link-error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(225, 29, 72, 0.15);
  margin-bottom: 1rem;
}

.add-link-success {
  color: #10B981;
  text-align: center;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.15);
  margin-bottom: 1rem;
}

.submit-link-button {
  padding: 0.625rem 1.25rem;
  background: #18181B;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  width: 100%;
  letter-spacing: 0.01em;
}

.submit-link-button:hover:not(:disabled) {
  background: #27272A;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 24, 27, 0.15);
}

.submit-link-button:disabled {
  background: rgba(113, 113, 122, 0.5);
  cursor: not-allowed;
}

/* 评论部分样式 */
.comments-section {
  margin-top: 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 1.5rem 2rem;
}

.comments-header {
  margin-bottom: 1.25rem;
}

.comments-header h3 {
  margin: 0;
  color: #18181B;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.comments-container {
  margin-top: 0;
}

.comments-loading,
.no-comments {
  text-align: center;
  padding: 1.5rem 1rem;
  color: #71717A;
  font-size: 0.9rem;
}

.comments-error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(225, 29, 72, 0.15);
  margin-bottom: 1rem;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0;
}

.comment-item {
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(226, 232, 240, 0.4);
  border-radius: 0.75rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.comment-item:hover {
  border-color: rgba(226, 232, 240, 0.7);
  box-shadow: 0 4px 16px -8px rgba(0, 0, 0, 0.06);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.comment-author {
  font-weight: 600;
  color: #18181B;
  font-size: 0.9rem;
}

.comment-date {
  font-size: 0.8rem;
  color: #71717A;
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.delete-comment-button {
  padding: 0.2rem 0.625rem;
  background: rgba(225, 29, 72, 0.08);
  color: #E11D48;
  border: 1px solid rgba(225, 29, 72, 0.15);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.delete-comment-button:hover:not(:disabled) {
  background: #E11D48;
  color: white;
  transform: translateY(-1px);
}

.delete-comment-button:disabled {
  background: rgba(113, 113, 122, 0.15);
  color: #A1A1AA;
  border-color: transparent;
  cursor: not-allowed;
}

.comment-content {
  line-height: 1.6;
  color: #18181B;
  white-space: pre-line;
  font-size: 0.9rem;
}

.add-comment-section {
  margin-bottom: 2rem;
}

.add-comment-section .form-group {
  flex-direction: row;
  gap: 1rem;
  align-items: flex-start;
}

.login-prompt {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  color: #71717A;
  border: 1px solid rgba(226, 232, 240, 0.4);
  border-radius: 0.75rem;
  font-size: 0.9rem;
  text-align: center;
}

.login-prompt a {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-prompt a:hover {
  color: #2563EB;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.add-comment-error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(225, 29, 72, 0.15);
  margin-bottom: 1rem;
}

.add-comment-success {
  color: #10B981;
  text-align: center;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.15);
  margin-bottom: 1rem;
}

.submit-comment-button {
  padding: 0.625rem 1.25rem;
  background: #18181B;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.submit-comment-button:hover:not(:disabled) {
  background: #27272A;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 24, 27, 0.15);
}

.submit-comment-button:disabled {
  background: rgba(113, 113, 122, 0.5);
  cursor: not-allowed;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .article-layout {
    flex-direction: column;
    gap: 1rem;
  }

  .article-sidebar {
    position: static;
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem 1.25rem;
    padding: 0.875rem 1.125rem;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(24px);
    border-radius: 1.25rem;
    border: 1px solid rgba(226, 232, 240, 0.5);
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
    max-height: none;
    overflow: visible;
  }

  .article-sidebar .sidebar-divider {
    display: none;
  }

  .sidebar-section {
    padding: 0;
    flex: 1;
    min-width: 0;
  }

  .sidebar-author-card {
    flex-direction: row;
    gap: 0.625rem;
    align-items: center;
  }

  .sidebar-avatar-wrapper {
    width: 40px;
    height: 40px;
    border-radius: 8px;
  }

  .sidebar-avatar-placeholder {
    font-size: 1rem;
  }

  .sidebar-author-name {
    font-size: 0.8rem;
  }

  .sidebar-section-title {
    display: none;
  }

  .toc-list {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 4px;
  }

  .toc-item {
    font-size: 0.72rem;
    padding: 3px 8px;
    border-radius: 4px;
    background: rgba(24, 24, 27, 0.04);
    white-space: nowrap;
  }

  .toc-item::before {
    display: none;
  }

  .toc-level-1,
  .toc-level-2,
  .toc-level-3 {
    padding-left: 8px;
  }

  .comment-previews-list,
  .sidebar-empty-state {
    display: none;
  }

  .article-body {
    padding: 1.25rem;
  }

  .article-header {
    flex-direction: column;
    gap: 0.75rem;
    padding-bottom: 1rem;
    margin-bottom: 1.25rem;
  }

  h1 {
    font-size: 1.35rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .comments-section {
    padding: 1.25rem;
  }

  .add-comment-section .form-group {
    flex-direction: column;
  }
}
</style>

