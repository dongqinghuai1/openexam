<template>
  <div class="login-container">
    <div class="login-orb login-orb-left"></div>
    <div class="login-orb login-orb-right"></div>

    <section class="login-shell">
      <div class="brand-mark">OX</div>
      <h1>OPENEXAM</h1>
      <p>登录到 OPENEXAM</p>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </section>

    <footer class="login-footer">© 2025 OPENEXAM</footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

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
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(extractErrorMessage(error, '登录失败'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  min-height: 100vh;
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 24px;
  background:
    radial-gradient(circle at 20% 20%, rgba(70, 85, 255, 0.08), transparent 26%),
    radial-gradient(circle at 80% 30%, rgba(120, 76, 255, 0.07), transparent 24%),
    linear-gradient(180deg, #09090b 0%, #0a0a0a 100%);
}

.login-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(80px);
  pointer-events: none;
}

.login-orb-left {
  width: 320px;
  height: 320px;
  left: -80px;
  top: -40px;
  background: rgba(68, 97, 255, 0.12);
}

.login-orb-right {
  width: 300px;
  height: 300px;
  right: -60px;
  bottom: -20px;
  background: rgba(139, 92, 246, 0.1);
}

.login-shell {
  position: relative;
  z-index: 1;
  width: min(100%, 400px);
  padding: 34px 30px 26px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(20px);
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(250, 250, 250, 0.96), rgba(214, 214, 214, 0.92));
  color: #09090b;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.login-shell h1 {
  margin-top: 22px;
  text-align: center;
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: #fafafa;
}

.login-shell p {
  margin-top: 8px;
  text-align: center;
  font-size: 14px;
  color: rgba(250, 250, 250, 0.65);
}

.login-form {
  margin-top: 28px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.login-form :deep(.el-input__wrapper) {
  min-height: 48px;
  background: rgba(255, 255, 255, 0.05) !important;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08) inset !important;
  border-radius: 14px;
}

.login-form :deep(.el-input__inner) {
  color: #fafafa !important;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(250, 250, 250, 0.38) !important;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px rgba(250, 250, 250, 0.32) inset, 0 0 0 4px rgba(59, 130, 246, 0.08) !important;
}

.login-btn {
  width: 100%;
  min-height: 48px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.02em;
  background: #fafafa !important;
  border-color: #fafafa !important;
  color: #09090b !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 28px rgba(255, 255, 255, 0.12);
}

.login-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  letter-spacing: 0.04em;
}
</style>
