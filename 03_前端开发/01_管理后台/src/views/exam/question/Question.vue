<template>
  <div class="question-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <div class="header-actions">
            <el-button @click="downloadTemplate">下载导入模板</el-button>
            <el-button @click="handleExport">导出题目</el-button>
            <el-upload
              :show-file-list="false"
              :http-request="handleImport"
              accept=".xlsx,.xlsm,.xltx,.xltm"
            >
              <el-button type="success">批量导入</el-button>
            </el-upload>
            <el-button type="primary" @click="handleAdd">新增题目</el-button>
          </div>
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

      <el-alert type="info" :closable="false" class="import-tip">
        <template #title>
          导入说明：请先下载模板，按“科目编码、题型、题目内容、答案、难度、分值”等字段填写。导入前会先做预校验，确认无误后再真正写入。
        </template>
      </el-alert>

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

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[25, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
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

    <el-dialog v-model="previewVisible" title="导入预校验" width="880px">
      <div class="preview-summary">
        <el-tag type="success">预计新增 {{ importPreview.created || 0 }} 条</el-tag>
        <el-tag type="warning">预计更新 {{ importPreview.updated || 0 }} 条</el-tag>
        <el-tag :type="(importPreview.errors || []).length ? 'danger' : 'info'">错误 {{ (importPreview.errors || []).length }} 条</el-tag>
      </div>
      <div class="preview-toolbar">
        <el-checkbox v-model="previewErrorOnly">仅显示错误行</el-checkbox>
        <el-button @click="exportErrorRows">导出失败行</el-button>
      </div>
      <el-table :data="previewRows" max-height="360" stripe>
        <el-table-column prop="row" label="行号" width="80" />
        <el-table-column prop="subject_code" label="科目编码" width="120" />
        <el-table-column prop="content" label="题目内容" min-width="260" show-overflow-tooltip />
        <el-table-column prop="type" label="题型" width="100" />
        <el-table-column prop="action" label="动作" width="90" />
        <el-table-column label="校验结果" min-width="220">
          <template #default="{ row }">
            <span v-if="row.errors?.length" class="error-text">{{ row.errors.join('；') }}</span>
            <span v-else class="success-text">通过</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="previewVisible = false">取消</el-button>
        <el-button type="primary" :disabled="(importPreview.errors || []).length > 0 || !pendingImportFile" @click="confirmImport">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const subjects = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增题目')
const formRef = ref()
const previewVisible = ref(false)
const importPreview = ref({ preview: [], errors: [], created: 0, updated: 0 })
const pendingImportFile = ref(null)
const previewErrorOnly = ref(false)
const pagination = reactive({ page: 1, size: 25, total: 0 })

const previewRows = computed(() => {
  const rows = importPreview.value.preview || []
  return previewErrorOnly.value ? rows.filter(item => item.errors?.length) : rows
})

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

function downloadBlob(data, filename) {
  const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

async function exportErrorRows() {
  const rows = (importPreview.value.preview || []).filter(item => item.errors?.length)
  if (!rows.length) {
    ElMessage.info('当前没有错误行可导出')
    return
  }

  try {
    const { Workbook } = await import('https://cdn.jsdelivr.net/npm/exceljs@4.4.0/+esm')
    const workbook = new Workbook()
    const worksheet = workbook.addWorksheet('题库修正')
    worksheet.addRow(['科目编码', '章节', '题型', '题目内容', '选项', '答案', '解析', '难度', '分值', '状态'])
    rows.forEach((item) => {
      worksheet.addRow([
        item.subject_code || '',
        item.chapter || '',
        item.type || '',
        item.content || '',
        item.options_text || '',
        item.answer || '',
        item.analysis || '',
        item.difficulty || '',
        item.score || '',
        item.status ? 'true' : 'false'
      ])
    })
    const buffer = await workbook.xlsx.writeBuffer()
    downloadBlob(buffer, 'question_import_errors.xlsx')
  } catch (e) {
    ElMessage.error('导出失败行失败')
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/exam/questions/', {
      params: {
        ...queryForm,
        page: pagination.page,
        page_size: pagination.size
      }
    })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取题目失败'))
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
    if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '删除题目失败'))
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

function handleQuery() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(queryForm, { subject: '', type: '' })
  handleQuery()
}

async function downloadTemplate() {
  try {
    const res = await api.get('/exam/questions/template/', { responseType: 'blob' })
    downloadBlob(res.data, 'question_import_template.xlsx')
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '下载模板失败'))
  }
}

async function handleExport() {
  try {
    const res = await api.get('/exam/questions/export/', { params: queryForm, responseType: 'blob' })
    downloadBlob(res.data, 'questions.xlsx')
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '导出题目失败'))
  }
}

async function handleImport(option) {
  pendingImportFile.value = option.file
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await api.post('/exam/questions/import_preview/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    importPreview.value = res.data || { preview: [], errors: [], created: 0, updated: 0 }
    previewErrorOnly.value = false
    previewVisible.value = true
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '导入题目失败'))
  } finally {
    option.onSuccess?.()
  }
}

async function confirmImport() {
  if (!pendingImportFile.value) return
  const formData = new FormData()
  formData.append('file', pendingImportFile.value)
  try {
    const res = await api.post('/exam/questions/import_file/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const result = res.data || {}
    ElMessage.success(`导入完成：新增 ${result.created || 0} 条，更新 ${result.updated || 0} 条`)
    previewVisible.value = false
    pendingImportFile.value = null
    fetchData()
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '确认导入失败'))
  }
}

onMounted(async () => {
  await fetchSubjects()
  await fetchData()
})
</script>

<style scoped>
.question-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.search-form { margin-bottom: 20px; }
.import-tip { margin-bottom: 20px; }
.preview-summary { display: flex; gap: 12px; margin-bottom: 16px; }
.preview-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.error-text { color: #f56c6c; }
.success-text { color: #67c23a; }
</style>
