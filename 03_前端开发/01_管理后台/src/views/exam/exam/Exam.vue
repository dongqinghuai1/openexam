<template>
  <div class="exam-page page-shell">
    <el-card class="surface-card">
      <template #header>
        <div class="card-header">
          <div>
            <div class="page-title">考试管理</div>
            <div class="page-subtitle">安排班级考试、试卷分配与成绩查看入口。</div>
          </div>
          <el-button type="primary" @click="handleAdd">新增考试</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="考试名称" min-width="180" />
        <el-table-column prop="paper_name" label="试卷" min-width="180" />
        <el-table-column prop="class_name" label="班级" min-width="160" />
        <el-table-column prop="subject_name" label="科目" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="220" class-name="operation-column">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handlePublish(row)">发布</el-button>
            <el-button type="info" link @click="handleScores(row)">成绩</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="680px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="考试名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="试卷" prop="paper">
          <el-select v-model="form.paper">
            <el-option v-for="item in papers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" prop="edu_class">
          <el-select v-model="form.edu_class">
            <el-option v-for="item in classes" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
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
import { useRouter } from 'vue-router'
import { extractErrorMessage } from '@/utils/error'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const papers = ref([])
const classes = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增考试')
const formRef = ref()

const form = reactive({ id: null, name: '', paper: null, edu_class: null, start_time: '', end_time: '', status: 'pending' })

const rules = {
  name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  paper: [{ required: true, message: '请选择试卷', trigger: 'change' }],
  edu_class: [{ required: true, message: '请选择班级', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

async function fetchOptions() {
  const [paperRes, classRes] = await Promise.all([
    api.get('/exam/papers/'),
    api.get('/edu/classes/')
  ])
  papers.value = paperRes.data.results || paperRes.data
  classes.value = classRes.data.results || classRes.data
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/exam/exams/')
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取考试失败'))
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '新增考试'
  Object.assign(form, { id: null, name: '', paper: null, edu_class: null, start_time: '', end_time: '', status: 'pending' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑考试'
  Object.assign(form, { ...row, paper: row.paper?.id || row.paper, edu_class: row.edu_class?.id || row.edu_class })
  dialogVisible.value = true
}

async function handlePublish(row) {
  try {
    await api.post(`/exam/exams/${row.id}/publish/`)
    ElMessage.success('发布成功')
    fetchData()
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '发布考试失败'))
  }
}

function handleScores(row) {
  router.push({ path: '/exam/scores', query: { exam: row.id } })
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该考试吗？', '提示', { type: 'warning' })
    await api.delete(`/exam/exams/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '删除考试失败'))
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    if (form.id) {
      await api.put(`/exam/exams/${form.id}/`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/exam/exams/', form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    const data = e.response?.data
    const message = data?.end_time?.[0] || data?.name?.[0] || '保存考试失败'
    ElMessage.error(message)
  }
}

onMounted(async () => {
  await fetchOptions()
  await fetchData()
})
</script>

<style scoped>
.exam-page { padding: 20px; }
</style>
