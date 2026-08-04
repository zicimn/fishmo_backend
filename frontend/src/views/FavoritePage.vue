<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'

interface Article {
  id: number
  title: string
  category: string
  created_at: string
  views: number
  likes: number
}

const router = useRouter()
const favorites = ref<Article[]>([])
const loading = ref(false)
const error = ref('')
const deletingId = ref<number | null>(null)

onMounted(async () => {
  await loadFavorites()
})

const loadFavorites = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await request.get('/user/favorite/get_list', {
      params: { page: 1, size: 10 }
    })
    const data = response.data
    favorites.value = data?.favorites || []
  } catch {
    error.value = '获取收藏失败'
  } finally {
    loading.value = false
  }
}

const goToArticle = (articleId: number) => {
  router.push(`/article/${articleId}`)
}

const removeFavorite = async (articleId: number, e: Event) => {
  e.stopPropagation()
  deletingId.value = articleId
  try {
    await request.delete(`/article/favorite/remove/${articleId}`)
    favorites.value = favorites.value.filter(item => item.id !== articleId)
  } catch {
    alert('删除失败')
  } finally {
    deletingId.value = null
  }
}
</script>

<template>
  <div class="favorite-page">
    <h2>我的收藏</h2>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="favorites.length === 0" class="empty">暂无收藏</div>

    <div v-else class="articles-list">
      <div
        v-for="article in favorites"
        :key="article.id"
        class="article-card"
        @click="goToArticle(article.id)"
      >
        <div class="article-content">
          <div class="article-title">{{ article.title }}</div>
          <div class="article-meta">
            <span class="article-id">{{ article.id }}</span>
            <span class="date">{{ new Date(article.created_at).toLocaleDateString() }}</span>
          </div>
          <div class="article-stats">
            <span>{{ article.views }} views</span>
            <span>{{ article.likes }} likes</span>
          </div>
        </div>
        <button
          class="delete-button"
          @click="removeFavorite(article.id, $event)"
          :disabled="deletingId === article.id"
        >
          {{ deletingId === article.id ? '删除中...' : '删除' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorite-page {
  max-width: 960px;
  margin: 0 auto;
}

h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #18181B;
  text-align: center;
  letter-spacing: -0.025em;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.loading, .error, .empty {
  text-align: center;
  padding: 2rem;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.article-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

.article-card:active {
  transform: scale(0.98);
}

.article-content {
  flex: 1;
  min-width: 0;
}

.article-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #18181B;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: -0.025em;
}

.article-card:hover .article-title {
  color: #3B82F6;
}

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #71717A;
  margin-bottom: 0.5rem;
}

.article-id {
  font-weight: 500;
}

.date {
  color: #94A3B8;
}

.article-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: #94A3B8;
}

.delete-button {
  margin-left: 1.5rem;
  padding: 0.75rem 1.25rem;
  background: #E11D48;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.delete-button:hover:not(:disabled) {
  background: #BE123C;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px -4px rgba(225, 29, 72, 0.35);
}

.delete-button:active:not(:disabled) {
  transform: scale(0.98);
}

.delete-button:disabled {
  background: rgba(148, 163, 184, 0.5);
  color: rgba(249, 250, 251, 0.6);
  cursor: not-allowed;
}

:deep(.app.dark-mode) h2 {
  color: #F4F4F5;
}

:deep(.app.dark-mode) .article-card {
  background: rgba(39, 39, 42, 0.6);
  border: 1px solid rgba(161, 161, 170, 0.15);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15);
}

:deep(.app.dark-mode) .article-card:hover {
  background: rgba(39, 39, 42, 0.7);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.2);
}

:deep(.app.dark-mode) .article-title {
  color: #F4F4F5;
}

:deep(.app.dark-mode) .article-card:hover .article-title {
  color: #3B82F6;
}

:deep(.app.dark-mode) .article-meta {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .date {
  color: #71717A;
}

:deep(.app.dark-mode) .article-stats {
  color: #71717A;
}

:deep(.app.dark-mode) .empty {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .error {
  color: #E11D48;
}

:deep(.app.dark-mode) .loading {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .delete-button {
  background: #E11D48;
}

:deep(.app.dark-mode) .delete-button:hover:not(:disabled) {
  background: #BE123C;
  box-shadow: 0 4px 12px -4px rgba(225, 29, 72, 0.4);
}

:deep(.app.dark-mode) .delete-button:disabled {
  background: rgba(113, 113, 122, 0.4);
  color: rgba(244, 244, 245, 0.4);
}
</style>
