<template>
  <div class="recording-page">
    <el-card>
      <template #header>
        <span>录屏回放</span>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="课程">
          <el-input v-model="queryForm.course_name" placeholder="请输入课程名称" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="可用" value="ready" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="recording_task.meeting_room.schedule.edu_class.name" label="班级" width="120" />
        <el-table-column prop="recording_task.meeting_room.schedule.course.name" label="课程" width="120" />
        <el-table-column prop="recording_task.meeting_room.schedule.date" label="上课日期" width="120" />
        <el-table-column prop="recording_task.start_time" label="录制开始" width="160" />
        <el-table-column prop="duration" label="时长(分钟)" width="100">
          <template #default="{ row }">{{ Math.floor(row.duration / 60) || '-' }}</template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_permission" label="查看权限" width="100">
          <template #default="{ row }">
            <span>{{ getPermissionText(row.view_permission) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'ready'" type="primary" link @click="handlePlay(row)">播放</el-button>
            <el-button v-if="row.status === 'ready'" type="success" link @click="handleDownload(row)">下载</el-button>
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
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'

const loading = ref(false)
const tableData = ref([])
const queryForm = reactive({ course_name: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

function getStatusType(status) {
  const map = { pending: 'info', ready: 'success', failed: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending: '待处理', ready: '可用', failed: '失败' }
  return map[status] || status
}

function getPermissionText(permission) {
  const map = { all: '所有人', teacher: '教师', student: '学生', none: '不可查看' }
  return map[permission] || permission
}

function formatSize(bytes) {
  if (!bytes) return '-'
  const mb = bytes / 1024 / 1024
  return mb > 1 ? mb.toFixed(1) + 'MB' : (bytes / 1024).toFixed(1) + 'KB'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/classroom/playbacks/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) { ElMessage.error('获取数据失败') }
  finally { loading.value = false }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { course_name: '', status: '' }); handleQuery() }

async function handlePlay(row) {
  try {
    const res = await api.get(`/classroom/playbacks/${row.id}/url/`)
    if (res.data.url) {
      window.open(res.data.url, '_blank')
    } else {
      ElMessage.error('无法获取播放地址')
    }
  } catch (e) { ElMessage.error('获取播放地址失败') }
}

function handleDownload(row) {
  if (row.file_url) {
    window.open(row.file_url, '_blank')
  } else {
    ElMessage.warning('当前没有可下载文件')
  }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.recording-page { padding: 20px; }
.search-form { margin-bottom: 20px; }
</style>
