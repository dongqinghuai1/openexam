import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/layout/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/Dashboard.vue'),
        meta: { title: '数据看板', icon: 'DataAnalysis', permission: 'dashboard_view' }
      },
      {
        path: 'system',
        name: 'System',
        meta: { title: '系统管理', icon: 'Setting', permission: 'system_management' },
        children: [
          {
            path: 'users',
            name: 'UserManagement',
            component: () => import('../views/system/user/User.vue'),
            meta: { title: '用户管理', permission: 'user_management' }
          },
          {
            path: 'roles',
            name: 'RoleManagement',
            component: () => import('../views/system/role/Role.vue'),
            meta: { title: '角色管理', permission: 'role_management' }
          },
          {
            path: 'menus',
            name: 'MenuManagement',
            component: () => import('../views/system/menu/Menu.vue'),
            meta: { title: '菜单管理', permission: 'menu_management' }
          },
          {
            path: 'logs',
            name: 'OperationLogManagement',
            component: () => import('../views/system/log/OperationLog.vue'),
            meta: { title: '操作日志', permission: 'log_management' }
          },
          {
            path: 'notifications',
            name: 'NotificationManagement',
            component: () => import('../views/system/notification/Notification.vue'),
            meta: { title: '通知消息', permission: 'notification_management' }
          }
        ]
      },
      {
        path: 'edu',
        name: 'Education',
        meta: { title: '教务管理', icon: 'School', permission: 'education_management' },
        children: [
          {
            path: 'students',
            name: 'StudentManagement',
            component: () => import('../views/edu/student/Student.vue'),
            meta: { title: '学生管理', permission: 'student_management' }
          },
          {
            path: 'teachers',
            name: 'TeacherManagement',
            component: () => import('../views/edu/teacher/Teacher.vue'),
            meta: { title: '教师管理', permission: 'teacher_management' }
          },
          {
            path: 'courses',
            name: 'CourseManagement',
            component: () => import('../views/edu/course/Course.vue'),
            meta: { title: '课程管理', permission: 'course_management' }
          },
          {
            path: 'classes',
            name: 'ClassManagement',
            component: () => import('../views/edu/class/Class.vue'),
            meta: { title: '班级管理', permission: 'class_management' }
          },
          {
            path: 'schedules',
            name: 'ScheduleManagement',
            component: () => import('../views/edu/schedule/Schedule.vue'),
            meta: { title: '排课管理', permission: 'schedule_management' }
          }
        ]
      },
      {
        path: 'classroom',
        name: 'Classroom',
        meta: { title: '在线课堂', icon: 'VideoCamera', permission: 'classroom_management' },
        children: [
          {
            path: 'list',
            name: 'ClassroomList',
            component: () => import('../views/classroom/List.vue'),
            meta: { title: '课堂列表', permission: 'classroom_view' }
          },
          {
            path: 'records',
            name: 'RecordingList',
            component: () => import('../views/classroom/Recording.vue'),
            meta: { title: '录屏回放', permission: 'recording_view' }
          }
        ]
      },
      {
        path: 'finance',
        name: 'Finance',
        meta: { title: '财务管理', icon: 'Money', permission: 'finance_management' },
        children: [
          {
            path: 'orders',
            name: 'OrderManagement',
            component: () => import('../views/finance/order/Order.vue'),
            meta: { title: '订单管理', permission: 'order_management' }
          },
          {
            path: 'refunds',
            name: 'RefundManagement',
            component: () => import('../views/finance/refund/Refund.vue'),
            meta: { title: '退款管理', permission: 'refund_management' }
          }
        ]
      },
      {
        path: 'exam',
        name: 'Exam',
        meta: { title: '考试管理', icon: 'Reading', permission: 'exam_management' },
        children: [
          {
            path: 'questions',
            name: 'QuestionManagement',
            component: () => import('../views/exam/question/Question.vue'),
            meta: { title: '题库管理', permission: 'question_management' }
          },
          {
            path: 'papers',
            name: 'PaperManagement',
            component: () => import('../views/exam/paper/Paper.vue'),
            meta: { title: '试卷管理', permission: 'paper_management' }
          },
          {
            path: 'exams',
            name: 'ExamManagement',
            component: () => import('../views/exam/exam/Exam.vue'),
            meta: { title: '考试管理', permission: 'exam_management' }
          },
          {
            path: 'scores',
            name: 'ScoreManagement',
            component: () => import('../views/exam/score/Score.vue'),
            meta: { title: '成绩管理', permission: 'score_view' }
          }
        ]
      },
      {
        path: 'statistics',
        name: 'Statistics',
        meta: { title: '统计分析', icon: 'PieChart', permission: 'statistics_view' },
        children: [
          {
            path: 'revenue',
            name: 'RevenueStatistics',
            component: () => import('../views/statistics/Revenue.vue'),
            meta: { title: '收入统计', permission: 'revenue_statistics' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.path !== '/login' && !userStore.token) {
    next('/login')
  } else if (to.path === '/login' && userStore.token) {
    if (userStore.isAdminConsoleUser) {
      next('/')
    } else {
      userStore.logout()
      next('/login')
    }
  } else {
    if (to.path !== '/login' && userStore.token && !userStore.isAdminConsoleUser) {
      window.alert('当前账号不是管理员，不能进入管理后台，请使用对应的教师端、学生端或家长端登录。')
      userStore.logout()
      next('/login')
      return
    }
    
    // 检查权限
    if (to.path !== '/login') {
      const hasPermission = checkPermission(to)
      if (!hasPermission) {
        ElMessage.error('权限不足，无法访问该页面')
        next(from.path || '/')
        return
      }
    }
    
    next()
  }
})

// 检查权限
function checkPermission(route) {
  const userStore = useUserStore()
  
  // 超级管理员拥有所有权限
  if (userStore.userInfo?.is_superuser) {
    return true
  }
  
  // 检查路由是否需要权限
  if (!route.meta || !route.meta.permission) {
    return true
  }
  
  // 检查用户是否有该权限
  const userPermissions = getUserPermissions()
  return userPermissions.includes(route.meta.permission)
}

// 获取用户权限
function getUserPermissions() {
  const userStore = useUserStore()
  const permissions = new Set()
  
  // 从用户角色中获取权限
  if (userStore.userInfo?.roles) {
    userStore.userInfo.roles.forEach(role => {
      if (role.permissions) {
        role.permissions.forEach(permission => {
          permissions.add(permission.code)
        })
      }
    })
  }
  
  return Array.from(permissions)
}

export default router
