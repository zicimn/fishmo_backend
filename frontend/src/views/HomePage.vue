<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { articleApi } from '@/api/article'
import type { ArticleItem } from '@/api/article'

const articles = ref<ArticleItem[]>([])
const loading = ref(true)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedCategory = ref<string>('')
const selectedSort = ref<string>('created_at')
const selectedOrder = ref<string>('desc')

const categories = ['all', 'code', 'health', 'other', 'test', 'study']
const sortOptions = [
  { value: 'created_at', label: '发布时间' },
  { value: 'views', label: '浏览量' },
  { value: 'likes', label: '点赞数' }
]
const orderOptions = [
  { value: 'desc', label: '降序' },
  { value: 'asc', label: '升序' }
]

const fetchArticles = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await articleApi.list(
      currentPage.value, 
      pageSize.value, 
      selectedCategory.value || undefined,
      selectedSort.value,
      selectedOrder.value
    )
    articles.value = response.data?.items || []
    total.value = response.data?.total || 0
  } catch (err) {
    error.value = '加载不出来'
    articles.value = []
    total.value = 0
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = (category: string) => {
  selectedCategory.value = category
  currentPage.value = 1
  fetchArticles()
}

const handleSortChange = () => {
  currentPage.value = 1
  fetchArticles()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchArticles()
}

onMounted(() => {
  fetchArticles()
})
</script>

<template>
  <div class="home-page">
    <h1>Articles</h1>
    
    <div class="filter-container">
      <div class="categories">
        <button 
          v-for="category in categories" 
          :key="category"
          :class="{ active: (category === 'all' && selectedCategory === '') || selectedCategory === category }"
          @click="handleCategoryChange(category === 'all' ? '' : category)"
        >
          {{ category }}
        </button>
      </div>
      
      <div class="sort-container">
        <select v-model="selectedSort" @change="handleSortChange" class="sort-select">
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <select v-model="selectedOrder" @change="handleSortChange" class="sort-select">
          <option v-for="option in orderOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="article-list">
        <div v-for="article in (articles || [])" :key="article.id" class="article-card">
          <div class="article-author-row">
            <img
              v-if="article.avatar"
              :src="article.avatar"
              :alt="article.author_name"
              class="article-avatar"
            />
            <span class="article-author-name">{{ article.author_name }}</span>
          </div>
          <router-link :to="`/article/${article.id}`" class="article-title">
            {{ article.title }}
          </router-link>
          <div class="article-meta">
            <span class="article-id">{{ article.id }}</span>
            <span class="category">{{ article.category }}</span>
            <span class="date">{{ new Date(article.create_at).toLocaleDateString() }}</span>
          </div>
          <div class="article-stats">
            <span>{{ article.views }} views</span>
            <span>{{ article.likes }} likes</span>
          </div>
        </div>
        
        <div v-if="(articles || []).length === 0" class="no-articles">
          无文章
        </div>
      </div>

      <!-- 分页控件（total 为后端返回的页数） -->
      <div class="pagination" v-if="total > 1">
        <button
          @click="handlePageChange(currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          上一页
        </button>
        <span class="pagination-info">
          第 {{ currentPage }} 页，共 {{ total }} 页
        </span>
        <button
          @click="handlePageChange(currentPage + 1)"
          :disabled="currentPage >= total"
          class="pagination-button"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  margin-bottom: 1.5rem;
  text-align: center;
  color: #333;
  font-size: 1.8rem;
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.categories {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.sort-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.sort-select {
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(5px);
  cursor: pointer;
  transition: all 0.3s;
  color: #333;
  font-size: 0.85rem;
}

.sort-select:hover {
  background: rgba(255, 255, 255, 0.4);
}

@media (max-width: 768px) {
  .filter-container {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .sort-container {
    width: 100%;
  }
  
  .sort-select {
    flex: 1;
  }
}

.categories button {
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(5px);
  cursor: pointer;
  transition: all 0.3s;
  color: #333;
  font-size: 0.85rem;
}

.categories button:hover {
  background: rgba(255, 255, 255, 0.4);
}

.categories button.active {
  background: rgba(51, 51, 51, 0.8);
  color: white;
  border-color: rgba(255, 255, 255, 0.2);
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article-card {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.6);
}

.article-author-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.article-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.article-author-name {
  font-size: 0.85rem;
  color: #71717A;
  font-weight: 500;
}

.article-title {
  font-size: 1.2rem;
  font-weight: bold;
  color: rgba(0, 0, 0, 0.8);
  text-decoration: none;
  margin-bottom: 0.5rem;
  display: block;
  line-height: 1.4;
}

.article-title:hover {
  color: #0066cc;
}

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.6);
  margin-bottom: 0.5rem;
}

.article-id {
  color: rgba(0, 0, 0, 0.6);
}

.article-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: rgba(0, 0, 0, 0.5);
}

.loading,
.error,
.no-articles {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #ff4444;
  background: rgba(255, 68, 68, 0.1);
  backdrop-filter: blur(5px);
  border-radius: 4px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
}

.pagination-button {
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  color: rgba(0, 0, 0, 0.8);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.5);
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.85rem;
  color: rgba(0, 0, 0, 0.6);
  font-weight: bold;
}
</style>