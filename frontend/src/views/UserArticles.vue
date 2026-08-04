<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { articleApi, type UserArticleItem } from '@/api/article'
import { useRouter } from 'vue-router'

const router = useRouter()

// 用户帖子列表
const userArticles = ref<UserArticleItem[]>([])
const articlesLoading = ref(false)
const articlesError = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

const fetchUserArticles = async () => {
  articlesLoading.value = true
  articlesError.value = ''
  try {
    const response = await articleApi.getUserArticles(currentPage.value, pageSize.value)
    userArticles.value = response.data.articles
  } catch (err: unknown) {
    articlesError.value = '加载不出来'
    console.error(err)
  } finally {
    articlesLoading.value = false
  }
}

const handleEditArticle = (articleId: number) => {
  router.push(`/edit/${articleId}`)
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUserArticles()
}

const handleDeleteArticle = async (articleId: number) => {
  if (!confirm('Are you sure you want to delete this article? This cannot be undone.')) {
    return
  }

  articlesLoading.value = true
  try {
    await articleApi.deleteArticle(articleId)
    // 删除成功后刷新页面
    await fetchUserArticles()
  } catch (err: unknown) {
    articlesError.value = '加载不出来'
    console.error(err)
  } finally {
    articlesLoading.value = false
  }
}

onMounted(() => {
  fetchUserArticles()
})
</script>

<template>
  <div class="user-articles-page">
    <div class="glass-card">
      <h1>Your Articles</h1>

      <div class="page-info">
        <span>Current Page: {{ currentPage }}</span>
      </div>

      <div v-if="articlesLoading" class="loading">加载文章中...</div>
      <div v-else-if="articlesError" class="error">{{ articlesError }}</div>
      <div v-else-if="userArticles.length === 0" class="no-articles">无文章</div>
      <div v-else class="articles-list">
        <div v-for="article in userArticles" :key="article.id" class="article-card">
          <div class="article-info">
            <h3>{{ article.title }}</h3>
            <p class="article-meta">
                <span>Category: {{ article.category || 'Unknown' }}</span>
                <span>Created: {{ article.created_at ? new Date(article.created_at).toLocaleDateString() : 'Unknown' }}</span>
              </p>
          </div>
          <div class="article-actions">
            <router-link :to="`/article/${article.id}`" class="view-button" v-if="article.id">View</router-link>
            <button class="edit-button" @click="handleEditArticle(article.id!)" v-if="article.id">Edit</button>
            <button class="delete-button" @click="handleDeleteArticle(article.id!)" v-if="article.id">Delete</button>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button
          @click="handlePageChange(currentPage - 1)"
          :disabled="currentPage === 1"
        >
          Previous
        </button>
        <span>{{ currentPage }}</span>
        <button
          @click="handlePageChange(currentPage + 1)"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-articles-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  padding: 2rem 0;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.65;
}

.glass-card {
  width: 100%;
  max-width: 960px;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur-xl;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

h1 {
  margin-bottom: 2rem;
  text-align: center;
  color: #18181B;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.loading, .no-articles {
  text-align: center;
  padding: 2rem;
  color: #71717A;
}

.error {
  color: #E11D48;
  text-align: center;
  padding: 0.5rem;
  background: rgba(225, 29, 72, 0.1);
  backdrop-filter: blur-xl;
  border-radius: 0.375rem;
  border: 1px solid rgba(225, 29, 72, 0.3);
  margin-bottom: 1rem;
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
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur-xl;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-card:hover {
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.article-info {
  flex: 1;
}

.article-info h3 {
  margin-bottom: 0.5rem;
  color: #18181B;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.article-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #71717A;
  margin: 0;
}

.article-actions {
  display: flex;
  gap: 0.75rem;
}

.view-button, .edit-button {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.view-button {
  background: rgba(255, 255, 255, 0.9);
  color: #18181B;
  backdrop-filter: blur-xl;
}

.edit-button {
  background: #3B82F6;
  color: #F9FAFB;
  backdrop-filter: blur-xl;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.view-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
}

.edit-button:hover {
  background: #2563EB;
  transform: translateY(-2px);
}

.delete-button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: #E11D48;
  color: #F9FAFB;
  backdrop-filter: blur-xl;
  border: 1px solid rgba(225, 29, 72, 0.3);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.delete-button:hover {
  background: rgba(225, 29, 72, 0.85);
  transform: translateY(-2px);
}

.page-info {
  margin-bottom: 1rem;
  text-align: right;
  font-size: 0.9rem;
  color: #71717A;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur-xl;
  color: #18181B;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-weight: 700;
  color: #18181B;
}
</style>
