<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/api/request'

interface AnnouncementItem {
  id: number
  title: string
  created_at: string
  content?: string
}

interface AnnouncementDetail {
  title: string
  content: string
  created_at: string
}

interface AnnouncementList {
  total: number
  items: AnnouncementItem[]
}

const announcements = ref<AnnouncementItem[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const size = 10
const expandedIds = ref<Set<number>>(new Set())

const fetchAnnouncements = async (page: number = 1) => {
  loading.value = true
  try {
    const response = await request.get<AnnouncementList>('/announcement/', {
      params: { page, size }
    })
    announcements.value = response.data.items
    totalPages.value = response.data.total
    currentPage.value = page
  } catch (error) {
    console.error('获取公告失败:', error)
    announcements.value = []
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

const toggleExpand = async (id: number) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
    const announcement = announcements.value.find(a => a.id === id)
    if (announcement && !announcement.content) {
      try {
        const response = await request.get(`/announcement/browse/${id}`)
        announcement.content = response.data.content
      } catch (error) {
        console.error('获取公告详情失败:', error)
      }
    }
  }
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    expandedIds.value.clear()
    fetchAnnouncements(page)
  }
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<template>
  <div class="announcement-page">
    <div class="page-header">
      <h1>更新栏</h1>
      <p class="page-subtitle">查看最新更新和系统通知</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <span>加载中...</span>
    </div>

    <div v-else-if="announcements.length === 0" class="empty-state">
      <p>暂无更新</p>
    </div>

    <div v-else class="announcement-list">
      <div 
        v-for="announcement in announcements" 
        :key="announcement.id" 
        class="announcement-card"
        :class="{ 'expanded': expandedIds.has(announcement.id) }"
      >
        <div class="announcement-header" @click="toggleExpand(announcement.id)">
          <div class="announcement-title">
            {{ announcement.title }}
          </div>
          <div class="announcement-header-right">
            <span class="announcement-date">{{ announcement.created_at }}</span>
            <span class="expand-icon" :class="{ 'rotated': expandedIds.has(announcement.id) }">▼</span>
          </div>
        </div>
        <div class="announcement-footer" @click="toggleExpand(announcement.id)">
          <span class="read-more">{{ expandedIds.has(announcement.id) ? '收起' : '展开' }}</span>
        </div>
        <div v-if="expandedIds.has(announcement.id)" class="announcement-content">
          <div class="article-content">{{ announcement.content }}</div>
        </div>
      </div>
    </div>

    <div v-if="!loading && announcements.length > 0 && totalPages > 1" class="pagination">
      <button 
        class="pagination-btn" 
        :disabled="currentPage <= 1"
        @click="goToPage(currentPage - 1)"
      >
        ← 上一页
      </button>
      <span class="pagination-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
      <button 
        class="pagination-btn" 
        :disabled="currentPage >= totalPages"
        @click="goToPage(currentPage + 1)"
      >
        下一页 →
      </button>
    </div>
  </div>
</template>

<style scoped>
.announcement-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.8rem;
  color: #18181B;
  margin-bottom: 0.5rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.page-subtitle {
  color: #71717A;
  font-size: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #71717A;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #71717A;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.announcement-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.announcement-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

.announcement-card:active {
  transform: scale(0.99);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.announcement-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #18181B;
  line-height: 1.4;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.announcement-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.announcement-date {
  font-size: 0.8125rem;
  color: #94A3B8;
  font-family: 'Geist Mono', 'JetBrains Mono', 'IBM Plex Mono', monospace;
}

.expand-icon {
  font-size: 0.6rem;
  color: #94A3B8;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.announcement-footer {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.read-more {
  font-size: 0.8rem;
  color: #3B82F6;
  cursor: pointer;
}

.announcement-content {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.article-content {
  color: #18181B;
  line-height: 1.65;
  font-size: 1rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
}

.pagination-btn {
  padding: 0.4rem 0.8rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  color: #18181B;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.85);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.85rem;
  color: #71717A;
  font-weight: bold;
}

@media (max-width: 768px) {
  .announcement-page {
    padding: 0.5rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .announcement-card {
    padding: 1rem;
  }

  .announcement-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .announcement-date {
    font-size: 0.8rem;
  }
}
</style>