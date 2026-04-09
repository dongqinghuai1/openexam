import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

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
        meta: { title: '数据看板', icon: 'DataAnalysis' }
      },
      {
        path: 'system',
        name: 'System',
        meta: { title: '系统管理', icon: 'Setting' },
        children: [
          {
            path: 'users',
            name: 'UserManagement',
            component: () => import('../views/system/user/User.vue'),
            meta: { title: '用户管理' }
          },
          {
            path: 'roles',
            name: 'RoleManagement',
            component: () => import('../views/system/role/Role.vue'),
            meta: { title: '角色管理' }
          },
          {
            path: 'menus',
            name: 'MenuManagement',
            component: () => import('../views/system/menu/Menu.vue'),
            meta: { title: '菜单管理' }
          },
          {
            path: 'logs',
            name: 'OperationLogManagement',
            component: () => import('../views/system/log/OperationLog.vue'),
            meta: { title: '操作日志' }
          },
          {
            path: 'notifications',
            name: 'NotificationManagement',
            component: () => import('../views/system/notification/Notification.vue'),
            meta: { title: '通知消息' }
          }
        ]
      },
      {
        path: 'edu',
        name: 'Education',
        meta: { title: '教务管理', icon: 'School' },
        children: [
          {
            path: 'students',
            name: 'StudentManagement',
            component: () => import('../views/edu/student/Student.vue'),
            meta: { title: '学生管理' }
          },
          {
            path: 'teachers',
            name: 'TeacherManagement',
            component: () => import('../views/edu/teacher/Teacher.vue'),
            meta: { title: '教师管理' }
          },
          {
            path: 'courses',
            name: 'CourseManagement',
            component: () => import('../views/edu/course/Course.vue'),
            meta: { title: '课程管理' }
          },
          {
            path: 'classes',
            name: 'ClassManagement',
            component: () => import('../views/edu/class/Class.vue'),
            meta: { title: '班级管理' }
          },
          {
            path: 'schedules',
            name: 'ScheduleManagement',
            component: () => import('../views/edu/schedule/Schedule.vue'),
            meta: { title: '排课管理' }
          }
        ]
      },
      {
        path: 'classroom',
        name: 'Classroom',
        meta: { title: '在线课堂', icon: 'VideoCamera' },
        children: [
          {
            path: 'list',
            name: 'ClassroomList',
            component: () => import('../views/classroom/List.vue'),
            meta: { title: '课堂列表' }
          },
          {
            path: 'records',
            name: 'RecordingList',
            component: () => import('../views/classroom/Recording.vue'),
            meta: { title: '录屏回放' }
          }
        ]
      },
      {
        path: 'finance',
        name: 'Finance',
        meta: { title: '财务管理', icon: 'Money' },
        children: [
          {
            path: 'orders',
            name: 'OrderManagement',
            component: () => import('../views/finance/order/Order.vue'),
            meta: { title: '订单管理' }
          },
          {
            path: 'refunds',
            name: 'RefundManagement',
            component: () => import('../views/finance/refund/Refund.vue'),
            meta: { title: '退款管理' }
          }
        ]
      },
      {
        path: 'exam',
        name: 'Exam',
        meta: { title: '考试管理', icon: 'Reading' },
        children: [
          {
            path: 'questions',
            name: 'QuestionManagement',
            component: () => import('../views/exam/question/Question.vue'),
            meta: { title: '题库管理' }
          },
          {
            path: 'papers',
            name: 'PaperManagement',
            component: () => import('../views/exam/paper/Paper.vue'),
            meta: { title: '试卷管理' }
          },
          {
            path: 'exams',
            name: 'ExamManagement',
            component: () => import('../views/exam/exam/Exam.vue'),
            meta: { title: '考试管理' }
          },
          {
            path: 'scores',
            name: 'ScoreManagement',
            component: () => import('../views/exam/score/Score.vue'),
            meta: { title: '成绩管理' }
          }
        ]
      },
      {
        path: 'statistics',
        name: 'Statistics',
        meta: { title: '统计分析', icon: 'PieChart' },
        children: [
          {
            path: 'revenue',
            name: 'RevenueStatistics',
            component: () => import('../views/statistics/Revenue.vue'),
            meta: { title: '收入统计' }
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
    next()
  }
})

export default router
