<template>
  <div class="dashboard openexam-fade-in">
    <section class="hero-panel openexam-hover-lift">
      <div class="hero-copy">
        <span class="eyebrow">教务管理系统</span>
        <h1>OpenExam 教育管理平台</h1>
        <p>一站式管理教务、课堂、考试与财务，实时掌握学校运营状态，提升管理效率。</p>
      </div>
      <div class="hero-summary">
        <div class="summary-card accent openexam-hover-scale">
          <div class="summary-icon">
            <i class="el-icon-money"></i>
          </div>
          <span>今日收入</span>
          <strong>¥{{ stats.todayRevenue }}</strong>
        </div>
        <div class="summary-card openexam-hover-scale">
          <div class="summary-icon">
            <i class="el-icon-check"></i>
          </div>
          <span>已支付订单</span>
          <strong>{{ monthSummary.paidOrderCount }}</strong>
        </div>
        <div class="summary-card openexam-hover-scale">
          <div class="summary-icon">
            <i class="el-icon-refresh"></i>
          </div>
          <span>已退款订单</span>
          <strong>{{ monthSummary.refundedOrderCount }}</strong>
        </div>
      </div>
    </section>

    <section class="metrics-grid">
      <article class="metric-card openexam-hover-lift">
        <div class="metric-icon student-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="metric-label">学生总数</div>
        <div class="metric-value">{{ stats.studentCount }}</div>
      </article>
      <article class="metric-card openexam-hover-lift">
        <div class="metric-icon teacher-icon">
          <i class="el-icon-s-custom"></i>
        </div>
        <div class="metric-label">教师总数</div>
        <div class="metric-value">{{ stats.teacherCount }}</div>
      </article>
      <article class="metric-card openexam-hover-lift">
        <div class="metric-icon class-icon">
          <i class="el-icon-s-grid"></i>
        </div>
        <div class="metric-label">班级数量</div>
        <div class="metric-value">{{ stats.classCount }}</div>
      </article>
      <article class="metric-card accent-line openexam-hover-lift">
        <div class="metric-icon refund-icon">
          <i class="el-icon-s-remove"></i>
        </div>
        <div class="metric-label">本月退款</div>
        <div class="metric-value">{{ monthSummary.refundedOrderCount }}</div>
      </article>
    </section>

    <section class="board-grid">
      <el-card class="base-card openexam-hover-lift">
        <template #header>
          <div class="card-header">
            <span>最近报名</span>
            <el-button type="primary" size="small" class="openexam-btn">
              <i class="el-icon-plus"></i> 新增报名
            </el-button>
          </div>
        </template>
        <el-table :data="recentEnrollments" style="width: 100%" class="table">
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="phone" label="手机号" />
          <el-table-column prop="course" label="课程" />
          <el-table-column prop="date" label="报名日期" />
        </el-table>
      </el-card>

      <el-card class="base-card openexam-hover-lift">
        <template #header>
          <div class="card-header">
            <span>今日课程</span>
            <el-button type="primary" size="small" class="openexam-btn">
              <i class="el-icon-calendar"></i> 查看日历
            </el-button>
          </div>
        </template>
        <el-table :data="todaySchedules" style="width: 100%" class="table">
          <el-table-column prop="time" label="时间" />
          <el-table-column prop="className" label="班级" />
          <el-table-column prop="course" label="课程" />
          <el-table-column prop="teacher" label="教师" />
        </el-table>
      </el-card>
    </section>

    <section class="board-grid compact">
      <el-card class="base-card openexam-hover-lift">
        <template #header>
          <div class="card-header">
            <span>最近通知</span>
            <el-button type="primary" size="small" class="openexam-btn">
              <i class="el-icon-message"></i> 发布通知
            </el-button>
          </div>
        </template>
        <el-empty v-if="notifications.length === 0" description="暂无已发布通知" />
        <el-timeline v-else class="notification-timeline">
          <el-timeline-item v-for="item in notifications" :key="item.id" :timestamp="item.published_at" :type="item.level === 'urgent' ? 'danger' : item.level === 'warning' ? 'warning' : 'primary'">
            <div class="timeline-title">{{ item.title }}</div>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card class="base-card openexam-hover-lift">
        <template #header>
          <div class="card-header">
            <span>本月概览</span>
            <el-button type="primary" size="small" class="openexam-btn">
              <i class="el-icon-data-analysis"></i> 详细报表
            </el-button>
          </div>
        </template>
        <el-descriptions :column="1" border class="monthly-overview">
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
.dashboard {
  padding: var(--openexam-space-4) 0 var(--openexam-space-6);
}

.hero-panel {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: var(--openexam-space-5);
  padding: var(--openexam-space-8);
  border: 1px solid var(--openexam-border);
  border-radius: var(--openexam-radius-2xl);
  background: linear-gradient(135deg, var(--openexam-bg-primary), var(--openexam-bg-secondary));
  margin-bottom: var(--openexam-space-6);
  box-shadow: var(--openexam-shadow-lg);
  transition: all var(--openexam-transition-fast);
}

