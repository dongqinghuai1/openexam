<template>
  <div class="log-page">
    <el-card>
      <template #header>
        <span>操作日志</span>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="操作人">
          <el-input v-model="queryForm.username" clearable />
        </el-form-item>
        <el-form-item label="方法">
          <el-select v-model="queryForm.method" clearable>
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="method" label="方法" width="100" />
        <el-table-column prop="path" label="路径" min-width="220" />
        <el-table-column prop="duration" label="耗时(ms)" width="100" />
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const queryForm = reactive({ username: '', method: '' })

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/users/operation-logs/', { params: queryForm })
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取操作日志失败'))
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.log-page { padding: 20px; }
.search-form { margin-bottom: 20px; }
</style>
