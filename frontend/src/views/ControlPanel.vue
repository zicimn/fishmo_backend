<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../api/article'
import type { UserArticleItem } from '../api/article'

const router = useRouter()

// 展开状态
const showArticles = ref(false)

// 文章相关
const userArticles = ref<UserArticleItem[]>([])
const articlesLoading = ref(false)
const articlesError = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 获取用户文章
const fetchUserArticles = async () => {
  if (!showArticles.value) return

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

// 切换文章展开状态
const toggleArticles = () => {
  showArticles.value = !showArticles.value
  if (showArticles.value) {
    fetchUserArticles()
  }
}

// 处理文章编辑
const handleEditArticle = (articleId: number) => {
  router.push(`/edit/${articleId}`)
}

// 处理文章查看
const handleViewArticle = (articleId: number) => {
  router.push(`/article/${articleId}`)
}

// 处理文章删除
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

// 分页处理
const handlePreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchUserArticles()
  }
}

const handleNextPage = () => {
  currentPage.value++
  fetchUserArticles()
}
</script>

<template>
  <div class="control-panel-page">
    <h1 class="page-title">我的文章</h1>

    <!-- 文章控制 -->
    <div class="control-section">
      <button class="toggle-button" @click="toggleArticles">
        {{ showArticles ? '隐藏文章' : '显示文章' }}
      </button>

      <div v-if="showArticles" class="control-content">
        <div v-if="articlesLoading" class="loading">加载中...</div>
        <div v-else-if="articlesError" class="error">{{ articlesError }}</div>
        <div v-else>
          <div v-if="userArticles.length === 0" class="no-items">暂无文章。</div>
          <div v-else class="articles-list">
            <div v-for="article in userArticles" :key="article.id" class="article-card" @click="article.id && handleViewArticle(article.id)">
              <div class="article-content">
                <div class="article-title">{{ article.title }}</div>
                <div class="article-meta">
                  <span class="article-id">{{ article.id }}</span>
                  <span class="category">{{ article.category }}</span>
                  <span class="date">{{ article.created_at ? new Date(article.created_at).toLocaleDateString() : '未知' }}</span>
                </div>
                <div class="article-stats">
                  <span>{{ article.views }} views</span>
                  <span>{{ article.likes }} likes</span>
                </div>
              </div>
              <div class="article-actions" @click.stop>
                <button class="view-button" @click="article.id && handleViewArticle(article.id)">查看</button>
                <button class="edit-button" @click="article.id && handleEditArticle(article.id)">编辑</button>
                <button class="delete-button" @click="article.id && handleDeleteArticle(article.id)">删除</button>
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination">
              <button @click="handlePreviousPage" :disabled="currentPage === 1">上一页</button>
              <span class="current-page">{{ currentPage }}</span>
              <button @click="handleNextPage">下一页</button>
            </div>
            <p class="page-info">当前页码：{{ currentPage }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
* {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.control-panel-page {
  padding: 2rem 0;
  max-width: 960px;
  margin: 0 auto;
}

.page-title {
  margin-bottom: 2rem;
  color: #18181B;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.control-section {
  margin-bottom: 2rem;
}

.toggle-button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  color: #18181B;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  width: 100%;
  text-align: left;
  margin-bottom: 1rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-2px);
}

.toggle-button:active {
  transform: scale(0.98);
}

.control-content {
  padding: 0;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #71717A;
}

.error {
  background: #E11D48;
  color: #F9FAFB;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.no-items {
  text-align: center;
  padding: 2rem;
  color: #71717A;
  font-style: italic;
}

/* 文章列表 */
.articles-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.article-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.7);
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
  letter-spacing: -0.025em;
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

.article-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
  margin-left: 1.5rem;
}

.view-button, .edit-button, .delete-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.view-button {
  background: #3B82F6;
  color: #F9FAFB;
}

.edit-button {
  background: #10B981;
  color: #F9FAFB;
}

.delete-button {
  background: #E11D48;
  color: #F9FAFB;
}

.view-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  background: #2563EB;
}

.edit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.delete-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.view-button:active,
.edit-button:active,
.delete-button:active {
  transform: scale(0.98);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
}

.pagination button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.current-page {
  padding: 0.5rem 1rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  color: #18181B;
}

.page-info {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #71717A;
  line-height: 1.65;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .glass-card {
    padding: 1.5rem;
    margin: 0 1rem;
  }

  .article-item, .link-item {
    flex-direction: column;
    gap: 1rem;
  }

  .article-actions {
    align-self: flex-start;
  }

  .delete-button {
    align-self: flex-start;
  }
}
</style>
