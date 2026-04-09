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
          <el-select v-model="queryForm.edu_class" placeholder="请选择" clearable>
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
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
        <el-table-column prop="date" label="上课日期" width="120" />
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="class_name" label="班级" width="120" />
        <el-table-column prop="course_name" label="课程" width="120" />
        <el-table-column prop="teacher_name" label="教师" width="100" />
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
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.meeting_room_id" type="primary" link @click="handleCreateMeeting(row)">创建会议</el-button>
            <el-button v-if="row.meeting_room_id && row.status === 'pending'" type="success" link @click="handleStart(row)">开始上课</el-button>
            <el-button v-if="row.status === 'ongoing'" type="warning" link @click="handleJoin(row)">进入课堂</el-button>
            <el-button v-if="row.status === 'ongoing'" type="danger" link @click="handleEnd(row)">结束课堂</el-button>
            <el-button v-if="row.status === 'ended'" type="info" link @click="handleViewPlayback(row)">查看回放</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const classes = ref([])
const queryForm = reactive({ edu_class: '', status: '' })

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
    const [scheduleRes, meetingRes] = await Promise.all([
      api.get('/edu/schedules/', { params: { ...queryForm, page_size: 100 } }),
      api.get('/classroom/meeting_rooms/', { params: { page_size: 100 } })
    ])
    const schedules = scheduleRes.data.results || scheduleRes.data
    const meetings = meetingRes.data.results || meetingRes.data
    const meetingMap = new Map(meetings.map(item => [item.schedule, item]))
    tableData.value = schedules.map(item => {
      const meeting = meetingMap.get(item.id)
      return {
        ...item,
        meeting_room_id: meeting?.id || null,
        meeting_id: meeting?.meeting_id || '-',
        join_url: meeting?.join_url || '',
        status: meeting?.status || 'pending'
      }
    })
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取课堂数据失败'))
  } finally {
    loading.value = false
  }
}

async function fetchClasses() {
  const res = await api.get('/edu/classes/')
  classes.value = res.data.results || res.data
}

function handleQuery() { fetchData() }
function handleReset() { Object.assign(queryForm, { edu_class: '', status: '' }); fetchData() }

async function handleCreateMeeting(row) {
  try {
    await api.post('/classroom/meeting_rooms/create_meeting/', { schedule_id: row.id })
    ElMessage.success('会议创建成功')
    fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '创建会议失败')
  }
}

async function handleStart(row) {
  try {
    await api.post(`/classroom/meeting_rooms/${row.meeting_room_id}/start_meeting/`)
    ElMessage.success('课堂已开始')
    fetchData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '开始课堂失败')
  }
}

function handleJoin(row) {
  if (row.join_url) {
    window.open(row.join_url, '_blank')
  }
}

async function handleEnd(row) {
  try {
    await ElMessageBox.confirm('确定结束课堂吗? 结束后将生成回放并联动扣课。', '提示', { type: 'warning' })
    await api.post(`/classroom/meeting_rooms/${row.meeting_room_id}/end_meeting/`)
    ElMessage.success('课堂已结束')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.error || '结束课堂失败')
  }
}

async function handleViewPlayback(row) {
  try {
    const res = await api.get('/classroom/playbacks/', { params: { page_size: 100 } })
    const list = res.data.results || res.data
    const target = list.find(item => item.recording_task && item.recording_task.meeting_room === row.meeting_room_id)
    if (!target) {
      ElMessage.warning('当前课堂暂无回放文件')
      return
    }
    const playbackRes = await api.get(`/classroom/playbacks/${target.id}/url/`)
    if (playbackRes.data.url) {
      window.open(playbackRes.data.url, '_blank')
    }
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取回放失败'))
  }
}

onMounted(async () => {
  await fetchClasses()
  await fetchData()
})
</script>

<style scoped>
.classroom-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
