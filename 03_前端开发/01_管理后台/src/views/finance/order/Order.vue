<template>
  <div class="order-page page-shell">
    <el-card class="surface-card">
      <template #header>
        <div class="card-header">
          <div>
            <div class="page-title">订单管理</div>
            <div class="page-subtitle">跟踪订单创建、支付状态与退款动作，保持财务流转清晰可查。</div>
          </div>
          <el-button type="primary" @click="handleAdd">新增订单</el-button>
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
        <el-table-column prop="order_no" label="订单号" min-width="190" />
        <el-table-column prop="student.name" label="学生姓名" min-width="120" />
        <el-table-column prop="student.phone" label="手机号" min-width="140" />
        <el-table-column label="课程/套餐" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.course?.name || row.course_package?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="课时数" width="90" align="center" />
        <el-table-column prop="amount" label="原价" width="110" align="right">
          <template #default="{ row }">¥{{ row.amount }}</template>
        </el-table-column>
        <el-table-column prop="discount" label="优惠" width="100" align="right">
          <template #default="{ row }">¥{{ row.discount }}</template>
        </el-table-column>
        <el-table-column prop="final_amount" label="实收" width="110" align="right">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold">¥{{ row.final_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_type" label="支付方式" width="100" align="center">
          <template #default="{ row }">
            <span>{{ getPaymentType(row.payment_type) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column label="操作" width="220" fixed="right" class-name="operation-column">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handlePay(row)">支付</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleCancel(row)">取消</el-button>
            <el-button v-if="row.status === 'paid'" type="warning" link @click="handleApplyRefund(row)">申请退款</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
      <el-form v-if="dialogMode === 'create'" ref="formRef" :model="form" :rules="rules" label-width="92px" class="two-col-form">
        <el-form-item label="学生" prop="student">
          <el-select v-model="form.student" filterable>
            <el-option v-for="item in students" :key="item.id" :label="`${item.name} (${item.phone})`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course">
          <el-select v-model="form.course" clearable>
            <el-option v-for="item in courses" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课时数" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" :max="500" />
        </el-form-item>
        <el-form-item label="订单金额" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="优惠金额">
          <el-input-number v-model="form.discount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="实收金额" prop="final_amount">
          <el-input-number v-model="form.final_amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_type">
          <el-select v-model="form.payment_type">
            <el-option label="微信" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="线下" value="offline" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-descriptions v-else-if="dialogMode === 'detail'" :column="2" border>
        <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="学生">{{ currentOrder.student_name }}</el-descriptions-item>
        <el-descriptions-item label="课程">{{ currentOrder.course_name || currentOrder.package_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="课时数">{{ currentOrder.quantity }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">¥{{ currentOrder.amount }}</el-descriptions-item>
        <el-descriptions-item label="实收金额">¥{{ currentOrder.final_amount }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ getPaymentType(currentOrder.payment_type) }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getStatusText(currentOrder.status) }}</el-descriptions-item>
      </el-descriptions>

      <el-form v-else ref="refundFormRef" :model="refundForm" :rules="refundRules" label-width="92px" class="single-col-form">
        <el-form-item label="退款金额" prop="amount">
          <el-input-number v-model="refundForm.amount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="退款原因" prop="reason">
          <el-input v-model="refundForm.reason" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="dialogMode === 'create'" type="primary" @click="submitOrder">确定</el-button>
        <el-button v-else-if="dialogMode === 'refund'" type="primary" @click="submitRefund">提交</el-button>
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
const dialogVisible = ref(false)
const dialogTitle = ref('订单详情')
const dialogMode = ref('detail')
const formRef = ref()
const refundFormRef = ref()
const students = ref([])
const courses = ref([])
const currentOrder = ref({})

const queryForm = reactive({ order_no: '', student_name: '', status: '', payment_type: '' })
const pagination = reactive({ page: 1, size: 10, total: 0 })
const form = reactive({ student: null, course: null, quantity: 1, amount: 0, discount: 0, final_amount: 0, payment_type: 'wechat', status: 'pending' })
const refundForm = reactive({ amount: 0, reason: '' })

const rules = {
  student: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入课时数', trigger: 'change' }],
  amount: [{ required: true, message: '请输入订单金额', trigger: 'change' }],
  final_amount: [{ required: true, message: '请输入实收金额', trigger: 'change' }],
  payment_type: [{ required: true, message: '请选择支付方式', trigger: 'change' }]
}

const refundRules = {
  amount: [{ required: true, message: '请输入退款金额', trigger: 'change' }],
  reason: [{ required: true, message: '请输入退款原因', trigger: 'blur' }]
}

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
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取订单数据失败')) }
  finally { loading.value = false }
}

async function fetchOptions() {
  const [studentRes, courseRes] = await Promise.all([
    api.get('/edu/students/'),
    api.get('/edu/courses/')
  ])
  students.value = studentRes.data.results || studentRes.data
  courses.value = courseRes.data.results || courseRes.data
}

function handleQuery() { pagination.page = 1; fetchData() }
function handleReset() { Object.assign(queryForm, { order_no: '', student_name: '', status: '', payment_type: '' }); handleQuery() }

function handleAdd() {
  dialogMode.value = 'create'
  dialogTitle.value = '新增订单'
  Object.assign(form, { student: null, course: null, quantity: 1, amount: 0, discount: 0, final_amount: 0, payment_type: 'wechat', status: 'pending' })
  dialogVisible.value = true
}

function handleView(row) {
  dialogMode.value = 'detail'
  dialogTitle.value = '订单详情'
  currentOrder.value = row
  dialogVisible.value = true
}

function handleApplyRefund(row) {
  dialogMode.value = 'refund'
  dialogTitle.value = '申请退款'
  currentOrder.value = row
  Object.assign(refundForm, { amount: Number(row.final_amount), reason: '' })
  dialogVisible.value = true
}

async function submitOrder() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    await api.post('/finance/orders/', form)
    ElMessage.success('订单创建成功')
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    const data = e.response?.data
    const message = data?.course?.[0] || data?.student?.[0] || data?.final_amount?.[0] || '订单创建失败'
    ElMessage.error(message)
  }
}

async function submitRefund() {
  if (!refundFormRef.value) return
  const valid = await refundFormRef.value.validate().catch(() => false)
  if (!valid) return
  try {
    await api.post(`/finance/orders/${currentOrder.value.id}/apply_refund/`, refundForm)
    ElMessage.success('退款申请已提交')
    dialogVisible.value = false
  } catch (e) {
    const data = e.response?.data
    const message = data?.error || data?.reason?.[0] || '退款申请失败'
    ElMessage.error(message)
  }
}

async function handlePay(row) {
  try {
    await ElMessageBox.confirm('确认支付该订单?', '提示', { type: 'info' })
    await api.post(`/finance/orders/${row.id}/pay/`)
    ElMessage.success('支付成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '订单支付失败')) }
}

async function handleCancel(row) {
  try {
    await ElMessageBox.confirm('确定取消该订单吗?', '提示', { type: 'warning' })
    await api.post(`/finance/orders/${row.id}/cancel/`)
    ElMessage.success('取消成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '取消订单失败')) }
}

onMounted(async () => { await fetchOptions(); fetchData() })
</script>

<style scoped>
.order-page { padding: 20px; }
.two-col-form { display: grid; grid-template-columns: 1fr 1fr; column-gap: 18px; }
.two-col-form :deep(.el-form-item) { margin-bottom: 18px; }
.single-col-form :deep(.el-form-item) { margin-bottom: 18px; }
@media (max-width: 900px) {
  .two-col-form { grid-template-columns: 1fr; }
}
</style>
