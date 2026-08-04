<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/user'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const newUsername = ref('')
const newEmail = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const newBio = ref('')

const error = ref('')
const success = ref('')
const loading = ref(false)

// 头像相关
const avatarUrl = ref('/upload/avatars/default_avatar.webp')
const avatarInput = ref<HTMLInputElement | null>(null)
const avatarLoading = ref(false)

const loadAvatar = async () => {
  try {
    const response = await userApi.getInfo()
    if (response.data && response.data.avatar) {
      avatarUrl.value = response.data.avatar + '?t=' + new Date().getTime()
    }
  } catch (err) {
    console.error('获取头像失败:', err)
  }
}

const handleAvatarChange = () => {
  if (avatarInput.value) {
    avatarInput.value.click()
  }
}

const handleAvatarFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) {
    return
  }

  // 检查文件大小（不超过5MB）
  if (file.size > 5 * 1024 * 1024) {
    error.value = '头像文件大小不能超过5MB'
    return
  }

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件'
    return
  }

  avatarLoading.value = true
  error.value = ''

  try {
    // 将图片转换为 base64 格式
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64Data = e.target?.result as string
      if (!base64Data) {
        error.value = '图片读取失败'
        avatarLoading.value = false
        return
      }

      try {
        const response = await userApi.updateAvatar(base64Data)
        if (response.data && response.data.user && response.data.user.avatar) {
          avatarUrl.value = response.data.user.avatar + '?t=' + new Date().getTime()
          success.value = '头像更新成功'
        }
      } catch (err: unknown) {
        error.value = '更新头像失败'
        console.error('更新头像失败:', err)
      } finally {
        avatarLoading.value = false
      }
    }
    reader.onerror = () => {
      error.value = '图片读取失败'
      avatarLoading.value = false
    }
    reader.readAsDataURL(file)
  } catch (err: unknown) {
    error.value = '更新头像失败'
    console.error('更新头像失败:', err)
    avatarLoading.value = false
  }
}

const handleUpdate = async () => {
  if (newPassword.value && newPassword.value !== confirmPassword.value) {
    error.value = '新密码不匹配'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
      const data = {
        new_username: newUsername.value || undefined,
        new_email: newEmail.value || undefined,
        new_password: newPassword.value || undefined,
        new_bio: newBio.value || undefined
      }
      console.log('发送的更新数据:', data)
      const response = await userApi.update(data)
      console.log('后端返回的响应:', response)
      console.log('响应数据:', response.data)
      success.value = '资料更新成功'
      // 重新登录以更新用户信息
      if (newUsername.value) {
        userStore.username = newUsername.value
      }
    } catch (err: unknown) {
      console.error('更新资料失败:', err)
      error.value = '更新资料失败'
    } finally {
      loading.value = false
    }
}

const handleDeleteAccount = async () => {
  if (!confirm('您确定要删除您的账户吗？此操作不可撤销。')) {
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await userApi.delete(true)
    userStore.logout()
    router.push('/')
  } catch (err: unknown) {
    error.value = '删除账户失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAvatar()
})
</script>

<template>
  <div class="user-profile">
    <div class="profile-header">
      <h1>用户中心</h1>

      <!-- 头像显示和更换按钮 -->
      <div class="avatar-container">
        <div class="avatar-wrapper">
          <img
            :src="avatarUrl"
            alt="头像"
            class="avatar"
            :class="{ 'loading': avatarLoading }"
          />
          <div class="avatar-overlay" @click="handleAvatarChange" v-if="!avatarLoading">
            <span class="change-avatar-text">更换头像</span>
          </div>
          <div v-if="avatarLoading" class="avatar-loading-overlay">
            <span class="loading-text">上传中...</span>
          </div>
        </div>
        <input
          ref="avatarInput"
          type="file"
          accept="image/*"
          style="display: none;"
          @change="handleAvatarFileSelect"
        />
        <p class="avatar-hint">点击头像更换（支持 jpg、png、webp，大小不超过5MB）</p>
      </div>
    </div>

    <div class="profile-form">
      <h2>更新资料</h2>
      <form @submit.prevent="handleUpdate" class="update-form">
        <div class="form-group">
          <label for="newUsername">新用户名（可选）</label>
          <input
            type="text"
            id="newUsername"
            v-model="newUsername"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="newEmail">新邮箱（可选）</label>
          <input
            type="email"
            id="newEmail"
            v-model="newEmail"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="newPassword">新密码（可选）</label>
          <input
            type="password"
            id="newPassword"
            v-model="newPassword"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认新密码</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="newBio">个人简介（可选）</label>
          <textarea
            id="newBio"
            v-model="newBio"
            rows="4"
            :disabled="loading"
          ></textarea>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="success" class="success">{{ success }}</div>
        <button type="submit" class="update-button" :disabled="loading">
          {{ loading ? '更新中...' : '更新资料' }}
        </button>
      </form>
    </div>

    <div class="delete-account">
      <h2>删除账户</h2>
      <p>警告：此操作不可撤销。您的账户和所有相关数据将被永久删除。</p>
      <button
        class="delete-button"
        @click="handleDeleteAccount"
        :disabled="loading"
      >
        {{ loading ? '处理中...' : '删除账户' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.user-profile {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.65;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-header h1 {
  margin-bottom: 1rem;
  text-align: center;
  color: #18181B;
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* 头像容器 */
.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.avatar-wrapper {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.avatar-wrapper:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.avatar.loading {
  opacity: 0.5;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.change-avatar-text {
  color: #F9FAFB;
  font-size: 0.875rem;
  font-weight: bold;
}

.avatar-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-text {
  color: #F9FAFB;
  font-size: 0.875rem;
}

.avatar-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94A3B8;
}

h2 {
  margin-bottom: 1.5rem;
  color: #18181B;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.profile-form,
.delete-account {
  max-width: 500px;
  margin: 0 auto 2rem;
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.update-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
  color: #18181B;
}

input,
textarea {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.1);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 0.5rem;
  border: 1px solid rgba(225, 29, 72, 0.3);
}

.success {
  color: #10B981;
  text-align: center;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 0.5rem;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.update-button {
  padding: 0.75rem 1.5rem;
  background: #3B82F6;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  color: #F9FAFB;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.update-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
}

.update-button:active:not(:disabled) {
  transform: scale(0.98);
}

.update-button:disabled {
  background: rgba(161, 161, 170, 0.6);
  cursor: not-allowed;
}

.delete-account p {
  margin-bottom: 1.5rem;
  color: #71717A;
}

.delete-button {
  padding: 0.75rem 1.5rem;
  background: #E11D48;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  color: #F9FAFB;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

.delete-button:hover:not(:disabled) {
  background: #BE123C;
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.1);
}

.delete-button:active:not(:disabled) {
  transform: scale(0.98);
}

.delete-button:disabled {
  background: rgba(161, 161, 170, 0.6);
  cursor: not-allowed;
}
</style>
