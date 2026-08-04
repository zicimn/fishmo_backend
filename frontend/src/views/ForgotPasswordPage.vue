<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/user'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const code = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)
const sendingCode = ref(false)
const codeSent = ref(false)
const countdown = ref(0)
let countdownInterval: number | undefined

onMounted(() => {
  // 确保loading状态初始化为false
  loading.value = false
  console.log('页面加载完成，loading状态:', loading.value)
})

const handleSendCode = async () => {
  if (!email.value) {
    error.value = '请输入邮箱'
    return
  }

  sendingCode.value = true
  error.value = ''

  try {
    await userApi.sendCode(email.value)
    codeSent.value = true
    startCountdown()
  } catch (err: unknown) {
    error.value = '发送验证码失败，请检查邮箱是否正确'
    console.error(err)
  } finally {
    sendingCode.value = false
  }
}

const startCountdown = () => {
  countdown.value = 60
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  countdownInterval = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownInterval)
    }
  }, 1000)
}

const handleResetPassword = async () => {
  if (!email.value || !password.value || !code.value) {
    error.value = '请填写所有字段'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''
  console.log('开始重置密码，loading状态:', loading.value)

  try {
    await userApi.retrieve(email.value, password.value, code.value)
    success.value = '密码重置成功，请登录'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: unknown) {
    error.value = '密码重置失败，请检查验证码是否正确'
    console.error('重置密码错误:', err)
  } finally {
    loading.value = false
    console.log('重置密码完成，loading状态:', loading.value)
  }
}
</script>

<template>
  <div class="forgot-password-page">
    <div class="glass-card">
      <h1>忘记密码</h1>
      <form @submit.prevent="handleResetPassword" class="forgot-password-form">
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
          <label for="code">验证码</label>
          <div class="code-input">
            <input
              type="text"
              id="code"
              v-model="code"
              required
              :disabled="loading"
            />
            <button
              type="button"
              class="send-code-button"
              :disabled="sendingCode || loading || countdown > 0"
              @click="handleSendCode"
            >
              {{ sendingCode ? '发送中...' : countdown > 0 ? `${countdown}秒后重发` : '发送验证码' }}
            </button>
          </div>
        </div>
        <div class="form-group">
          <label for="password">新密码</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            :disabled="loading"
          />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="success" class="success">{{ success }}</div>
        <button type="submit" class="reset-button" :disabled="loading">
          {{ loading ? '重置中...' : '重置密码' }}
        </button>
        <div class="login-link">
          想起密码了？ <router-link to="/login">登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.forgot-password-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.65;
}

.glass-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.5);
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #18181B;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.forgot-password-form {
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
  font-weight: 600;
  color: #18181B;
  font-size: 0.875rem;
}

input {
  padding: 0.75rem 1rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  color: #18181B;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: inherit;
  line-height: 1.65;
}

input:focus {
  outline: none;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

input::placeholder {
  color: #94A3B8;
}

.code-input {
  display: flex;
  gap: 0.5rem;
}

.code-input input {
  flex: 1;
}

.send-code-button {
  padding: 0.75rem 1rem;
  background: #3B82F6;
  backdrop-filter: blur(20px);
  color: #F9FAFB;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
  font-family: inherit;
  line-height: 1.65;
}

.send-code-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
}

.send-code-button:active:not(:disabled) {
  transform: scale(0.98);
}

.send-code-button:disabled {
  background: #94A3B8;
  border-color: rgba(148, 163, 184, 0.3);
  cursor: not-allowed;
  opacity: 0.7;
}

.error {
  color: #E11D48;
  text-align: center;
  padding: 0.75rem 1rem;
  background: rgba(225, 29, 72, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 0.5rem;
  border: 1px solid rgba(225, 29, 72, 0.2);
  font-size: 0.875rem;
  font-weight: 500;
}

.success {
  color: #10B981;
  text-align: center;
  padding: 0.75rem 1rem;
  background: rgba(16, 185, 129, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 0.5rem;
  border: 1px solid rgba(16, 185, 129, 0.2);
  font-size: 0.875rem;
  font-weight: 500;
}

.reset-button {
  padding: 0.75rem 1rem;
  background: #3B82F6;
  backdrop-filter: blur(20px);
  color: #F9FAFB;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  font-family: inherit;
  line-height: 1.65;
}

.reset-button:hover:not(:disabled) {
  background: #2563EB;
  transform: translateY(-2px);
}

.reset-button:active:not(:disabled) {
  transform: scale(0.98);
}

.reset-button:disabled {
  background: #94A3B8;
  border-color: rgba(148, 163, 184, 0.3);
  cursor: not-allowed;
  opacity: 0.7;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  color: #71717A;
  font-size: 0.9375rem;
}

.login-link a {
  color: #3B82F6;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-link a:hover {
  color: #2563EB;
  text-decoration: underline;
}
</style>
