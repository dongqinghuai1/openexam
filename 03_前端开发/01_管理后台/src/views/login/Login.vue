<template>
  <div class="login-container">
    <div class="login-grid">
      <section class="login-brand">
        <div class="brand-chip">EduAdmin</div>
        <h1>清晰、安静、克制的教务与运营中控台。</h1>
        <p>以白色为基底，用节制的层次、柔和的边界和高密度信息组织，把系统做成更接近 Apple 式的产品体验，而不是传统后台模板。</p>
        <div class="brand-meta">
          <div class="meta-card">
            <span>核心场景</span>
            <strong>教务、课堂、考试、财务四条主链已打通</strong>
          </div>
          <div class="meta-card">
            <span>体验目标</span>
            <strong>让复杂流程看起来像一个安静、可靠的系统</strong>
          </div>
        </div>
      </section>

      <section class="login-box">
        <div class="login-head">
          <div class="eyebrow">Secure Access</div>
          <h2>登录控制台</h2>
          <p>建议统一使用 `127.0.0.1:3000` 访问，避免本地存储跨 host 不共享。</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">进入系统</el-button>
          </el-form-item>
        </el-form>

        <div class="login-tips">
          <span>默认账号</span>
          <strong>admin / admin123</strong>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form.username, form.password)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: grid;
  place-items: center;
  padding: 48px;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.08), transparent 24%),
    radial-gradient(circle at bottom right, rgba(255, 255, 255, 0.92), transparent 26%),
    linear-gradient(180deg, #f8f9fb 0%, #f1f3f5 100%);
}

.login-grid {
  width: min(1180px, 100%);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 28px;
}

.login-brand,
.login-box {
  position: relative;
  overflow: hidden;
  padding: 42px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(24px);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.08);
}

.login-brand::before,
.login-box::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.7), transparent 46%);
  pointer-events: none;
}

.brand-chip,
.eyebrow {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  letter-spacing: 0.16em;
  font-size: 12px;
  color: #0071e3;
  background: rgba(0, 113, 227, 0.08);
  border: 1px solid rgba(0, 113, 227, 0.12);
}

.login-brand h1 {
  margin-top: 26px;
  max-width: 680px;
  font-size: clamp(38px, 5vw, 72px);
  line-height: 1.02;
  font-weight: 700;
  color: #111827;
}

.login-brand p {
  margin-top: 18px;
  max-width: 560px;
  font-size: 18px;
  line-height: 1.8;
  color: #6b7280;
}

.brand-meta {
  display: grid;
  gap: 14px;
  margin-top: 34px;
}

.meta-card {
  padding: 18px 20px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.94);
  border: 1px solid rgba(15, 23, 42, 0.06);
}

.meta-card span {
  display: block;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #94a3b8;
}

.meta-card strong {
  display: block;
  margin-top: 8px;
  font-size: 18px;
  color: #111827;
  font-weight: 600;
}

.login-head h2 {
  margin-top: 20px;
  font-size: 34px;
  color: #111827;
}

.login-head p {
  margin-top: 12px;
  color: #6b7280;
  line-height: 1.8;
}

.login-form {
  margin-top: 28px;
}

.login-btn {
  width: 100%;
  min-height: 48px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-tips {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(247, 248, 250, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.06);
}

.login-tips span {
  display: block;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #94a3b8;
}

.login-tips strong {
  display: block;
  margin-top: 8px;
  color: #111827;
  font-size: 18px;
}

@media (max-width: 980px) {
  .login-container {
    padding: 20px;
  }

  .login-grid {
    grid-template-columns: 1fr;
  }

  .login-brand,
  .login-box {
    padding: 26px;
  }
}
</style>
