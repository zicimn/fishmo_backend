<script setup lang="ts">
import { ref } from 'vue'
import request from '@/api/request'

const activeTool = ref('compression')
const windowObj = window

interface Tool {
  id: string
  name: string
  icon: string
  description: string
}

const tools = ref<Tool[]>([
  { id: 'compression', name: '图片压缩', icon: '', description: '压缩图片体积' },
  { id: 'diviation', name: '今日运势', icon: '', description: '测试今日运势' },
  { id: 'watermark', name: '', icon: '', description: '' },
  { id: 'format', name: '', icon: '', description: '' },
  { id: 'resize', name: '', icon: '', description: '' },
  { id: 'crop', name: '', icon: '', description: '' },
  { id: 'tool7', name: '', icon: '', description: '' },
  { id: 'tool8', name: '', icon: '', description: '' }
])

const compressionImages = ref<File[]>([])
const compressionQuality = ref(80)
const compressionStyle = ref('webp')
const compressionResults = ref<string[]>([])
const compressionLoading = ref(false)
const compressionError = ref('')

const compressedImages = ref<{ name: string; url: string; size: number }[]>([])

// 命运测试相关
const diviationLoading = ref(false)
const diviationError = ref('')
const diviationData = ref<{ user_id: number; fate: string; url: string } | null>(null)

const handleToolClick = (toolId: string) => {
  // 查找工具对象
  const tool = tools.value.find(t => t.id === toolId)
  if (!tool || !tool.name) {
    return // 空白卡片不做任何操作
  }

  activeTool.value = toolId
  if (toolId === 'diviation') {
    handleDiviation()
  } else if (toolId !== 'compression') {
    alert('该功能正在开发中，敬请期待！')
  }
}

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    compressionImages.value = [...compressionImages.value, ...files]
    compressionError.value = ''
  }
}

const removeImage = (index: number) => {
  compressionImages.value.splice(index, 1)
}

const handleCompression = async () => {
  if (compressionImages.value.length === 0) {
    compressionError.value = '请至少上传一张图片'
    return
  }

  compressionLoading.value = true
  compressionError.value = ''
  compressedImages.value = []

  try {
    const base64Images = await Promise.all(
      compressionImages.value.map(file => {
        return new Promise<string>((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = () => resolve(reader.result as string)
          reader.onerror = reject
          reader.readAsDataURL(file)
        })
      })
    )

    const response = await request.post('/tools/compression', {
      images: base64Images,
      quality: compressionQuality.value,
      style: compressionStyle.value
    })

    compressionResults.value = response.data.images

    compressionResults.value.forEach((base64, index) => {
      const parts = base64.split(',')
      if (parts.length < 2) return

      const byteString = atob(parts[1] || '')
      const mimePart = parts[0]?.split(':')[1]
      if (!mimePart) return
      const mimeString = mimePart.split(';')[0]

      const ab = new ArrayBuffer(byteString.length)
      const ia = new Uint8Array(ab)
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i)
      }
      const blob = new Blob([ab], { type: mimeString })
      const url = windowObj.URL.createObjectURL(blob)

      const originalImage = compressionImages.value[index]
      if (!originalImage) return

      compressedImages.value.push({
        name: `${originalImage.name.split('.')[0]}.${compressionStyle.value}`,
        url: url,
        size: blob.size
      })
    })
  } catch (error: unknown) {
    let errorMessage = '压缩失败，请稍后重试'
    if (typeof error === 'object' && error !== null) {
      // 安全地访问错误对象的属性
      if ('response' in error && typeof error.response === 'object' && error.response !== null) {
        const response = error.response
        if ('data' in response && typeof response.data === 'object' && response.data !== null) {
          const data = response.data
          if ('detail' in data && typeof data.detail === 'string') {
            errorMessage = data.detail
          }
        }
      } else if ('message' in error && typeof error.message === 'string') {
        errorMessage = error.message
      }
    }
    compressionError.value = errorMessage
    console.error('Compression failed:', error)
  } finally {
    compressionLoading.value = false
  }
}

