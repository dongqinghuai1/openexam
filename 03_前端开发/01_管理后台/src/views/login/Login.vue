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

      <div class="auth-links">
        <span @click="registerVisible = true">用户注册</span>
        <span @click="resetVisible = true">忘记密码</span>
      </div>
    </section>

    <el-dialog v-model="registerVisible" title="用户注册" width="520px">
        <el-form :model="registerForm" label-width="92px">
        <el-form-item label="用户名"><el-input v-model="registerForm.username" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="registerForm.email" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="registerForm.phone" /></el-form-item>
        <el-form-item label="验证码">
          <div class="sms-row">
            <el-input v-model="registerForm.verify_code" />
            <el-button @click="sendSmsCode('register')">发送验证码</el-button>
          </div>
        </el-form-item>
        <el-form-item label="密码"><el-input v-model="registerForm.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="registerForm.role" style="width: 100%">
            <el-option label="学生" value="student" />
            <el-option label="家长" value="parent" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="registerForm.name" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'student'" label="年级"><el-input v-model="registerForm.grade" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'student'" label="学校"><el-input v-model="registerForm.school" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'student'" label="家长姓名"><el-input v-model="registerForm.parent_name" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'student'" label="家长手机"><el-input v-model="registerForm.parent_phone" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'teacher'" label="学历"><el-input v-model="registerForm.education" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'teacher'" label="专业"><el-input v-model="registerForm.major" /></el-form-item>
        <el-form-item v-if="registerForm.role === 'teacher'" label="证书"><el-input v-model="registerForm.certification" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRegister">提交注册</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetVisible" title="重置密码" width="460px">
      <el-form :model="resetForm" label-width="92px">
        <el-form-item label="邮箱"><el-input v-model="resetForm.email" /></el-form-item>
        <el-form-item label="验证码">
          <div class="sms-row">
            <el-input v-model="resetForm.verify_code" />
            <el-button @click="sendSmsCode('reset_password')">发送验证码</el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码"><el-input v-model="resetForm.new_password" type="password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">重置密码</el-button>
      </template>
    </el-dialog>

    <footer class="login-footer">© 2025 OPENEXAM</footer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api, useUserStore } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)
const registerVisible = ref(false)
const resetVisible = ref(false)
const teacherPortalUrl = import.meta.env.VITE_TEACHER_PORTAL_URL || 'http://127.0.0.1:3001'
const studentPortalUrl = import.meta.env.VITE_STUDENT_PORTAL_URL || 'http://127.0.0.1:3002'
const parentPortalUrl = import.meta.env.VITE_PARENT_PORTAL_URL || 'http://127.0.0.1:3003'

const form = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  phone: '',
  verify_code: '',
  password: '',
  role: 'student',
  name: '',
  grade: '',
  school: '',
  parent_name: '',
  parent_phone: '',
  education: '',
  major: '',
  certification: ''
})

const resetForm = reactive({
  email: '',
  verify_code: '',
  new_password: ''
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
    const result = await userStore.login(form.username, form.password)
    const roleCodes = (result.user?.roles || []).map(item => item.code)
    if (!result.user?.is_superuser && !roleCodes.includes('admin')) {
      const payload = new URLSearchParams({
        token: result.token,
        refresh_token: result.refresh_token,
        user: encodeURIComponent(JSON.stringify(result.user))
      }).toString()

      if (roleCodes.includes('teacher') && teacherPortalUrl) {
        window.location.href = `${teacherPortalUrl}${teacherPortalUrl.includes('?') ? '&' : '?'}${payload}`
        return
      }
      if (roleCodes.includes('student') && studentPortalUrl) {
        window.location.href = `${studentPortalUrl}${studentPortalUrl.includes('?') ? '&' : '?'}${payload}`
        return
      }
      if (roleCodes.includes('parent') && parentPortalUrl) {
        window.location.href = `${parentPortalUrl}${parentPortalUrl.includes('?') ? '&' : '?'}${payload}`
        return
      }

      await userStore.logout()
      ElMessage.error('当前账号不是管理员，请使用对应用户端登录，且需先配置对应端入口地址')
      return
    }
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(extractErrorMessage(error, '登录失败'))
  } finally {
    loading.value = false
  }
}

async function sendSmsCode(scene) {
  const email = scene === 'register' ? registerForm.email : resetForm.email
  if (!email) {
    ElMessage.warning('请先输入邮箱')
    return
  }
  try {
    await api.post('/users/sms/send/', { email, scene })
    ElMessage.success('验证码已发送')
  } catch (error) {
    ElMessage.error(extractErrorMessage(error, '发送验证码失败'))
  }
}

async function handleRegister() {
  try {
    const payload = { ...registerForm }
    await api.post('/users/register/', payload)
    ElMessage.success(registerForm.role === 'teacher' ? '注册成功，等待审核' : '注册成功，请登录')
    registerVisible.value = false
  } catch (error) {
    ElMessage.error(extractErrorMessage(error, '注册失败'))
  }
}

async function handleResetPassword() {
  try {
    await api.post('/users/reset-password/', resetForm)
    ElMessage.success('密码重置成功，请重新登录')
    resetVisible.value = false
  } catch (error) {
    ElMessage.error(extractErrorMessage(error, '重置密码失败'))
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

.auth-links {
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: rgba(250, 250, 250, 0.7);
}

.auth-links span {
  cursor: pointer;
}

.sms-row {
  display: flex;
  gap: 10px;
  width: 100%;
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
