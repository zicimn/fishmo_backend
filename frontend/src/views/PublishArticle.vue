<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { articleApi } from '@/api/article'
import { useRouter } from 'vue-router'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const router = useRouter()

const title = ref('')
const category = ref('ai')
const content = ref('')
const images = ref<string[]>([])
const error = ref('')
const success = ref('')
const loading = ref(false)
const showPreview = ref(false)
const status = ref(true)

// Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 渲染后的 HTML
const renderedContent = computed(() => {
  if (!content.value) return ''
  const html = md.render(content.value)
  return DOMPurify.sanitize(html)
})

// 自动保存相关
const lastSavedTime = ref('')
const isSaving = ref(false)
let saveTimer: ReturnType<typeof setInterval> | null = null
const DRAFT_KEY = 'article_draft'

const categories = ['all', 'code', 'health', 'other', 'test', 'study']

// 加载草稿
const loadDraft = () => {
  try {
    const draft = localStorage.getItem(DRAFT_KEY)
    if (draft) {
      const data = JSON.parse(draft)
      title.value = data.title || ''
      category.value = data.category || 'ai'
      content.value = data.content || ''
      // 图片数据较大，不保存到 localStorage
      lastSavedTime.value = data.savedTime || ''
    }
  } catch (e) {
    console.error('Failed to load draft:', e)
  }
}

// 保存草稿
const saveDraft = async () => {
  if (loading.value) return

  // 只有有内容时才保存
  if (!title.value && !content.value) return

  isSaving.value = true
  try {
    const draft = {
      title: title.value,
      category: category.value,
      content: content.value,
      savedTime: new Date().toLocaleString()
    }
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
    lastSavedTime.value = draft.savedTime
  } catch (e) {
    console.error('Failed to save draft:', e)
  } finally {
    isSaving.value = false
  }
}

// 清除草稿
const clearDraft = () => {
  localStorage.removeItem(DRAFT_KEY)
  lastSavedTime.value = ''
}

// 监听数据变化自动保存
watch([title, category, content], () => {
  saveDraft()
}, { deep: true })

// 定时保存（额外保障）
onMounted(() => {
  loadDraft()
  saveTimer = setInterval(saveDraft, 30000) // 每30秒自动保存
})

onUnmounted(() => {
  if (saveTimer) {
    clearInterval(saveTimer)
  }
})

const handlePublish = async () => {
  if (!title.value || !category.value || !content.value) {
    error.value = 'Please fill in all required fields'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await articleApi.publish({ status: status.value, title: title.value, category: category.value, content: content.value, images: images.value })
    success.value = 'Article published successfully!'
    // 发布成功后清除草稿
    clearDraft()
    // 跳转到文章详情页
    const articleId = response.data?.id
    setTimeout(() => {
      router.push(articleId ? `/article/${articleId}` : '/')
    }, 2000)
  } catch (err: unknown) {
    error.value = '发布文章失败，请重试。'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fileInput = ref<HTMLInputElement | null>(null)

const addImage = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (file) {
      // 限制单张图片大小为16MB
      if (file.size > 16 * 1024 * 1024) {
        error.value = '单张图片大小不能超过16MB'
        return
      }

      // 计算当前已上传图片的总大小
      const currentTotalSize = images.value.reduce((total, img) => total + img.length, 0)
      const newTotalSize = currentTotalSize + file.size

      // 限制所有图片总大小为16MB
      if (newTotalSize > 16 * 1024 * 1024) {
        error.value = '所有图片总大小不能超过16MB'
        return
      }

      const reader = new FileReader()
      reader.onload = (event) => {
        const result = event.target?.result as string
        images.value.push(result)
        error.value = '' // 清除错误信息
      }
      reader.readAsDataURL(file)
    }
  }
}

const removeImage = (index: number) => {
  images.value.splice(index, 1)
}

