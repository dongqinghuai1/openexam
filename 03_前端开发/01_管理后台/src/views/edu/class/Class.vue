<template>
  <div class="class-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleAdd">新建班级</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="班级名称">
          <el-input v-model="queryForm.name" placeholder="请输入班级名称" clearable />
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="queryForm.course" placeholder="请选择" clearable>
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="开班" value="open" />
            <el-option label="结课" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="班级名称" width="150" />
        <el-table-column prop="code" label="班级编码" width="100" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="teacher_name" label="授课教师" width="100" />
        <el-table-column prop="max_students" label="最大人数" width="100" />
        <el-table-column prop="student_count" label="当前人数" width="100" />
        <el-table-column prop="start_date" label="开班日期" width="120" />
        <el-table-column prop="end_date" label="结课日期" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'open' ? 'success' : 'info'">{{ row.status === 'open' ? '开班' : '结课' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleAddStudent(row)">添加学生</el-button>
            <el-button type="info" link @click="handleViewStudent(row)">查看学生</el-button>
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
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="班级编码" prop="code">
          <el-input v-model="form.code" placeholder="留空自动生成" />
        </el-form-item>
        <el-form-item label="课程" prop="course">
          <el-select v-model="form.course" placeholder="请选择">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher">
          <el-select v-model="form.teacher" placeholder="请选择">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大人数" prop="max_students">
          <el-input-number v-model="form.max_students" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="开班日期" prop="start_date">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="结课日期">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="开班" value="open" />
            <el-option label="结课" value="closed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="studentDialogVisible" title="班级学生" width="600px">
      <template #header>
        <div class="card-header">
          <span>班级学生</span>
          <el-button type="primary" size="small" @click="openAddStudentDialog">添加学生</el-button>
        </div>
      </template>
      <el-table :data="classStudents" stripe>
        <el-table-column prop="student.name" label="姓名" width="100" />
        <el-table-column prop="student.phone" label="手机号" width="120" />
        <el-table-column prop="student.grade" label="年级" width="80" />
        <el-table-column prop="join_date" label="入班日期" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'studying' ? 'success' : 'info'">{{ row.status === 'studying' ? '在读' : row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" link @click="handleRemoveStudent(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="addStudentDialogVisible" title="添加学生到班级" width="500px">
      <el-form ref="studentFormRef" :model="studentForm" :rules="studentRules" label-width="100px">
        <el-form-item label="选择学生" prop="student_id">
          <el-select v-model="studentForm.student_id" placeholder="请选择学生" filterable>
            <el-option v-for="stu in availableStudents" :key="stu.id" :label="`${stu.name} (${stu.phone})`" :value="stu.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入班日期" prop="join_date">
          <el-date-picker v-model="studentForm.join_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addStudentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddStudent">确定</el-button>
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
const courses = ref([])
const teachers = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建班级')
const formRef = ref()
const studentDialogVisible = ref(false)
const addStudentDialogVisible = ref(false)
const studentFormRef = ref()
const classStudents = ref([])
const availableStudents = ref([])
const currentClassId = ref(null)

const queryForm = reactive({ name: '', course: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({
  id: null, name: '', code: '', course: null, teacher: null, max_students: 20, start_date: '', end_date: '', status: 'open'
})
const studentForm = reactive({ student_id: null, join_date: '' })

const rules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  teacher: [{ required: true, message: '请选择授课教师', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开班日期', trigger: 'change' }],
  end_date: [{ validator: validateEndDate, trigger: 'change' }]
}
const studentRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  join_date: [{ required: true, message: '请选择入班日期', trigger: 'change' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/edu/classes/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取班级数据失败')) }
  finally { loading.value = false }
}

async function fetchOptions() {
  try {
    const [cRes, tRes] = await Promise.all([api.get('/edu/courses/'), api.get('/edu/teachers/')])
    courses.value = cRes.data.results || cRes.data
    teachers.value = tRes.data.results || tRes.data
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取班级下拉数据失败')) }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { name: '', course: '', status: '' }); handleQuery() }

function handleAdd() {
  dialogTitle.value = '新建班级'
  Object.assign(form, {
    id: null,
    name: '',
    code: '',
    course: null,
    teacher: null,
    max_students: 20,
    start_date: '',
    end_date: '',
    status: 'open'
  })
  dialogVisible.value = true
}

function getErrorMessage(error, fallback) {
  const data = error?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (data.error) return data.error
  const firstKey = Object.keys(data)[0]
  const firstValue = firstKey ? data[firstKey] : null
  if (Array.isArray(firstValue)) return firstValue[0]
  if (typeof firstValue === 'string') return firstValue
  return fallback
}

function validateEndDate(rule, value, callback) {
  if (value && form.start_date && value < form.start_date) {
    callback(new Error('结课日期不能早于开班日期'))
    return
  }
  callback()
}

function handleEdit(row) {
  dialogTitle.value = '编辑班级'
  Object.assign(form, { ...row, course: row.course?.id || row.course, teacher: row.teacher?.id || row.teacher })
  dialogVisible.value = true
}

async function handleAddStudent(row) {
  currentClassId.value = row.id
  await Promise.all([fetchClassStudents(row.id), fetchAvailableStudents(row.id)])
  if (availableStudents.value.length === 0) {
    ElMessage.warning('当前没有可添加的学生，请先创建学生或检查学生状态')
    return
  }
  studentForm.student_id = null
  studentForm.join_date = new Date().toISOString().slice(0, 10)
  addStudentDialogVisible.value = true
}

async function handleViewStudent(row) {
  currentClassId.value = row.id
  try {
    await fetchClassStudents(row.id)
    studentDialogVisible.value = true
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取班级学生列表失败')) }
}

async function fetchClassStudents(classId) {
  const res = await api.get(`/edu/classes/${classId}/`)
  classStudents.value = res.data.class_students || []
}

async function fetchAvailableStudents(classId) {
  const [studentRes, classRes] = await Promise.all([
    api.get('/edu/students/'),
    api.get(`/edu/classes/${classId}/`)
  ])
  const students = studentRes.data.results || studentRes.data
  const currentStudentIds = new Set((classRes.data.class_students || []).filter(item => item.status === 'studying').map(item => item.student.id))
  availableStudents.value = students.filter(item => !currentStudentIds.has(item.id) && item.status === 'active')
}

function openAddStudentDialog() {
  if (!currentClassId.value) return
  handleAddStudent({ id: currentClassId.value, name: '' })
}

async function submitAddStudent() {
  if (!studentFormRef.value || !currentClassId.value) return
  const valid = await studentFormRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    await api.post(`/edu/classes/${currentClassId.value}/add_student/`, studentForm)
    ElMessage.success('添加学生成功')
    addStudentDialogVisible.value = false
    await fetchClassStudents(currentClassId.value)
    await fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || getErrorMessage(e, '添加学生失败'))
  }
}

async function handleRemoveStudent(row) {
  try {
    await ElMessageBox.confirm(`确定移除学生 "${row.student.name}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/edu/classes/${currentClassId.value}/remove_student/${row.student.id}/`)
    ElMessage.success('移除成功')
    await fetchClassStudents(currentClassId.value)
    await fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '移除学生失败'))
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    const payload = {
      ...form,
      code: form.code || undefined
    }
    if (form.id) {
      await api.put(`/edu/classes/${form.id}/`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/edu/classes/', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, getErrorMessage(e, '保存班级失败')))
  }
}

onMounted(() => { fetchData(); fetchOptions() })
</script>

<style scoped>
.class-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
