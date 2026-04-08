<template>
  <div class="question-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <el-button type="primary" @click="handleAdd">新增题目</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="科目">
          <el-select v-model="queryForm.subject" clearable>
            <el-option v-for="item in subjects" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="queryForm.type" clearable>
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="填空题" value="blank" />
            <el-option label="问答题" value="essay" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="content" label="题目内容" min-width="260" show-overflow-tooltip />
        <el-table-column prop="type" label="题型" width="100" />
        <el-table-column prop="difficulty" label="难度" width="100" />
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column prop="creator_name" label="创建人" width="100" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="科目" prop="subject">
          <el-select v-model="form.subject">
            <el-option v-for="item in subjects" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="章节">
          <el-input v-model="form.chapter" />
        </el-form-item>
        <el-form-item label="题型" prop="type">
          <el-select v-model="form.type">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="填空题" value="blank" />
            <el-option label="问答题" value="essay" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="选项">
          <el-input v-model="form.optionsText" type="textarea" :rows="4" placeholder='每行一项，例如 A. 选项一' />
        </el-form-item>
        <el-form-item label="答案" prop="answer">
          <el-input v-model="form.answer" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="form.analysis" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="form.difficulty">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="分值" prop="score">
          <el-input-number v-model="form.score" :min="1" :max="100" />
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

const loading = ref(false)
const tableData = ref([])
const subjects = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增题目')
const formRef = ref()

const queryForm = reactive({ subject: '', type: '' })
const form = reactive({
  id: null,
  subject: null,
  chapter: '',
  type: 'single',
  content: '',
  optionsText: '',
  answer: '',
  analysis: '',
  difficulty: 'medium',
  score: 5,
  status: true
})

const rules = {
  subject: [{ required: true, message: '请选择科目', trigger: 'change' }],
  type: [{ required: true, message: '请选择题型', trigger: 'change' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  answer: [{ required: true, message: '请输入答案', trigger: 'blur' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }]
}

function parseOptions(text) {
  const lines = text.split('\n').map(item => item.trim()).filter(Boolean)
  return lines.reduce((acc, item, index) => {
    acc[String.fromCharCode(65 + index)] = item.replace(/^[A-Z]\.?\s*/, '')
    return acc
  }, {})
}

function stringifyOptions(options) {
  if (!options || typeof options !== 'object') return ''
  return Object.entries(options).map(([key, value]) => `${key}. ${value}`).join('\n')
}

async function fetchSubjects() {
  const res = await api.get('/edu/subjects/')
  subjects.value = res.data.results || res.data
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/exam/questions/', { params: queryForm })
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取题目失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  dialogTitle.value = '新增题目'
  Object.assign(form, { id: null, subject: null, chapter: '', type: 'single', content: '', optionsText: '', answer: '', analysis: '', difficulty: 'medium', score: 5, status: true })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑题目'
  Object.assign(form, { ...row, subject: row.subject?.id || row.subject, optionsText: stringifyOptions(row.options) })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除该题目吗？`, '提示', { type: 'warning' })
    await api.delete(`/exam/questions/${row.id}/`)
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
    const payload = {
      ...form,
      options: parseOptions(form.optionsText)
    }
    delete payload.optionsText
    if (form.id) {
      await api.put(`/exam/questions/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/exam/questions/', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    const data = e.response?.data
    const message = data?.content?.[0] || data?.answer?.[0] || '保存题目失败'
    ElMessage.error(message)
  }
}

function handleQuery() { fetchData() }
function handleReset() { Object.assign(queryForm, { subject: '', type: '' }); fetchData() }

onMounted(async () => {
  await fetchSubjects()
  await fetchData()
})
</script>

<style scoped>
.question-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
