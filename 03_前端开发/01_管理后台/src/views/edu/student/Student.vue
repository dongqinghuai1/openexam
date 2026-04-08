<template>
  <div class="student-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生管理</span>
          <el-button type="primary" @click="handleAdd">新增学生</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="queryForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="queryForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="在读" value="active" />
            <el-option label="休学" value="inactive" />
            <el-option label="毕业" value="graduated" />
            <el-option label="退学" value="withdrawn" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="gender" label="性别" width="60">
          <template #default="{ row }">{{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="grade" label="年级" width="80" />
        <el-table-column prop="school" label="学校" />
        <el-table-column prop="parent_name" label="家长姓名" width="100" />
        <el-table-column prop="parent_phone" label="家长手机" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期" prop="birthday">
          <el-date-picker v-model="form.birthday" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-input v-model="form.grade" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="form.school" />
        </el-form-item>
        <el-form-item label="家长姓名" prop="parent_name">
          <el-input v-model="form.parent_name" />
        </el-form-item>
        <el-form-item label="家长手机" prop="parent_phone">
          <el-input v-model="form.parent_phone" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="在读" value="active" />
            <el-option label="休学" value="inactive" />
            <el-option label="毕业" value="graduated" />
            <el-option label="退学" value="withdrawn" />
          </el-select>
        </el-form-item>
        <el-form-item label="入学日期" prop="enrollment_date">
          <el-date-picker v-model="form.enrollment_date" type="date" value-format="YYYY-MM-DD" />
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
const dialogVisible = ref(false)
const dialogTitle = ref('新增学生')
const formRef = ref()

const queryForm = reactive({ name: '', phone: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({
  id: null, name: '', phone: '', gender: 'male', birthday: '', grade: '', school: '',
  parent_name: '', parent_phone: '', status: 'active', enrollment_date: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  parent_name: [{ required: true, message: '请输入家长姓名', trigger: 'blur' }],
  parent_phone: [{ required: true, message: '请输入家长手机', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入年级', trigger: 'blur' }],
  enrollment_date: [{ required: true, message: '请选择入学日期', trigger: 'change' }]
}

function getStatusType(status) {
  const map = { active: 'success', inactive: 'warning', graduated: 'info', withdrawn: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { active: '在读', inactive: '休学', graduated: '毕业', withdrawn: '退学' }
  return map[status] || status
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/edu/students/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { name: '', phone: '', status: '' }); handleQuery() }

function handleAdd() {
  dialogTitle.value = '新增学生'
  Object.assign(form, { id: null, name: '', phone: '', gender: 'male', birthday: '', grade: '', school: '', parent_name: '', parent_phone: '', status: 'active', enrollment_date: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑学生'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

function handleView(row) {
  ElMessage.info('查看详情: ' + row.name)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除学生 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/edu/students/${row.id}/`)
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
          await api.put(`/edu/students/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/edu/students/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error('操作失败') }
    }
  })
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.student-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
