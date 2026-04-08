<template>
  <div class="order-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="queryForm.order_no" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="学生姓名">
          <el-input v-model="queryForm.student_name" placeholder="请输入学生姓名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="queryForm.payment_type" placeholder="请选择" clearable>
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="线下" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="student.name" label="学生姓名" width="100" />
        <el-table-column prop="student.phone" label="手机号" width="120" />
        <el-table-column label="课程/套餐" width="150">
          <template #default="{ row }">
            {{ row.course?.name || row.course_package?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="课时数" width="80" />
        <el-table-column prop="amount" label="原价" width="100">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="discount" label="优惠" width="80">
          <template #default="{ row }">¥{{ row.discount }}</template>
        </el-table-column>
        <el-table-column prop="final_amount" label="实收" width="100">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold">¥{{ row.final_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_type" label="支付方式" width="80">
          <template #default="{ row }">
            <span>{{ getPaymentType(row.payment_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handlePay(row)">支付</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleCancel(row)">取消</el-button>
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
const dialogVisible = ref(false)
const dialogTitle = ref('订单详情')

const queryForm = reactive({ order_no: '', student_name: '', status: '', payment_type: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })

function getStatusType(status) {
  const map = { pending: 'warning', paid: 'success', cancelled: 'info', refunded: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending: '待支付', paid: '已支付', cancelled: '已取消', refunded: '已退款' }
  return map[status] || status
}

function getPaymentType(type) {
  const map = { wechat: '微信', alipay: '支付宝', offline: '线下' }
  return map[type] || type
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/finance/orders/', { params: { ...queryForm, page: pagination.page, page_size: pagination.size } })
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || tableData.value.length
  } catch (e) { ElMessage.error('获取数据失败') }
  finally { loading.value = false }
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { order_no: '', student_name: '', status: '', payment_type: '' }); handleQuery() }
function handleView(row) { ElMessage.info('订单详情: ' + row.order_no) }

async function handlePay(row) {
  try {
    await ElMessageBox.confirm('确认支付该订单?', '提示', { type: 'info' })
    await api.post(`/finance/orders/${row.id}/pay/`)
    ElMessage.success('支付成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('支付失败') }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定取消该订单吗?', '提示', { type: 'warning' })
    await api.post(`/finance/orders/${row.id}/cancel/`)
    ElMessage.success('取消成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.order-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>