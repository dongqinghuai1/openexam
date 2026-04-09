<template>
  <div class="teacher-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教师管理</span>
          <el-button type="primary" @click="handleAdd">新增教师</el-button>
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
            <el-option label="在职" value="active" />
            <el-option label="离职" value="resigned" />
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
        <el-table-column prop="education" label="学历" width="80" />
        <el-table-column prop="major" label="专业" />
        <el-table-column prop="subjects" label="擅长科目">
          <template #default="{ row }">
            <el-tag v-for="sub in row.subjects" :key="sub.id" size="small" style="margin-right: 5px">{{ sub.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="class_count" label="班级数" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status === 'active' ? '在职' : '离职' }}</el-tag>
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
        <el-form-item label="学历" prop="education">
          <el-input v-model="form.education" />
        </el-form-item>
        <el-form-item label="专业" prop="major">
          <el-input v-model="form.major" />
        </el-form-item>
        <el-form-item label="证书">
          <el-input v-model="form.certification" />
        </el-form-item>
        <el-form-item label="擅长科目" prop="subject_ids">
          <el-select v-model="form.subject_ids" multiple placeholder="请选择">
            <el-option v-for="sub in subjects" :key="sub.id" :label="sub.name" :value="sub.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="薪资类型">
          <el-radio-group v-model="form.salary_type">
            <el-radio value="hourly">按课时</el-radio>
            <el-radio value="fixed">固定工资</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker v-model="form.hire_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="在职" value="active" />
            <el-option label="离职" value="resigned" />
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
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const subjects = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增教师')
const formRef = ref()

const queryForm = reactive({ name: '', phone: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({
  id: null, name: '', phone: '', gender: 'male', birthday: '', education: '', major: '',
  certification: '', subject_ids: [], salary_type: 'hourly', hire_date: '', status: 'active'
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  education: [{ required: true, message: '请输入学历', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  hire_date: [{ required: true, message: '请选择入职日期', trigger: 'change' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/edu/teachers/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取教师数据失败'))
  } finally {
    loading.value = false
  }
}

async function fetchSubjects() {
  try {
    const res = await api.get('/edu/subjects/')
    subjects.value = res.data.results || res.data
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取科目列表失败')) }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { name: '', phone: '', status: '' }); handleQuery() }

function handleAdd() {
  dialogTitle.value = '新增教师'
  Object.assign(form, { id: null, name: '', phone: '', gender: 'male', birthday: '', education: '', major: '', certification: '', subject_ids: [], salary_type: 'hourly', hire_date: '', status: 'active' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑教师'
  form.subject_ids = row.subjects?.map(s => s.id) || []
  Object.assign(form, { ...row, subject_ids: form.subject_ids })
  dialogVisible.value = true
}

function handleView(row) { ElMessage.info('查看详情: ' + row.name) }

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除教师 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/edu/teachers/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '删除教师失败')) }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.id) {
          await api.put(`/edu/teachers/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/edu/teachers/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error(extractErrorMessage(e, '保存教师失败')) }
    }
  })
}

onMounted(() => { fetchData(); fetchSubjects() })
</script>

<style scoped>
.teacher-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
