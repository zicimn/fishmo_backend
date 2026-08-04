<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { articleApi, type LinkResponse } from '@/api/article'

const links = ref<LinkResponse[]>([])
const linksLoading = ref(false)
const linksError = ref('')
const linksPage = ref(1)
const linksPageSize = ref(10)

const fetchUserLinks = async () => {
  linksLoading.value = true
  linksError.value = ''
  try {
    const response = await articleApi.getUserLinks(linksPage.value, linksPageSize.value)
    links.value = response.data.links
  } catch (err: unknown) {
    linksError.value = '加载不出来'
    console.error(err)
  } finally {
    linksLoading.value = false
  }
}

const handleDeleteLink = async (articleId: number, linkId: number) => {
  if (confirm('Are you sure you want to delete this link?')) {
    try {
      await articleApi.deleteUserLink(articleId, linkId)
      // Refresh links after deletion
      await fetchUserLinks()
    } catch (err: unknown) {
      console.error('删除链接失败:', err)
      linksError.value = '加载不出来'
    }
  }
}

onMounted(() => {
  fetchUserLinks()
})
</script>

<template>
  <div class="glass-card">
    <h1>我的链接</h1>

    <div v-if="linksError" class="error-message">
      {{ linksError }}
    </div>

    <div v-if="linksLoading" class="loading">
      加载链接中...
    </div>

    <div v-else-if="links.length === 0" class="empty-state">
      无链接
    </div>

    <div v-else class="links-list">
      <div v-for="link in links" :key="link.id" class="link-item">
        <div class="link-info">
          <h3>{{ link.title || link.url }}</h3>
          <a :href="link.url" target="_blank" rel="noopener noreferrer" class="link-url">
            {{ link.url }}
          </a>
          <p class="link-article">Article ID: {{ link.article_id }}</p>
        </div>
        <div class="link-actions">
          <button
            @click="handleDeleteLink(link.article_id, link.id)"
            class="delete-button"
          >
            Delete
          </button>
        </div>
      </div>

      <div class="pagination">
        <button
          @click="() => linksPage > 1 && linksPage-- && fetchUserLinks()"
          :disabled="linksPage === 1"
        >
          Previous
        </button>
        <span>Page {{ linksPage }}</span>
        <button @click="() => linksPage++ && fetchUserLinks()">
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-message {
  color: #E11D48;
  padding: 1rem;
  background: rgba(225, 29, 72, 0.1);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-style: italic;
  color: #71717A;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #71717A;
  font-style: italic;
}

.links-list {
  margin-top: 1rem;
}

.link-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  margin-bottom: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.link-item:hover {
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.link-info {
  flex: 1;
}

.link-info h3 {
  margin-bottom: 0.5rem;
  color: #18181B;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.link-url {
  display: block;
  color: #3B82F6;
  text-decoration: none;
  margin-bottom: 0.5rem;
  word-break: break-all;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.link-url:hover {
  text-decoration: underline;
  color: #2563EB;
}

.link-article {
  font-size: 0.9rem;
  color: #94A3B8;
  margin: 0;
}

.link-actions {
  margin-left: 1rem;
}

.delete-button {
  background: rgba(225, 29, 72, 0.1);
  border: 1px solid rgba(225, 29, 72, 0.3);
  color: #E11D48;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.delete-button:hover {
  background: rgba(225, 29, 72, 0.2);
  transform: translateY(-2px);
}

.delete-button:active {
  transform: scale(0.98);
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
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  color: #18181B;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pagination button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
}

.pagination button:active:not(:disabled) {
  transform: scale(0.98);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-weight: 700;
  color: #18181B;
}

/* Dark mode adapts */
:deep(.dark-mode) .link-item {
  background: rgba(39, 39, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15);
}

:deep(.dark-mode) .link-info h3 {
  color: #F9FAFB;
}

:deep(.dark-mode) .link-url {
  color: #60A5FA;
}

:deep(.dark-mode) .link-url:hover {
  color: #93BBFD;
}

:deep(.dark-mode) .link-article {
  color: #A1A1AA;
}

:deep(.dark-mode) .pagination button {
  background: rgba(39, 39, 42, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #F9FAFB;
}

:deep(.dark-mode) .pagination button:hover:not(:disabled) {
  background: rgba(63, 63, 70, 0.6);
}

:deep(.dark-mode) .pagination span {
  color: #F9FAFB;
}

:deep(.dark-mode) .delete-button {
  background: rgba(225, 29, 72, 0.15);
  border: 1px solid rgba(225, 29, 72, 0.3);
}

:deep(.dark-mode) .delete-button:hover {
  background: rgba(225, 29, 72, 0.25);
}
</style>
