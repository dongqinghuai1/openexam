<template>
  <div class="score-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成绩管理</span>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="考试">
          <el-select v-model="queryForm.exam" clearable>
            <el-option v-for="item in exams" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="student_id" label="学生ID" width="100" />
        <el-table-column prop="student_name" label="学生姓名" width="120" />
        <el-table-column prop="exam_name" label="考试" min-width="180" />
        <el-table-column prop="score" label="得分" width="100" />
        <el-table-column prop="total_score" label="总分" width="100" />
        <el-table-column prop="rank" label="排名" width="100" />
        <el-table-column prop="created_at" label="生成时间" min-width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'
import { useRoute } from 'vue-router'

const route = useRoute()

const loading = ref(false)
const tableData = ref([])
const exams = ref([])
const queryForm = reactive({ exam: route.query.exam || '' })

async function fetchOptions() {
  const res = await api.get('/exam/exams/')
  exams.value = res.data.results || res.data
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/exam/scores/', { params: queryForm })
    tableData.value = res.data.results || res.data
  } catch (e) {
    ElMessage.error('获取成绩失败')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchOptions()
  await fetchData()
})
</script>

<style scoped>
.score-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>
