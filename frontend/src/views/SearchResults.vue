<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/api/request'

interface SearchResult {
  id: number
  title: string
  author_id: number
  category: string
  views: number
  likes: number
  created_at: string
}

const route = useRoute()
const router = useRouter()
const searchResults = ref<SearchResult[]>([])
const loading = ref(false)
const error = ref('')
const searchWord = ref('')

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

onMounted(async () => {
  const word = route.params.word as string
  searchWord.value = word
  currentPage.value = 1 // 重置页码
  await fetchSearchResults(word, currentPage.value, pageSize.value)
})

// 监听路由参数变化，当搜索关键词改变时重新搜索
watch(() => route.params.word, async (newWord) => {
  if (newWord) {
    const word = newWord as string
    searchWord.value = word
    currentPage.value = 1 // 重置页码
    await fetchSearchResults(word, currentPage.value, pageSize.value)
  }
}, { immediate: false })

const fetchSearchResults = async (word: string, page: number = 1, size: number = 10) => {
  loading.value = true
  error.value = ''
  try {
    console.log('开始搜索:', word, 'page:', page, 'size:', size)
    console.log('请求URL:', `/search/${encodeURIComponent(word)}?page=${page}&size=${size}`)
    const response = await request.get(`/search/${encodeURIComponent(word)}`, {
      params: {
        page,
        size
      }
    })
    console.log('搜索成功:', response.data)
    searchResults.value = response.data.result
    // 假设API返回total字段
    if ('total' in response.data) {
      total.value = response.data.total
    }
  } catch (err) {
    error.value = '搜索失败，请稍后重试'
    console.error('搜索失败:', err)
    if (err instanceof Error) {
      console.error('错误详情:', err.message)
    }
    // 安全地处理错误响应
    if (typeof err === 'object' && err !== null && 'response' in err) {
      console.error('错误响应:', err.response)
    }
  } finally {
    loading.value = false
    console.log('搜索结束')
  }
}

const goToArticle = (id: number) => {
  router.push(`/article/${id}`)
}

const changePage = async (page: number) => {
  if (page < 1) return
  currentPage.value = page
  const word = searchWord.value
  await fetchSearchResults(word, currentPage.value, pageSize.value)
}
</script>

<template>
  <div class="search-results">
    <h2 class="search-title">搜索结果: {{ searchWord }}</h2>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在搜索...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="searchResults.length === 0" class="no-results">
      <p>未找到相关文章</p>
    </div>

    <div v-else class="results-list">
      <div
        v-for="article in searchResults"
        :key="article.id"
        class="article-card"
        @click="goToArticle(article.id)"
      >
        <h3 class="article-title">{{ article.title }}</h3>
        <div class="article-meta">
          <span class="article-author">{{ article.author_id }}</span>
          <span class="article-category">{{ article.category }}</span>
          <span class="article-date">{{ new Date(article.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="article-stats">
          <span class="article-views">{{ article.views }} views</span>
          <span class="article-likes">{{ article.likes }} likes</span>
        </div>
      </div>

      <!-- 分页控件 -->
      <div class="pagination" v-if="total > pageSize">
        <button
          @click="changePage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          上一页
        </button>
        <span class="pagination-info">
          第 {{ currentPage }} 页，共 {{ Math.ceil(total / pageSize) }} 页
        </span>
        <button
          @click="changePage(currentPage + 1)"
          :disabled="currentPage >= Math.ceil(total / pageSize)"
          class="pagination-button"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-results {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.search-title {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #18181B;
  text-align: center;
  letter-spacing: -0.025em;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: #71717A;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.15);
  border-radius: 50%;
  border-top: 4px solid #3B82F6;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background: rgba(225, 29, 72, 0.08);
  border: 1px solid rgba(225, 29, 72, 0.2);
  border-radius: 0.375rem;
  padding: 1.5rem;
  text-align: center;
  color: #E11D48;
  margin: 2rem 0;
}

.no-results {
  text-align: center;
  padding: 4rem 0;
  color: #71717A;
  font-size: 1.1rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.article-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
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
  background: rgba(255, 255, 255, 0.85);
}

.article-card:active {
  transform: scale(0.98);
}

.article-title {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #18181B;
  line-height: 1.65;
  letter-spacing: -0.025em;
}

.article-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #71717A;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.article-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #94A3B8;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* 暗黑模式样式 */
:deep(.app.dark-mode) .search-title {
  color: #F9FAFB;
}

:deep(.app.dark-mode) .loading {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .loading-spinner {
  border-color: rgba(59, 130, 246, 0.15);
  border-top-color: #3B82F6;
}

:deep(.app.dark-mode) .error {
  background: rgba(225, 29, 72, 0.12);
  border-color: rgba(225, 29, 72, 0.25);
  color: #F87171;
}

:deep(.app.dark-mode) .no-results {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .article-card {
  background: rgba(24, 24, 27, 0.7);
  border: 1px solid rgba(63, 63, 70, 0.5);
}

:deep(.app.dark-mode) .article-card:hover {
  background: rgba(24, 24, 27, 0.85);
}

:deep(.app.dark-mode) .article-title {
  color: #F9FAFB;
}

:deep(.app.dark-mode) .article-meta {
  color: #A1A1AA;
}

:deep(.app.dark-mode) .article-stats {
  color: #71717A;
}

/* 响应式调整 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.pagination-button {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #18181B;
  font-size: 0.9rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(59, 130, 246, 0.5);
  color: #3B82F6;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.pagination-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.pagination-info {
  font-size: 0.9rem;
  color: #71717A;
  font-weight: 600;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* 暗黑模式样式 */
:deep(.app.dark-mode) .pagination {
  border-top: 1px solid rgba(63, 63, 70, 0.5);
}

:deep(.app.dark-mode) .pagination-button {
  background: rgba(24, 24, 27, 0.7);
  border-color: rgba(63, 63, 70, 0.5);
  color: #F9FAFB;
}

:deep(.app.dark-mode) .pagination-button:hover:not(:disabled) {
  background: rgba(24, 24, 27, 0.85);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60A5FA;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

:deep(.app.dark-mode) .pagination-info {
  color: #A1A1AA;
}

@media (max-width: 768px) {
  .search-results {
    padding: 0 1rem;
  }

  .search-title {
    font-size: 1.2rem;
  }

  .article-card {
    padding: 1rem;
  }

  .article-title {
    font-size: 1.1rem;
  }

  .article-meta {
    flex-wrap: wrap;
    font-size: 0.8rem;
  }

  .pagination {
    gap: 0.5rem;
  }

  .pagination-button {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }

  .pagination-info {
    font-size: 0.8rem;
  }
}
</style>