.eyebrow {
  display: inline-block;
  padding: var(--openexam-space-2) var(--openexam-space-3);
  border-radius: var(--openexam-radius-full);
  letter-spacing: 0.12em;
  font-size: var(--openexam-font-xs);
  color: var(--openexam-primary);
  background: var(--openexam-primary-light);
  font-weight: var(--openexam-font-medium);
}

.hero-copy h1 {
  margin-top: var(--openexam-space-5);
  max-width: 720px;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.05;
  color: var(--openexam-text-primary);
  letter-spacing: -0.04em;
  font-weight: var(--openexam-font-bold);
}

.hero-copy p {
  margin-top: var(--openexam-space-4);
  max-width: 680px;
  line-height: 1.8;
  color: var(--openexam-text-secondary);
  font-size: var(--openexam-font-base);
}

.hero-summary {
  display: grid;
  gap: var(--openexam-space-4);
}

.summary-card {
  padding: var(--openexam-space-5);
  border-radius: var(--openexam-radius-xl);
  background: var(--openexam-bg-primary);
  border: 1px solid var(--openexam-border);
  box-shadow: var(--openexam-shadow);
  transition: all var(--openexam-transition-fast);
  position: relative;
  overflow: hidden;
}

.summary-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--openexam-primary), var(--openexam-secondary));
  opacity: 0;
  transition: opacity var(--openexam-transition-fast);
}

.summary-card:hover::before {
  opacity: 1;
}

.summary-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--openexam-radius-full);
  background: var(--openexam-primary-light);
  color: var(--openexam-primary);
  font-size: 18px;
  margin-bottom: var(--openexam-space-3);
}

.summary-card span {
  display: block;
  font-size: var(--openexam-font-xs);
  letter-spacing: 0.1em;
  color: var(--openexam-text-tertiary);
  text-transform: uppercase;
  font-weight: var(--openexam-font-medium);
}

.summary-card strong {
  display: block;
  margin-top: var(--openexam-space-3);
  font-size: 2.25rem;
  color: var(--openexam-text-primary);
  letter-spacing: -0.03em;
  font-weight: var(--openexam-font-bold);
}

.summary-card.accent {
  background: var(--openexam-primary-light);
  border-color: var(--openexam-primary);
}

.summary-card.accent .summary-icon {
  background: var(--openexam-primary);
  color: white;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--openexam-space-5);
  margin-bottom: var(--openexam-space-6);
}

.metric-card {
  padding: var(--openexam-space-6);
  border-radius: var(--openexam-radius-xl);
  background: var(--openexam-bg-primary);
  border: 1px solid var(--openexam-border);
  box-shadow: var(--openexam-shadow);
  transition: all var(--openexam-transition-fast);
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--openexam-primary), var(--openexam-secondary));
  opacity: 0;
  transition: opacity var(--openexam-transition-fast);
}

.metric-card:hover::before {
  opacity: 1;
}

.metric-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: var(--openexam-radius-full);
  font-size: 20px;
  margin-bottom: var(--openexam-space-4);
}

.student-icon {
  background: var(--openexam-primary-light);
  color: var(--openexam-primary);
}

.teacher-icon {
  background: var(--openexam-secondary-light);
  color: var(--openexam-secondary);
}

.class-icon {
  background: var(--openexam-success-light);
  color: var(--openexam-success);
}

.refund-icon {
  background: var(--openexam-danger-light);
  color: var(--openexam-danger);
}

.metric-label {
  color: var(--openexam-text-secondary);
  font-size: var(--openexam-font-sm);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: var(--openexam-font-medium);
}

.metric-value {
  margin-top: var(--openexam-space-4);
  font-size: 2.5rem;
  font-weight: var(--openexam-font-bold);
  color: var(--openexam-text-primary);
  letter-spacing: -0.04em;
}

.accent-line {
  border-color: var(--openexam-primary);
}

.board-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--openexam-space-5);
  margin-top: var(--openexam-space-6);
}

.board-grid.compact {
  align-items: start;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.card-header span {
  font-size: var(--openexam-font-lg);
  font-weight: var(--openexam-font-semibold);
  color: var(--openexam-text-primary);
}

.notification-timeline .el-timeline-item__node {
  width: 16px;
  height: 16px;
}

.timeline-title {
  font-weight: var(--openexam-font-semibold);
  color: var(--openexam-text-primary);
  margin-left: var(--openexam-space-3);
}

.monthly-overview .el-descriptions__label {
  font-weight: var(--openexam-font-medium);
  color: var(--openexam-text-secondary);
}

.monthly-overview .el-descriptions__content {
  font-weight: var(--openexam-font-semibold);
  color: var(--openexam-text-primary);
}

@media (max-width: 960px) {
  .hero-panel,
  .metrics-grid,
  .board-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-panel {
    padding: var(--openexam-space-6);
  }
  
  .hero-copy h1 {
    font-size: 1.75rem;
  }
  
  .metric-value {
    font-size: 2rem;
  }
}

@media (max-width: 576px) {
  .hero-panel {
    padding: var(--openexam-space-4);
  }
  
  .hero-copy h1 {
    font-size: 1.5rem;
  }
  
  .summary-card strong {
    font-size: 1.75rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
  
  .metric-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
}
</style>
