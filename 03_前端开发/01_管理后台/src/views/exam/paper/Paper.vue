<template>
  <div class="paper-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试卷管理</span>
          <el-button type="primary" @click="handleAdd">新增试卷</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="试卷名称" min-width="180" />
        <el-table-column prop="subject_name" label="科目" width="120" />
        <el-table-column prop="question_count" label="题目数" width="100" />
        <el-table-column prop="total_score" label="总分" width="80" />
        <el-table-column prop="duration" label="时长(分钟)" width="100" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="试卷名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="科目" prop="subject">
          <el-select v-model="form.subject">
            <el-option v-for="item in subjects" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长" prop="duration">
          <el-input-number v-model="form.duration" :min="10" :max="300" />
        </el-form-item>
        <el-form-item label="题目" prop="question_ids">
          <el-select v-model="form.question_ids" multiple filterable style="width: 100%">
            <el-option v-for="item in filteredQuestions" :key="item.id" :label="`${item.id} - ${item.content}`" :value="item.id" />
          </el-select>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'

const loading = ref(false)
const tableData = ref([])
const subjects = ref([])
const questions = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增试卷')
const formRef = ref()

const form = reactive({ id: null, name: '', subject: null, duration: 90, question_ids: [], status: 'draft' })

const rules = {
  name: [{ required: true, message: '请输入试卷名称', trigger: 'blur' }],
  subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
  question_ids: [{ required: true, message: '请选择题目', trigger: 'change' }]
}

const filteredQuestions = computed(() => {
  if (!form.subject) return questions.value
  return questions.value.filter(item => item.subject === form.subject)
})

async function fetchOptions() {
  const [subjectRes, questionRes] = await Promise.all([
    api.get('/edu/subjects/'),
    api.get('/exam/questions/')
  ])
  subjects.value = subjectRes.data.results || subjectRes.data
  questions.value = questionRes.data.results || questionRes.data
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/exam/papers/')
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取试卷失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '新增试卷'
  Object.assign(form, { id: null, name: '', subject: null, duration: 90, question_ids: [], status: 'draft' })
  dialogVisible.value = true
}

async function handleEdit(row) {
  dialogTitle.value = '编辑试卷'
  const detail = await api.get(`/exam/papers/${row.id}/`)
  Object.assign(form, {
    id: row.id,
    name: row.name,
    subject: row.subject,
    duration: row.duration,
    question_ids: detail.data.questions?.map(item => item.id) || [],
    status: row.status
  })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定删除该试卷吗？', '提示', { type: 'warning' })
    await api.delete(`/exam/papers/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    const payload = { ...form }
    if (form.id) {
      await api.put(`/exam/papers/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/exam/papers/', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    const data = e.response?.data
    const message = data?.question_ids?.[0] || data?.name?.[0] || '保存试卷失败'
    ElMessage.error(message)
  }
}

onMounted(async () => {
  await fetchOptions()
  await fetchData()
})
</script>

<style scoped>
.paper-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
