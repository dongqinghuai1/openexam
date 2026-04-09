<template>
  <div class="dashboard">
    <section class="hero-panel">
      <div class="hero-copy">
        <span class="eyebrow">LIVE OPERATIONS</span>
        <h1>今天的教务、课堂、考试与财务都在这一块面板上。</h1>
        <p>这是运营驾驶舱，而不是普通的后台首页。关注实时班级状态、今日收入与最近通知，把一线动作和管理决策放在同一视野里。</p>
      </div>
      <div class="hero-summary">
        <div class="summary-card accent">
          <span>今日收入</span>
          <strong>¥{{ stats.todayRevenue }}</strong>
        </div>
        <div class="summary-card">
          <span>已支付订单</span>
          <strong>{{ monthSummary.paidOrderCount }}</strong>
        </div>
        <div class="summary-card">
          <span>已退款订单</span>
          <strong>{{ monthSummary.refundedOrderCount }}</strong>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <article class="metric-card">
        <div class="metric-label">学生总数</div>
        <div class="metric-value">{{ stats.studentCount }}</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">教师总数</div>
        <div class="metric-value">{{ stats.teacherCount }}</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">班级数量</div>
        <div class="metric-value">{{ stats.classCount }}</div>
      </article>
      <article class="metric-card accent-line">
        <div class="metric-label">本月退款</div>
        <div class="metric-value">{{ monthSummary.refundedOrderCount }}</div>
      </article>
    </section>

    <section class="board-grid">
      <el-card>
        <template #header><span>最近报名</span></template>
        <el-table :data="recentEnrollments" style="width: 100%">
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="phone" label="手机号" />
          <el-table-column prop="course" label="课程" />
          <el-table-column prop="date" label="报名日期" />
        </el-table>
      </el-card>

      <el-card>
        <template #header><span>今日课程</span></template>
        <el-table :data="todaySchedules" style="width: 100%">
          <el-table-column prop="time" label="时间" />
          <el-table-column prop="className" label="班级" />
          <el-table-column prop="course" label="课程" />
          <el-table-column prop="teacher" label="教师" />
        </el-table>
      </el-card>
    </section>

    <section class="board-grid compact">
      <el-card>
        <template #header><span>最近通知</span></template>
        <el-empty v-if="notifications.length === 0" description="暂无已发布通知" />
        <el-timeline v-else>
          <el-timeline-item v-for="item in notifications" :key="item.id" :timestamp="item.published_at" :type="item.level === 'urgent' ? 'danger' : item.level === 'warning' ? 'warning' : 'primary'">
            <div class="timeline-title">{{ item.title }}</div>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card>
        <template #header><span>本月概览</span></template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="已支付订单数">{{ monthSummary.paidOrderCount }}</el-descriptions-item>
          <el-descriptions-item label="已退款订单数">{{ monthSummary.refundedOrderCount }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const stats = ref({ studentCount: 0, teacherCount: 0, classCount: 0, todayRevenue: 0 })
const recentEnrollments = ref([])
const todaySchedules = ref([])
const notifications = ref([])
const monthSummary = ref({ paidOrderCount: 0, refundedOrderCount: 0 })

async function fetchDashboard() {
  try {
    const res = await api.get('/users/dashboard/')
    stats.value = res.data.stats || stats.value
    recentEnrollments.value = res.data.recentEnrollments || []
    todaySchedules.value = res.data.todaySchedules || []
    notifications.value = res.data.notifications || []
    monthSummary.value = res.data.monthSummary || monthSummary.value
  } catch (e) {
    ElMessage.error(extractErrorMessage(e, '获取看板数据失败'))
  }
}

onMounted(fetchDashboard)
</script>

<style scoped>
.dashboard { padding: 8px 0 24px; }
.hero-panel {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 20px;
  padding: 28px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 32px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.82));
  margin-bottom: 20px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}
.eyebrow { display: inline-block; padding: 8px 12px; border-radius: 999px; letter-spacing: 0.12em; font-size: 12px; color: #2563eb; background: rgba(37, 99, 235, 0.08); }
.hero-copy h1 { margin-top: 18px; max-width: 720px; font-size: clamp(30px, 4vw, 54px); line-height: 1.05; color: #0f172a; letter-spacing: -0.04em; }
.hero-copy p { margin-top: 14px; max-width: 680px; line-height: 1.8; color: #667085; font-size: 16px; }
.hero-summary { display: grid; gap: 14px; }
.summary-card { padding: 18px 20px; border-radius: 20px; background: rgba(255,255,255,0.9); border: 1px solid rgba(15,23,42,0.06); }
.summary-card span { display: block; font-size: 12px; letter-spacing: 0.1em; color: #98a2b3; text-transform: uppercase; }
.summary-card strong { display: block; margin-top: 12px; font-size: 34px; color: #0f172a; letter-spacing: -0.03em; }
.summary-card.accent { background: rgba(37,99,235,0.06); border-color: rgba(37,99,235,0.12); }
.metrics-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; margin-bottom: 20px; }
.metric-card { padding: 22px; border-radius: 24px; background: rgba(255,255,255,0.82); border: 1px solid rgba(15,23,42,0.06); box-shadow: 0 8px 24px rgba(15,23,42,0.04); }
.metric-label { color: #98a2b3; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; }
.metric-value { margin-top: 16px; font-size: 40px; font-weight: 700; color: #111827; letter-spacing: -0.04em; }
.accent-line { border-color: rgba(37,99,235,0.12); }
.board-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.board-grid.compact { align-items: start; }
.timeline-title { font-weight: 600; color: #111827; }

@media (max-width: 960px) {
  .hero-panel,
  .metrics-grid,
  .board-grid {
    grid-template-columns: 1fr;
  }
}
</style>
