<template>
  <div class="refund-page page-shell">
    <el-card class="surface-card">
      <template #header>
        <div>
          <div class="page-title">退款管理</div>
          <div class="page-subtitle">跟踪退款申请、审批进度和课时冻结联动。</div>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="queryForm.order_no" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="退款ID" width="80" />
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="student_name" label="学生姓名" min-width="120" />
        <el-table-column prop="amount" label="退款金额" width="110">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="退款原因" min-width="150" />
        <el-table-column prop="applicant_name" label="申请人" min-width="120" />
        <el-table-column prop="created_at" label="申请时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" class-name="operation-column">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">批准</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
            </template>
            <el-button v-else type="primary" link @click="handleView(row)">详情</el-button>
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
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const queryForm = reactive({ order_no: '', status: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

function getStatusType(status) {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending: '待审批', approved: '已批准', rejected: '已拒绝' }
  return map[status] || status
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/finance/refunds/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取退款数据失败')) }
  finally { loading.value = false }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { order_no: '', status: '' }); handleQuery() }
function handleView(row) { ElMessage.info(`退款详情: ${row.order_no} / ${row.amount}`) }

async function handleApprove(row) {
  try {
    await ElMessageBox.confirm('确定批准该退款申请吗?', '提示', { type: 'warning' })
    await api.post(`/finance/refunds/${row.id}/approve/`)
    ElMessage.success('审批成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '退款审批失败')) }
}

async function handleReject(row) {
  try {
    await ElMessageBox.confirm('确定拒绝该退款申请吗?', '提示', { type: 'warning' })
    await api.post(`/finance/refunds/${row.id}/reject/`)
    ElMessage.success('已拒绝')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '退款拒绝失败')) }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.refund-page { padding: 20px; }
</style>
