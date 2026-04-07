<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409EFF">
            <el-icon :size="30"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.studentCount }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67C23A">
            <el-icon :size="30"><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.teacherCount }}</div>
            <div class="stat-label">教师总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #E6A23C">
            <el-icon :size="30"><School /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.classCount }}</div>
            <div class="stat-label">班级数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #F56C6C">
            <el-icon :size="30"><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.todayRevenue }}</div>
            <div class="stat-label">今日收入</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近报名</span>
          </template>
          <el-table :data="recentEnrollments" style="width: 100%">
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="phone" label="手机号" />
            <el-table-column prop="course" label="课程" />
            <el-table-column prop="date" label="报名日期" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日课程</span>
          </template>
          <el-table :data="todaySchedules" style="width: 100%">
            <el-table-column prop="time" label="时间" />
            <el-table-column prop="className" label="班级" />
            <el-table-column prop="course" label="课程" />
            <el-table-column prop="teacher" label="教师" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref({
  studentCount: 156,
  teacherCount: 28,
  classCount: 15,
  todayRevenue: 12800
})

const recentEnrollments = ref([
  { name: '张三', phone: '13800138000', course: 'Python入门', date: '2024-01-15' },
  { name: '李四', phone: '13800138001', course: 'Java基础', date: '2024-01-14' },
  { name: '王五', phone: '13800138002', course: 'Web前端', date: '2024-01-13' }
])

const todaySchedules = ref([
  { time: '09:00-10:30', className: 'Python基础班', course: 'Python基础', teacher: '张老师' },
  { time: '14:00-15:30', className: 'Java进阶班', course: 'Java进阶', teacher: '李老师' }
])
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 5px;
}
</style>