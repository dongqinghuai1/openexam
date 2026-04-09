<template>
  <div class="notification-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通知消息</span>
          <el-button type="primary" @click="handleAdd">新增通知</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="level" label="级别" width="100" />
        <el-table-column prop="target_type" label="发送对象" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="creator_name" label="创建人" width="100" />
        <el-table-column prop="published_at" label="发布时间" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" type="success" link @click="handlePublish(row)">发布</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="标题" prop="title"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="级别" prop="level">
          <el-select v-model="form.level">
            <el-option label="普通" value="info" />
            <el-option label="提醒" value="warning" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="发送对象" prop="target_type">
          <el-select v-model="form.target_type">
            <el-option label="全体" value="all" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
            <el-option label="家长" value="parent" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content"><el-input v-model="form.content" type="textarea" :rows="5" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增通知')
const formRef = ref()
const form = reactive({ id: null, title: '', content: '', level: 'info', target_type: 'all', status: 'draft' })

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  level: [{ required: true, message: '请选择级别', trigger: 'change' }],
  target_type: [{ required: true, message: '请选择发送对象', trigger: 'change' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/users/notifications/')
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取通知列表失败'))
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '新增通知'
  Object.assign(form, { id: null, title: '', content: '', level: 'info', target_type: 'all', status: 'draft' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑通知'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

async function handlePublish(row) {
  try {
    await api.post(`/users/notifications/${row.id}/publish/`)
    ElMessage.success('通知已发布')
    fetchData()
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '发布通知失败'))
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除通知 "${row.title}" 吗?`, '提示', { type: 'warning' })
    await api.delete(`/users/notifications/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '删除通知失败'))
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (form.id) {
      await api.put(`/users/notifications/${form.id}/`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/users/notifications/', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '保存通知失败'))
  }
}

onMounted(fetchData)
</script>

<style scoped>
.notification-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
