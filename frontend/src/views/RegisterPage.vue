<script setup lang="ts">
import { ref } from 'vue'
import { userApi } from '@/api/user'
import { useRouter } from 'vue-router'

const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const code = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)
const countdown = ref(0)
const timer = ref<number | null>(null)

const startCountdown = () => {
  countdown.value = 60
  timer.value = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(timer.value!)
    }
  }, 1000)
}

const handleSendCode = async () => {
  if (!email.value) {
    error.value = '请输入您的邮箱'
    return
  }

  try {
    await userApi.sendCode(email.value)
    success.value = '验证码发送成功'
    startCountdown()
  } catch (err: unknown) {
    error.value = '发送验证码失败'
    console.error(err)
  }
}

const handleRegister = async () => {
  if (!name.value || !email.value || !password.value || !confirmPassword.value || !code.value) {
    error.value = '请填写所有字段'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = '密码不匹配'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    await userApi.register({ name: name.value, email: email.value, password: password.value, code: code.value })
    success.value = '注册成功！请登录。'
    // 跳转到登录页面
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: unknown) {
    error.value = '注册失败，请重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-form-container">
      <h1>注册</h1>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="name">用户名</label>
          <input
            type="text"
            id="name"
            v-model="name"
            required
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            id="email"
            v-model="email"
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
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="confirmPassword"
            required
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label for="code">验证码</label>
          <div class="code-input-container">
            <input
              type="text"
              id="code"
              v-model="code"
              required
              :disabled="loading"
              placeholder="请输入验证码"
            />
            <button
              type="button"
              class="send-code-button"
              @click="handleSendCode"
              :disabled="loading || countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}秒` : '发送验证码' }}
            </button>
          </div>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="success" class="success">{{ success }}</div>
        <button type="submit" class="register-button" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <div class="login-link">
          已经有账户？ <router-link to="/login">登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem;
}

.register-form-container {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
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
  font-weight: 700;
  letter-spacing: -0.025em;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.code-input-container {
  display: flex;
  gap: 1rem;
}

.code-input-container input {
  flex: 1;
}

.send-code-button {
  padding: 0.75rem 1rem;
  background: #3B82F6;
  backdrop-filter: blur(12px);
  color: #F9FAFB;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.send-code-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px -3px rgba(59, 130, 246, 0.3);
}

.send-code-button:disabled {
  background: #94A3B8;
  cursor: not-allowed;
  transform: none;
}

label {
  font-weight: 600;
  color: #18181B;
  font-size: 0.875rem;
}

input {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  color: #18181B;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.65;
}

input::placeholder {
  color: #94A3B8;
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
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(12px);
  border-radius: 0.5rem;
  border: 1px solid rgba(225, 29, 72, 0.2);
  font-size: 0.875rem;
}

.success {
  color: #10B981;
  text-align: center;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  backdrop-filter: blur(12px);
  border-radius: 0.5rem;
  border: 1px solid rgba(16, 185, 129, 0.2);
  font-size: 0.875rem;
}

.register-button {
  padding: 0.75rem 1.5rem;
  background: #3B82F6;
  backdrop-filter: blur(12px);
  color: #F9FAFB;
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.register-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px -3px rgba(59, 130, 246, 0.3);
}

.register-button:disabled {
  background: #94A3B8;
  cursor: not-allowed;
  transform: none;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  color: #71717A;
  font-size: 0.9rem;
}

.login-link a {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-link a:hover {
  text-decoration: underline;
  color: #2563EB;
}
</style>
