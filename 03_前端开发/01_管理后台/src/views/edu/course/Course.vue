<template>
  <div class="course-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="课程名称">
          <el-input v-model="queryForm.name" placeholder="请输入课程名称" clearable />
        </el-form-item>
        <el-form-item label="科目">
          <el-select v-model="queryForm.subject" placeholder="请选择" clearable>
            <el-option v-for="sub in subjects" :key="sub.id" :label="sub.name" :value="sub.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="在售" value="active" />
            <el-option label="已下架" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="课程名称" width="180" />
        <el-table-column prop="code" label="课程编码" width="100" />
        <el-table-column prop="subject_name" label="科目" width="100" />
        <el-table-column prop="cover" label="封面" width="80">
          <template #default="{ row }">
            <el-image v-if="row.cover" :src="row.cover" style="width: 50px; height: 50px" fit="cover" />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="总课时" width="80" />
        <el-table-column prop="duration" label="单次时长(分钟)" width="120" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="chapter_count" label="章节数" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status === 'active' ? '在售' : '已下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="课程编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="所属科目" prop="subject">
          <el-select v-model="form.subject" placeholder="请选择">
            <el-option v-for="sub in subjects" :key="sub.id" :label="sub.name" :value="sub.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="form.cover" placeholder="请输入图片URL" />
        </el-form-item>
        <el-form-item label="总课时" prop="total_hours">
          <el-input-number v-model="form.total_hours" :min="1" />
        </el-form-item>
        <el-form-item label="单次时长(分钟)" prop="duration">
          <el-input-number v-model="form.duration" :min="30" :step="30" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="在售" value="active" />
            <el-option label="已下架" value="archived" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'

const loading = ref(false)
const tableData = ref([])
const subjects = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增课程')
const formRef = ref()

const queryForm = reactive({ name: '', subject: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({
  id: null, name: '', code: '', subject: null, description: '', cover: '',
  total_hours: 10, duration: 90, price: 0, status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入课程编码', trigger: 'blur' }],
  subject: [{ required: true, message: '请选择所属科目', trigger: 'change' }],
  total_hours: [{ required: true, message: '请输入总课时', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/edu/courses/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchSubjects() {
  try {
    const res = await api.get('/edu/subjects/')
    subjects.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { name: '', subject: '', status: '' }); handleQuery() }

function handleAdd() {
  dialogTitle.value = '新增课程'
  Object.assign(form, { id: null, name: '', code: '', subject: null, description: '', cover: '', total_hours: 10, duration: 90, price: 0, status: 'active' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑课程'
  Object.assign(form, { ...row, subject: row.subject?.id || row.subject })
  dialogVisible.value = true
}

function handleView(row) { ElMessage.info('查看详情: ' + row.name) }

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除课程 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/edu/courses/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.id) {
          await api.put(`/edu/courses/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/edu/courses/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error('操作失败') }
    }
  })
}

onMounted(() => { fetchData(); fetchSubjects() })
</script>

<style scoped>
.course-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>