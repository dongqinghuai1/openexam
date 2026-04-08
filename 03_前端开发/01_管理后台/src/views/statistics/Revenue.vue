<template>
  <div class="statistics-page">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.todayRevenue }}</div>
            <div class="stat-label">今日收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.monthRevenue }}</div>
            <div class="stat-label">本月收入</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.todayOrders }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ stats.monthOrders }}</div>
            <div class="stat-label">本月订单</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>收入趋势</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="fetchChartData"
          />
        </div>
      </template>
      <div ref="chartRef" style="height: 350px"></div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header><span>课程销售排行</span></template>
          <el-table :data="courseStats" stripe>
            <el-table-column prop="name" label="课程名称" />
            <el-table-column prop="orderCount" label="订单数" width="100" />
            <el-table-column prop="revenue" label="收入" width="100">
              <template #default="{ row }">¥{{ row.revenue }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>支付方式分布</span></template>
          <div ref="pieChartRef" style="height: 250px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'
import * as echarts from 'echarts'

const stats = ref({
  todayRevenue: '12,800',
  monthRevenue: '286,500',
  todayOrders: 15,
  monthOrders: 156
})

const dateRange = ref([])
const chartRef = ref(null)
const pieChartRef = ref(null)
const courseStats = ref([
  { name: 'Python入门', orderCount: 45, revenue: 45000 },
  { name: 'Java基础', orderCount: 38, revenue: 38000 },
  { name: 'Web前端', orderCount: 32, revenue: 32000 },
  { name: '数据结构', orderCount: 25, revenue: 25000 }
])

let chart = null
let pieChart = null

function initChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value', name: '收入(元)' },
    series: [{
      name: '收入',
      type: 'line',
      data: [8200, 9320, 9010, 13400, 12900, 15200, 12800],
      smooth: true,
      areaStyle: { color: 'rgba(64, 158, 255, 0.2)' }
    }]
  })
}

function initPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 1048, name: '微信' },
        { value: 735, name: '支付宝' },
        { value: 580, name: '线下' }
      ]
    }]
  })
}

async function fetchChartData() {
  try {
    const res = await api.get('/finance/orders/statistics/', {
      params: {
        start_date: dateRange.value?.[0] || '',
        end_date: dateRange.value?.[1] || ''
      }
    })
    // 更新图表数据
  } catch (e) { console.error(e) }
}

onMounted(() => {
  initChart()
  initPieChart()
  fetchChartData()
})
</script>

<style scoped>
.statistics-page { padding: 20px; }
.stat-card { text-align: center; padding: 20px; }
.stat-value { font-size: 28px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 14px; color: #999; margin-top: 10px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>