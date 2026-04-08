<template>
  <div class="schedule-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排课管理</span>
          <el-button type="primary" @click="handleAdd">新建排课</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="班级">
          <el-select v-model="queryForm.edu_class" placeholder="请选择" clearable>
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教师">
          <el-select v-model="queryForm.teacher" placeholder="请选择" clearable>
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="queryForm.date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-calendar v-model="calendarDate">
        <template #date-cell="{ data }">
          <div class="calendar-cell">
            <div class="date-number">{{ data.day.split('-').slice(1).join('-') }}</div>
            <div class="schedule-list">
              <div v-for="s in getSchedulesByDate(data.day)" :key="s.id" class="schedule-item" @click="handleView(s)">
                <span class="time">{{ s.start_time?.substring(0,5) }}</span>
                <span class="name">{{ s.class_name }}</span>
              </div>
            </div>
          </div>
        </template>
      </el-calendar>

      <el-divider />

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="class_name" label="班级" width="150" />
        <el-table-column prop="course_name" label="课程" width="150" />
        <el-table-column prop="teacher_name" label="教师" width="100" />
        <el-table-column prop="room" label="教室" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleReschedule(row)">调课</el-button>
            <el-button type="danger" link @click="handleCancel(row)">取消</el-button>
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
        <el-form-item label="班级" prop="edu_class">
          <el-select v-model="form.edu_class" placeholder="请选择">
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course">
          <el-select v-model="form.course" placeholder="请选择">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教师" prop="teacher">
          <el-select v-model="form.teacher" placeholder="请选择">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课日期" prop="date">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="教室">
          <el-input v-model="form.room" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.note" type="textarea" :rows="2" />
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
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const classes = ref([])
const teachers = ref([])
const courses = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建排课')
const formRef = ref()
const calendarDate = ref(new Date())

const queryForm = reactive({ edu_class: '', teacher: '', date: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({
  id: null, edu_class: null, course: null, teacher: null, date: '', start_time: '', end_time: '', room: '', note: ''
})

const rules = {
  edu_class: [{ required: true, message: '请选择班级', trigger: 'change' }],
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  teacher: [{ required: true, message: '请选择教师', trigger: 'change' }],
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

function getStatusType(status) {
  const map = { scheduled: 'success', cancelled: 'info', completed: 'warning' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { scheduled: '已排课', cancelled: '已取消', completed: '已完成' }
  return map[status] || status
}

function getSchedulesByDate(date) {
  return tableData.value.filter(s => s.date === date)
}

async function fetchData() {
  loading.value = true
  try {
    const params = { ...queryForm, page: pagination.page, page_size: pagination.size }
    if (calendarDate.value) {
      params.date = dayjs(calendarDate.value).format('YYYY-MM-DD')
    }
    const res = await api.get('/edu/schedules/', { params })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchOptions() {
  try {
    const [clsRes, tRes, cRes] = await Promise.all([
      api.get('/edu/classes/'),
      api.get('/edu/teachers/'),
      api.get('/edu/courses/')
    ])
    classes.value = clsRes.data.results || clsRes.data
    teachers.value = tRes.data.results || tRes.data
    courses.value = cRes.data.results || cRes.data
  } catch (e) { console.error(e) }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { edu_class: '', teacher: '', date: '' }); handleQuery() }

function handleAdd() {
  dialogTitle.value = '新建排课'
  Object.assign(form, { id: null, edu_class: null, course: null, teacher: null, date: '', start_time: '', end_time: '', room: '', note: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑排课'
  Object.assign(form, { ...row, edu_class: row.edu_class?.id || row.edu_class, course: row.course?.id || row.course, teacher: row.teacher?.id || row.teacher })
  dialogVisible.value = true
}

function handleView(row) { ElMessage.info('查看: ' + row.class_name) }

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定取消该排课吗？', '提示', { type: 'warning' })
    await api.delete(`/edu/schedules/${row.id}/`)
    ElMessage.success('取消成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

function handleReschedule(row) { ElMessage.info('调课功能: ' + row.class_name) }

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.id) {
          await api.put(`/edu/schedules/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/edu/schedules/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error('操作失败') }
    }
  })
}

onMounted(() => { fetchData(); fetchOptions() })
</script>

<style scoped>
.schedule-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
.calendar-cell { height: 100%; min-height: 60px; }
.date-number { font-size: 12px; color: #999; }
.schedule-list { margin-top: 5px; }
.schedule-item { font-size: 12px; background: #e6f4ff; padding: 2px 5px; margin-bottom: 2px; border-radius: 3px; cursor: pointer; }
.schedule-item:hover { background: #bae7ff; }
.schedule-item .time { margin-right: 5px; }
</style>