const downloadImage = (image: { name: string; url: string }) => {
  const link = document.createElement('a')
  link.href = image.url
  link.download = image.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const downloadAllImages = () => {
  compressedImages.value.forEach((image, index) => {
    setTimeout(() => {
      downloadImage(image)
    }, index * 200)
  })
}

const clearCompression = () => {
  compressionImages.value = []
  compressionResults.value = []
  compressedImages.value = []
  compressionError.value = ''
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

const handleDiviation = async () => {
  diviationLoading.value = true
  diviationError.value = ''
  diviationData.value = null

  try {
    const response = await request.get('/tools/diviation')
    diviationData.value = response.data
  } catch (error: unknown) {
    let errorMessage = '获取命运测试失败，请稍后重试'
    if (typeof error === 'object' && error !== null) {
      if ('response' in error && typeof error.response === 'object' && error.response !== null) {
        const response = error.response
        if ('data' in response && typeof response.data === 'object' && response.data !== null) {
          const data = response.data
          if ('detail' in data && typeof data.detail === 'string') {
            errorMessage = data.detail
          }
        }
      } else if ('message' in error && typeof error.message === 'string') {
        errorMessage = error.message
      }
    }
    diviationError.value = errorMessage
    console.error('Diviation failed:', error)
  } finally {
    diviationLoading.value = false
  }
}
</script>

<template>
  <div class="tools-page">
    <div class="tools-header">
      <h1>🛠️ 工具箱</h1>
      <p class="tools-subtitle">提供多种工具，让您的工作更加便捷</p>
    </div>

    <div class="tools-grid">
      <div
        v-for="tool in tools"
        :key="tool.id"
        class="tool-card"
        :class="{ active: activeTool === tool.id, empty: !tool.name }"
        @click="handleToolClick(tool.id)"
      >
      <div class="tool-name" v-if="tool.name">{{ tool.name }}</div>
      <div class="tool-description" v-if="tool.description">{{ tool.description }}</div>
      </div>
    </div>

    <div v-if="activeTool === 'compression'" class="tool-content">
      <div class="content-section">
        <h2>🗜️ 图片压缩</h2>

        <div class="upload-area">
          <input
            type="file"
            id="image-upload"
            accept="image/*"
            multiple
            @change="handleImageUpload"
            class="file-input"
          />
          <label for="image-upload" class="upload-label">
            <span class="upload-icon">📁</span>
            <span class="upload-text">点击选择图片或拖拽到此处</span>
            <span class="upload-hint">支持多选，最多10张图片</span>
          </label>
        </div>

        <div v-if="compressionImages.length > 0" class="selected-images">
          <div class="images-header">
            <span>已选择 {{ compressionImages.length }} 张图片</span>
            <button @click="clearCompression" class="clear-btn">清空</button>
          </div>
          <div class="images-list">
            <div v-for="(image, index) in compressionImages" :key="index" class="image-item">
              <img :src="windowObj.URL.createObjectURL(image)" alt="" class="image-thumbnail" />
              <div class="image-info">
                <span class="image-name">{{ image.name }}</span>
                <span class="image-size">{{ formatFileSize(image.size) }}</span>
              </div>
              <button @click="removeImage(index)" class="remove-btn">✕</button>
            </div>
          </div>
        </div>

        <div class="compression-options">
          <div class="option-group">
            <label class="option-label">压缩质量</label>
            <div class="quality-slider">
              <input
                type="range"
                min="10"
                max="100"
                v-model="compressionQuality"
                class="slider"
              />
              <span class="quality-value">{{ compressionQuality }}%</span>
            </div>
          </div>

          <div class="option-group">
            <label class="option-label">输出格式</label>
            <div class="format-buttons">
              <button
                class="format-btn"
                :class="{ active: compressionStyle === 'webp' }"
                @click="compressionStyle = 'webp'"
              >
                WebP
              </button>
              <button
                class="format-btn"
                :class="{ active: compressionStyle === 'jpg' }"
                @click="compressionStyle = 'jpg'"
              >
                JPEG
              </button>
              <button
                class="format-btn"
                :class="{ active: compressionStyle === 'png' }"
                @click="compressionStyle = 'png'"
              >
                PNG
              </button>
            </div>
          </div>
        </div>

        <div v-if="compressionError" class="error-message">
          {{ compressionError }}
        </div>

        <button
          @click="handleCompression"
          :disabled="compressionImages.length === 0 || compressionLoading"
          class="compress-btn"
        >
          {{ compressionLoading ? '压缩中...' : '开始压缩' }}
        </button>

        <div v-if="compressedImages.length > 0" class="results-section">
          <div class="results-header">
            <h3>压缩结果</h3>
            <button @click="downloadAllImages" class="download-all-btn">
              下载全部
            </button>
          </div>
          <div class="results-list">
            <div v-for="(image, index) in compressedImages" :key="index" class="result-item">
              <img :src="image.url" alt="" class="result-thumbnail" />
              <div class="result-info">
                <span class="result-name">{{ image.name }}</span>
                <span class="result-size">{{ formatFileSize(image.size) }}</span>
              </div>
              <button @click="downloadImage(image)" class="download-btn">下载</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="activeTool === 'diviation'" class="tool-content">
      <div class="content-section">
        <h2>今日运势</h2>

        <div v-if="diviationLoading" class="loading">
          正在获取今日运势...
        </div>

        <div v-else-if="diviationError" class="error-message">
          {{ diviationError }}
        </div>

        <div v-else-if="diviationData" class="diviation-result">
          <div class="diviation-content">
            <div class="diviation-image">
              <img :src="diviationData.url" alt="今日运势" class="fate-image">
            </div>
            <div class="diviation-text">
              <h3>今日运势</h3>
              <p class="fate-text">{{ diviationData.fate }}</p>
              <p class="user-id">用户ID: {{ diviationData.user_id }}</p>
            </div>
          </div>
        </div>

        <div v-else class="diviation-placeholder">
          <p>点击上方的「今日运势」按钮开始测试</p>
        </div>
      </div>
    </div>

    <div v-else class="tool-content empty">
      <div class="coming-soon">
        <div class="coming-soon-icon">🚧</div>
        <h3>该功能正在开发中</h3>
        <p>敬请期待！</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tools-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.tools-header {
  text-align: center;
  margin-bottom: 3rem;
}

.tools-header h1 {
  font-size: 2.5rem;
  color: #18181B;
  margin-bottom: 0.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.tools-subtitle {
  color: #71717A;
  font-size: 1.1rem;
  line-height: 1.65;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.tool-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur-xl;
  border-radius: 1.25rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 2px solid transparent;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
  border-color: #3B82F6;
}

.tool-card:active {
  transform: scale(0.98);
}

.tool-card.active {
  border-color: #3B82F6;
  background: rgba(59, 130, 246, 0.08);
}

.tool-card.empty {
  background: rgba(200, 200, 200, 0.15);
  border: 2px dashed rgba(226, 232, 240, 0.5);
  cursor: default;
  box-shadow: none;
}

.tool-card.empty:hover {
  transform: none;
  box-shadow: none;
  border-color: rgba(226, 232, 240, 0.5);
}

.tool-card.empty:active {
  transform: none;
}

.tool-name {
  font-size: 1.3rem;
  font-weight: 700;
  color: #18181B;
  margin-bottom: 0.5rem;
}

.tool-description {
  font-size: 0.9rem;
  color: #71717A;
  line-height: 1.65;
}

.tool-content {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur-xl;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid rgba(226, 232, 240, 0.5);
}

.tool-content.empty {
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.content-section h2 {
  font-size: 1.8rem;
  color: #18181B;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.upload-area {
  margin-bottom: 2rem;
}

.file-input {
  display: none;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  border: 2px dashed rgba(203, 213, 225, 0.6);
  border-radius: 1.25rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: rgba(255, 255, 255, 0.4);
}

.upload-label:hover {
  border-color: #3B82F6;
  background: rgba(59, 130, 246, 0.04);
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.2rem;
  color: #18181B;
  margin-bottom: 0.5rem;
}

.upload-hint {
  font-size: 0.9rem;
  color: #94A3B8;
  line-height: 1.65;
}

.selected-images {
  margin-bottom: 2rem;
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: 700;
  color: #18181B;
}

.clear-btn {
  padding: 0.5rem 1rem;
  background: #E11D48;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.clear-btn:hover {
  background: #BE123C;
  transform: translateY(-2px);
}

.clear-btn:active {
  transform: scale(0.98);
}

.images-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-item {
  position: relative;
  background: rgba(249, 250, 251, 0.8);
  border-radius: 0.75rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
}

.image-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 0.375rem;
}

.image-info {
  flex: 1;
  min-width: 0;
}

.image-name {
  display: block;
  font-size: 0.9rem;
  color: #18181B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-size {
  font-size: 0.8rem;
  color: #94A3B8;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  background: #E11D48;
  color: #F9FAFB;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 24px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.remove-btn:hover {
  transform: translateY(-1px);
  background: #BE123C;
}

.compression-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.option-group {
  background: rgba(249, 250, 251, 0.8);
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
}

.option-label {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: #18181B;
  margin-bottom: 1rem;
}

.quality-slider {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: #E2E8F0;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3B82F6;
  cursor: pointer;
}

.quality-value {
  font-weight: 700;
  color: #3B82F6;
  min-width: 50px;
  text-align: right;
}

.format-buttons {
  display: flex;
  gap: 0.5rem;
}

.format-btn {
  flex: 1;
  padding: 0.8rem;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 700;
  color: #71717A;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.format-btn:hover {
  border-color: #3B82F6;
  transform: translateY(-2px);
}

.format-btn:active {
  transform: scale(0.98);
}

.format-btn.active {
  background: #3B82F6;
  border-color: #3B82F6;
  color: #F9FAFB;
}

.error-message {
  background: rgba(225, 29, 72, 0.08);
  color: #BE123C;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  text-align: center;
  border: 1px solid rgba(225, 29, 72, 0.2);
}

.compress-btn {
  width: 100%;
  padding: 1rem;
  background: #3B82F6;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.compress-btn:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
}

.compress-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.compress-btn:disabled {
  background: #D4D4D8;
  cursor: not-allowed;
  transform: none;
}

.results-section {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-header h3 {
  font-size: 1.3rem;
  color: #18181B;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.download-all-btn {
  padding: 0.8rem 1.5rem;
  background: #3B82F6;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 700;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.download-all-btn:hover {
  background: #2563EB;
  transform: translateY(-2px);
}

.download-all-btn:active {
  transform: scale(0.98);
}

.results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.result-item {
  background: rgba(249, 250, 251, 0.8);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  border: 1px solid rgba(226, 232, 240, 0.5);
}

.result-thumbnail {
  width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: 0.375rem;
}

.result-info {
  width: 100%;
  text-align: center;
}

.result-name {
  display: block;
  font-size: 0.9rem;
  color: #18181B;
  margin-bottom: 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-size {
  font-size: 0.8rem;
  color: #10B981;
  font-weight: 700;
}

.download-btn {
  width: 100%;
  padding: 0.6rem;
  background: #10B981;
  color: #F9FAFB;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-weight: 700;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.download-btn:hover {
  background: #059669;
  transform: translateY(-2px);
}

.download-btn:active {
  transform: scale(0.98);
}

.coming-soon {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur-xl;
  border-radius: 1.25rem;
}

.coming-soon-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.coming-soon h3 {
  font-size: 1.8rem;
  color: #18181B;
  margin-bottom: 0.5rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.coming-soon p {
  color: #71717A;
  font-size: 1.1rem;
  line-height: 1.65;
}

/* 今日运势样式 */
.diviation-result {
  margin-top: 2rem;
}

.diviation-content {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  align-items: flex-start;
}

.diviation-image {
  flex: 1;
  max-width: 50%;
}

.fate-image {
  width: 100%;
  height: auto;
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.diviation-text {
  flex: 1;
  max-width: 50%;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1.25rem;
  backdrop-filter: blur-xl;
  border: 1px solid rgba(226, 232, 240, 0.5);
}

.diviation-text h3 {
  font-size: 1.5rem;
  color: #18181B;
  margin-bottom: 1rem;
  text-align: center;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.fate-text {
  font-size: 1.1rem;
  line-height: 1.65;
  color: #71717A;
  margin-bottom: 1.5rem;
  text-align: center;
}

.user-id {
  font-size: 0.9rem;
  color: #94A3B8;
  text-align: center;
}

.diviation-placeholder {
  text-align: center;
  padding: 3rem;
  color: #71717A;
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 1.25rem;
  backdrop-filter: blur-xl;
  border: 1px solid rgba(226, 232, 240, 0.5);
  line-height: 1.65;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #71717A;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .tools-page {
    padding: 1rem;
  }

  .tools-header h1 {
    font-size: 1.8rem;
  }

  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .tool-card {
    padding: 1.5rem;
  }

  .diviation-content {
    flex-direction: column;
  }

  .diviation-image,
  .diviation-text {
    max-width: 100%;
  }
}
</style>