// Markdown 插入函数
const insertMarkdown = (prefix: string, suffix: string, placeholder: string) => {
  const textarea = document.getElementById('content') as HTMLTextAreaElement
  if (!textarea || loading.value) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)

  const newText = content.value.substring(0, start) +
                  prefix +
                  (selectedText || placeholder) +
                  suffix +
                  content.value.substring(end)

  content.value = newText

  // 设置光标位置
  setTimeout(() => {
    textarea.focus()
    const cursorPos = start + prefix.length + (selectedText ? selectedText.length : placeholder.length) + suffix.length
    textarea.setSelectionRange(cursorPos, cursorPos)
  }, 0)
}
</script>

<template>
  <div class="publish-page">
    <form @submit.prevent="handlePublish" novalidate class="publish-form">
      <div class="publish-layout">
        <!-- ===== Left Sidebar ===== -->
        <aside class="publish-sidebar">
          <div class="sidebar-inner">
            <!-- Header -->
            <div class="sidebar-header">
              <h2 class="sidebar-title">设置</h2>
            </div>

            <!-- Category -->
            <div class="sb-section">
              <label class="sb-label">分类</label>
              <div class="select-wrapper">
                <select v-model="category" :disabled="loading" class="sb-select">
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
                <span class="select-chevron">
                  <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
                    <path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </div>
            </div>

            <!-- Status Toggle -->
            <div class="sb-section">
              <label class="sb-label">状态</label>
              <div class="status-group">
                <button
                  type="button"
                  :class="['status-btn', { active: status }]"
                  @click="status = true"
                  :disabled="loading"
                >
                  <span class="status-indicator public"></span>
                  公开
                </button>
                <button
                  type="button"
                  :class="['status-btn', { active: !status }]"
                  @click="status = false"
                  :disabled="loading"
                >
                  <span class="status-indicator draft"></span>
                  草稿
                </button>
              </div>
              <p class="status-hint">{{ status ? '所有用户可见' : '仅自己可见' }}</p>
            </div>

            <!-- Divider -->
            <div class="sb-divider"></div>

            <!-- Images -->
            <div class="sb-section">
              <label class="sb-label">配图</label>
              <button
                type="button"
                @click="addImage"
                :disabled="loading"
                class="sb-add-image-btn"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
                <span>添加图片</span>
              </button>
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleFileSelect"
              />
            </div>

            <!-- Spacer to push publish + autosave to bottom -->
            <div class="sb-spacer"></div>

            <!-- Publish -->
            <div class="sb-publish-area">
              <button type="submit" class="sb-publish-btn" :disabled="loading">
                <span v-if="loading" class="btn-spinner"></span>
                <span v-else class="btn-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="19" x2="12" y2="5"/>
                    <polyline points="5 12 12 5 19 12"/>
                  </svg>
                </span>
                {{ loading ? '发布中...' : '发布文章' }}
              </button>
            </div>

            <!-- Auto-save status -->
            <div class="sb-auto-save">
              <span v-if="isSaving" class="as-saving">
                <span class="as-spinner"></span>
                保存中...
              </span>
              <span v-else-if="lastSavedTime" class="as-saved">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                已自动保存
              </span>
              <span v-else class="as-idle">
                自动保存就绪
              </span>
            </div>
          </div>
        </aside>

        <!-- ===== Main Editor ===== -->
        <main class="publish-editor">
          <!-- Title -->
          <div class="title-field">
            <input
              type="text"
              v-model="title"
              :disabled="loading"
              placeholder="输入文章标题..."
              class="title-input"
            />
            <div class="title-underline"></div>
          </div>

          <!-- Gradient Divider -->
          <div class="editor-divider"></div>

          <!-- Markdown Toolbar -->
          <div class="md-toolbar">
            <button type="button" @click="insertMarkdown('**', '**', '加粗文本')" :disabled="loading" class="md-btn" title="加粗"><strong>B</strong></button>
            <button type="button" @click="insertMarkdown('*', '*', '斜体文本')" :disabled="loading" class="md-btn" title="斜体"><em>I</em></button>
            <button type="button" @click="insertMarkdown('~~', '~~', '删除线')" :disabled="loading" class="md-btn" title="删除线"><del>S</del></button>
            <span class="md-sep"></span>
            <button type="button" @click="insertMarkdown('# ', '', '一级标题')" :disabled="loading" class="md-btn" title="标题 1">H1</button>
            <button type="button" @click="insertMarkdown('## ', '', '二级标题')" :disabled="loading" class="md-btn" title="标题 2">H2</button>
            <button type="button" @click="insertMarkdown('### ', '', '三级标题')" :disabled="loading" class="md-btn" title="标题 3">H3</button>
            <span class="md-sep"></span>
            <button type="button" @click="insertMarkdown('- ', '', '无序列表')" :disabled="loading" class="md-btn" title="无序列表">&bull;</button>
            <button type="button" @click="insertMarkdown('1. ', '', '有序列表')" :disabled="loading" class="md-btn" title="有序列表">1.</button>
            <span class="md-sep"></span>
            <button type="button" @click="insertMarkdown('```\n', '\n```', '代码块')" :disabled="loading" class="md-btn" title="代码块">&lt;/&gt;</button>
            <button type="button" @click="insertMarkdown('`', '`', '行内代码')" :disabled="loading" class="md-btn" title="行内代码"><code>`</code></button>
            <button type="button" @click="insertMarkdown('[', '](url)', '链接文本')" :disabled="loading" class="md-btn" title="链接">Link</button>
            <span class="md-sep"></span>
            <button
              type="button"
              @click="showPreview = !showPreview"
              :disabled="loading"
              :class="['md-preview-btn', { active: showPreview }]"
            >
              <svg v-if="showPreview" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              {{ showPreview ? '编辑' : '预览' }}
            </button>
          </div>

          <!-- Content Area -->
          <div class="editor-content-area">
            <!-- Editing mode -->
            <textarea
              v-if="!showPreview"
              id="content"
              v-model="content"
              :disabled="loading"
              placeholder="在这里开始写作... 支持 Markdown 格式"
              class="content-textarea"
            ></textarea>
            <!-- Preview mode -->
            <div
              v-else
              class="preview-content"
              v-html="renderedContent"
            ></div>
          </div>

          <!-- Image Strip (below editor) -->
          <div v-if="images.length" class="image-strip">
            <div class="image-strip-label">图片 ({{ images.length }})</div>
            <div class="image-strip-grid">
              <div v-for="(img, idx) in images" :key="idx" class="image-strip-item">
                <img :src="img" :alt="`图片 ${idx + 1}`" />
                <button
                  type="button"
                  @click="removeImage(idx)"
                  :disabled="loading"
                  class="image-strip-remove"
                  title="删除图片"
                >
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- Messages -->
      <div class="messages-area">
        <Transition name="msg">
          <div v-if="error" class="message error-msg">{{ error }}</div>
        </Transition>
        <Transition name="msg">
          <div v-if="success" class="message success-msg">{{ success }}</div>
        </Transition>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* ============================================
   Page Layout
   ============================================ */
.publish-page {
  max-width: 1260px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100dvh;
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(59, 130, 246, 0.03) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 100%, rgba(16, 185, 129, 0.02) 0%, transparent 60%);
}

.publish-form {
  all: unset;
  display: block;
}

/* ============================================
   Main Layout: Sidebar + Editor
   ============================================ */
.publish-layout {
  display: flex;
  gap: 0;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ============================================
   Left Sidebar
   ============================================ */
.publish-sidebar {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid rgba(226, 232, 240, 0.5);
  background: rgba(255, 255, 255, 0.3);
  position: sticky;
  top: 2rem;
  align-self: flex-start;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
}

.sidebar-inner {
  padding: 1.75rem 1.5rem;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  gap: 0.125rem;
}

.sidebar-header {
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(226, 232, 240, 0.4);
}

.sidebar-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #71717A;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin: 0;
}

/* Sidebar Sections */
.sb-section {
  margin-bottom: 1.25rem;
}

.sb-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #18181B;
  margin-bottom: 0.5rem;
  letter-spacing: 0.02em;
}

/* ===== Category Select ===== */
.select-wrapper {
  position: relative;
}

.select-wrapper .select-chevron {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #71717A;
  pointer-events: none;
  display: flex;
  align-items: center;
}

.sb-select {
  width: 100%;
  padding: 0.55rem 2rem 0.55rem 0.75rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.6);
  color: #18181B;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sb-select:hover:not(:disabled) {
  border-color: rgba(59, 130, 246, 0.25);
  background: rgba(255, 255, 255, 0.8);
}

.sb-select:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.sb-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Status Toggle ===== */
.status-group {
  display: flex;
  gap: 0.5rem;
}

.status-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.55rem 0.5rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  color: #52525B;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  line-height: 1;
}

.status-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(59, 130, 246, 0.2);
}

.status-btn.active:first-child {
  background: rgba(16, 185, 129, 0.1);
  border-color: #10B981;
  color: #059669;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.08);
}

.status-btn.active:last-child {
  background: rgba(245, 158, 11, 0.1);
  border-color: #F59E0B;
  color: #D97706;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.08);
}

.status-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.public {
  background: #10B981;
}

.status-indicator.draft {
  background: #F59E0B;
}

.status-btn:not(.active) .status-indicator {
  opacity: 0.4;
}

.status-hint {
  margin: 0.35rem 0 0;
  font-size: 0.72rem;
  color: #A1A1AA;
  line-height: 1.4;
}

/* ===== Sidebar Divider ===== */
.sb-divider {
  height: 1px;
  background: linear-gradient(
    to right,
    rgba(226, 232, 240, 0.6),
    rgba(226, 232, 240, 0.2)
  );
  margin: 0.5rem 0 1rem;
}

/* ===== Add Image Button ===== */
.sb-add-image-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  border: 1px dashed rgba(59, 130, 246, 0.25);
  border-radius: 0.5rem;
  background: rgba(59, 130, 246, 0.05);
  color: #3B82F6;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  line-height: 1;
}

.sb-add-image-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
}

.sb-add-image-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.sb-add-image-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Spacer ===== */
.sb-spacer {
  flex: 1;
  min-height: 1rem;
}

/* ===== Publish Button ===== */
.sb-publish-area {
  margin-bottom: 0.75rem;
}

.sb-publish-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  background: #18181B;
  border: none;
  border-radius: 0.5rem;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  letter-spacing: 0.01em;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  line-height: 1;
}

.sb-publish-btn:hover:not(:disabled) {
  background: #27272A;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(24, 24, 27, 0.15);
}

.sb-publish-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.sb-publish-btn:disabled {
  background: rgba(113, 113, 122, 0.35);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

.btn-icon {
  display: flex;
  align-items: center;
}

/* ===== Auto Save ===== */
.sb-auto-save {
  padding-top: 0.75rem;
  border-top: 1px solid rgba(226, 232, 240, 0.3);
}

.as-saving {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  color: #3B82F6;
  font-weight: 500;
}

.as-spinner {
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

.as-saved {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: #10B981;
  font-weight: 500;
}

.as-idle {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: #A1A1AA;
  font-weight: 400;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ============================================
   Main Editor
   ============================================ */
.publish-editor {
  flex: 1;
  padding: 2rem 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ===== Title ===== */
.title-field {
  margin-bottom: 1rem;
  position: relative;
}

.title-input {
  width: 100%;
  border: none;
  background: transparent;
  font-size: 1.75rem;
  font-weight: 700;
  color: #18181B;
  letter-spacing: -0.03em;
  line-height: 1.3;
  padding: 0.25rem 0;
  font-family: inherit;
  outline: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.title-input::placeholder {
  color: #D4D4D8;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.title-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.title-underline {
  height: 2px;
  background: linear-gradient(
    to right,
    rgba(226, 232, 240, 0.6),
    rgba(226, 232, 240, 0.3)
  );
  border-radius: 1px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  margin-top: 0.25rem;
}

.title-input:focus ~ .title-underline,
.title-input:not(:placeholder-shown) ~ .title-underline {
  background: linear-gradient(
    to right,
    #3B82F6,
    rgba(59, 130, 246, 0.3)
  );
  height: 2px;
}

/* ===== Editor Divider ===== */
.editor-divider {
  height: 1px;
  background: linear-gradient(
    to right,
    rgba(226, 232, 240, 0.7) 0%,
    rgba(226, 232, 240, 0.5) 50%,
    transparent 100%
  );
  margin-bottom: 0.75rem;
}

/* ===== Markdown Toolbar ===== */
.md-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem 0.625rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.md-toolbar:focus-within {
  border-color: rgba(59, 130, 246, 0.2);
}

.md-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.55rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  background: transparent;
  color: #52525B;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  line-height: 1;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  min-width: 28px;
}

.md-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.15);
  color: #3B82F6;
}

.md-btn:active:not(:disabled) {
  transform: scale(0.94);
}

.md-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.md-btn strong {
  font-weight: 700;
}

.md-btn em {
  font-style: italic;
}

.md-btn del {
  text-decoration: line-through;
}

.md-btn code {
  font-family: 'JetBrains Mono', 'Fira Code', monospace, 'Geist', 'Inter', sans-serif;
  font-size: 0.85em;
}

.md-sep {
  width: 1px;
  height: 20px;
  background: rgba(203, 213, 225, 0.5);
  margin: 0 0.2rem;
  flex-shrink: 0;
}

.md-preview-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.7rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.5);
  color: #71717A;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  font-family: inherit;
  line-height: 1;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  margin-left: auto;
}

.md-preview-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
  color: #3B82F6;
}

.md-preview-btn.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3B82F6;
  color: #3B82F6;
}

.md-preview-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ===== Content Area ===== */
.editor-content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 420px;
}

.content-textarea {
  flex: 1;
  width: 100%;
  min-height: 400px;
  padding: 1rem 0;
  border: none;
  background: transparent;
  font-size: 1rem;
  line-height: 1.8;
  color: #18181B;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.content-textarea::placeholder {
  color: #D4D4D8;
  font-weight: 400;
}

.content-textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Preview Content (reuses markdown styles from original) */
.preview-content {
  flex: 1;
  min-height: 400px;
  padding: 1rem 0;
  background: transparent;
  color: #27272A;
  line-height: 1.8;
  word-wrap: break-word;
  overflow-x: auto;
}

.preview-content h1 {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(24, 24, 27, 0.06);
  color: #18181B;
}

.preview-content h2 {
  font-size: 1.5rem;
  font-weight: 650;
  letter-spacing: -0.02em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  color: #18181B;
}

.preview-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
  color: #27272A;
}

.preview-content p {
  margin-bottom: 1.25rem;
  line-height: 1.8;
}

.preview-content strong {
  font-weight: 650;
  color: #18181B;
}

.preview-content em {
  font-style: italic;
}

.preview-content del {
  text-decoration: line-through;
  color: #A1A1AA;
}

.preview-content ul,
.preview-content ol {
  padding-left: 1.5rem;
  margin-bottom: 1.25rem;
}

.preview-content li {
  margin-bottom: 0.5rem;
  line-height: 1.75;
}

.preview-content code {
  padding: 0.2em 0.4em;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 4px;
  font-size: 0.85em;
  font-family: 'JetBrains Mono', 'Fira Code', monospace, 'Geist', 'Inter', sans-serif;
  color: #3B82F6;
  font-weight: 500;
}

.preview-content pre {
  padding: 1.25rem 1.5rem;
  background: #18181B;
  border-radius: 0.75rem;
  overflow-x: auto;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(24, 24, 27, 0.08);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.preview-content pre code {
  background: transparent;
  padding: 0;
  font-size: 0.875rem;
  color: #E4E4E7;
  font-weight: 400;
}

.preview-content a {
  color: #3B82F6;
  text-decoration: none;
  background-image: linear-gradient(#3B82F6, #3B82F6);
  background-position: 0% 100%;
  background-repeat: no-repeat;
  background-size: 0% 1px;
  transition: background-size 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.preview-content a:hover {
  background-size: 100% 1px;
  color: #2563EB;
}

.preview-content blockquote {
  border-left: 3px solid #3B82F6;
  padding: 0.75rem 1.25rem;
  margin: 1.5rem 0;
  color: #52525B;
  font-style: italic;
  background: rgba(59, 130, 246, 0.04);
  border-radius: 0 0.5rem 0.5rem 0;
}

.preview-content hr {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(24, 24, 27, 0.08), transparent);
  margin: 2.5rem 0;
}

.preview-content img {
  max-width: 100%;
  border-radius: 0.75rem;
  margin: 2rem auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  display: block;
}

.preview-content table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.preview-content th,
.preview-content td {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(24, 24, 27, 0.08);
  text-align: left;
}

.preview-content th {
  background: rgba(24, 24, 27, 0.03);
  font-weight: 600;
  color: #18181B;
}

/* ===== Image Strip ===== */
.image-strip {
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.5);
}

.image-strip-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #71717A;
  margin-bottom: 0.75rem;
  letter-spacing: 0.03em;
}

.image-strip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.625rem;
}

.image-strip-item {
  position: relative;
  width: 76px;
  height: 76px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid rgba(226, 232, 240, 0.6);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.image-strip-item:hover {
  border-color: rgba(226, 232, 240, 0.9);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.image-strip-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-strip-remove {
  position: absolute;
  top: 3px;
  right: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(24, 24, 27, 0.55);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  padding: 0;
}

.image-strip-item:hover .image-strip-remove {
  opacity: 1;
}

.image-strip-remove:hover {
  background: #E11D48;
  transform: scale(1.1);
}

.image-strip-remove:disabled {
  opacity: 0;
  cursor: not-allowed;
}

/* ============================================
   Messages
   ============================================ */
.messages-area {
  margin-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message {
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.error-msg {
  color: #E11D48;
  background: rgba(225, 29, 72, 0.08);
  border: 1px solid rgba(225, 29, 72, 0.12);
}

.success-msg {
  color: #10B981;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.12);
}

/* ===== Message Transition ===== */
.msg-enter-active,
.msg-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.msg-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.msg-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* ============================================
   Responsive
   ============================================ */
@media (max-width: 900px) {
  .publish-layout {
    flex-direction: column;
  }

  .publish-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(226, 232, 240, 0.5);
    position: static;
    max-height: none;
    overflow: visible;
  }

  .sidebar-inner {
    padding: 1.25rem 1.5rem;
    min-height: auto;
  }

  .sb-spacer {
    display: none;
  }

  .publish-editor {
    padding: 1.5rem;
  }

  .title-input {
    font-size: 1.4rem;
  }

  .status-group {
    max-width: 240px;
  }
}

@media (max-width: 600px) {
  .publish-page {
    padding: 1rem;
  }

  .publish-editor {
    padding: 1.25rem;
  }

  .title-input {
    font-size: 1.2rem;
  }

  .md-toolbar {
    gap: 0.125rem;
    padding: 0.375rem 0.5rem;
  }

  .md-btn {
    padding: 0.3rem 0.45rem;
    font-size: 0.72rem;
    min-width: 24px;
  }

  .image-strip-item {
    width: 64px;
    height: 64px;
  }
}
</style>
