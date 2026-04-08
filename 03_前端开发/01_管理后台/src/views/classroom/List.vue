<template>
  <div class="classroom-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>在线课堂</span>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="班级">
          <el-select v-model="queryForm.class_name" placeholder="请选择" clearable>
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="未开始" value="pending" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="schedule.date" label="上课日期" width="120" />
        <el-table-column prop="schedule.start_time" label="开始时间" width="100" />
        <el-table-column prop="schedule.end_time" label="结束时间" width="100" />
        <el-table-column prop="schedule.edu_class.name" label="班级" width="120" />
        <el-table-column prop="schedule.course.name" label="课程" width="120" />
        <el-table-column prop="schedule.teacher.name" label="教师" width="100" />
        <el-table-column prop="meeting_id" label="会议ID" width="150" />
        <el-table-column prop="join_url" label="入会链接" width="120">
          <template #default="{ row }">
            <el-link v-if="row.join_url" type="primary" :href="row.join_url" target="_blank">进入课堂</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" link @click="handleCreateMeeting(row)">创建会议</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handleStart(row)">开始上课</el-button>
            <el-button v-if="row.status === 'ongoing'" type="warning" link @click="handleJoin(row)">进入课堂</el-button>
            <el-button v-if="row.status === 'ongoing'" type="danger" link @click="handleEnd(row)">结束课堂</el-button>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'

const loading = ref(false)
const tableData = ref([])
const classes = ref([])
const queryForm = reactive({ class_name: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

function getStatusType(status) {
  const map = { pending: 'info', ongoing: 'success', ended: '' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending: '未开始', ongoing: '进行中', ended: '已结束' }
  return map[status] || status
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/classroom/meeting_rooms/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) { ElMessage.error('获取数据失败') }
  finally { loading.value = false }
}

async function fetchClasses() {
  try {
    const res = await api.get('/edu/classes/')
    classes.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { class_name: '', status: '' }); handleQuery() }

async function handleCreateMeeting(row) {
  try {
    await api.post('/classroom/meeting_rooms/create_meeting/', { schedule_id: row.schedule.id })
    ElMessage.success('会议创建成功')
    fetchData()
  } catch (e) { ElMessage.error('创建失败') }
}

function handleStart(row) {
  ElMessage.info('开始上课: ' + row.schedule?.edu_class?.name)
}

function handleJoin(row) {
  if (row.join_url) {
    window.open(row.join_url, '_blank')
  }
}

async function handleEnd(row) {
  try {
    await ElMessageBox.confirm('确定结束课堂吗?', '提示', { type: 'warning' })
    await api.post(`/classroom/meeting_rooms/${row.id}/end_meeting/`)
    ElMessage.success('课堂已结束')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

onMounted(() => { fetchData(); fetchClasses() })
</script>

<style scoped>
.classroom-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>