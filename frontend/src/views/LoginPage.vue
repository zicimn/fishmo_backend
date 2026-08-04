<script setup lang="ts">
import { ref } from 'vue'
import { userApi } from '@/api/user'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await userApi.login({ username: username.value, password: password.value })
    console.log('登录响应:', response)
    userStore.login(response.data)
    router.push('/')
  } catch (err: unknown) {
    error.value = '登录失败，请检查您的凭据'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-form-container">
      <h1>登录</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            :disabled="loading"
          />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" class="login-button" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <div class="register-link">
          还没有账户？ <router-link to="/register">注册</router-link>
        </div>
        <div class="forgot-password-link">
          <router-link to="/forgot-password">忘记密码？</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.login-form-container {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.5);
  padding: 2rem;
  max-width: 400px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #18181B;
  font-size: 1.8rem;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.login-form {
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

input {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(24px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem;
  background: rgba(225, 29, 72, 0.1);
  backdrop-filter: blur(24px);
  border-radius: 0.5rem;
  border: 1px solid rgba(225, 29, 72, 0.3);
}

.login-button {
  padding: 0.75rem 1.5rem;
  background: #3B82F6;
  backdrop-filter: blur(24px);
  color: #F9FAFB;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: bold;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.login-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.login-button:disabled {
  background: rgba(148, 163, 184, 0.6);
  cursor: not-allowed;
}

.login-button:active:not(:disabled) {
  transform: scale(0.98);
}

.register-link {
  text-align: center;
  margin-top: 1rem;
  color: #71717A;
}

.register-link a {
  color: #3B82F6;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.register-link a:hover {
  text-decoration: underline;
  color: #2563EB;
}

.forgot-password-link {
  text-align: center;
  margin-top: 0.5rem;
  color: #71717A;
}

.forgot-password-link a {
  color: #3B82F6;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.forgot-password-link a:hover {
  text-decoration: underline;
  color: #2563EB;
}
</style>
