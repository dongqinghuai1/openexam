import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

/**
 * 检查用户是否有指定权限
 * @param {string} permissionCode - 权限编码
 * @returns {boolean} - 是否有权限
 */
export function checkPermission(permissionCode) {
  const userStore = useUserStore()
  
  // 超级管理员拥有所有权限
  if (userStore.userInfo?.is_superuser) {
    return true
  }
  
  // 获取用户权限
  const userPermissions = getUserPermissions()
  return userPermissions.includes(permissionCode)
}

/**
 * 获取用户所有权限
 * @returns {Array} - 权限编码数组
 */
export function getUserPermissions() {
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

/**
 * 检查权限并执行操作
 * @param {string} permissionCode - 权限编码
 * @param {Function} callback - 有权限时执行的回调函数
 * @returns {boolean} - 是否执行了操作
 */
export function checkPermissionAndExecute(permissionCode, callback) {
  if (checkPermission(permissionCode)) {
    callback()
    return true
  } else {
    ElMessage.error('权限不足，无法执行该操作')
    return false
  }
}

/**
 * 检查是否有多个权限中的任意一个
 * @param {Array} permissionCodes - 权限编码数组
 * @returns {boolean} - 是否有任意一个权限
 */
export function hasAnyPermission(permissionCodes) {
  if (typeof permissionCodes === 'string') {
    permissionCodes = [permissionCodes]
  }
  return permissionCodes.some(code => checkPermission(code))
}

/**
 * 检查是否拥有所有指定权限
 * @param {Array} permissionCodes - 权限编码数组
 * @returns {boolean} - 是否拥有所有权限
 */
export function hasAllPermissions(permissionCodes) {
  if (typeof permissionCodes === 'string') {
    permissionCodes = [permissionCodes]
  }
  return permissionCodes.every(code => checkPermission(code))
}

/**
 * 权限检查指令
 */
export const permissionDirective = {
  mounted(el, binding) {
    const { value } = binding
    if (!checkPermission(value)) {
      el.style.display = 'none'
    }
  },
  updated(el, binding) {
    const { value } = binding
    if (!checkPermission(value)) {
      el.style.display = 'none'
    } else {
      el.style.display = ''
    }
  }
}

// 路由权限映射
export const routePermissionMap = {
  '/dashboard': 'dashboard_view',
  '/system/users': 'user_management',
  '/system/roles': 'role_management',
  '/system/menus': 'menu_management',
  '/system/logs': 'log_management',
  '/system/notifications': 'notification_management',
  '/edu/students': 'student_management',
  '/edu/teachers': 'teacher_management',
  '/edu/courses': 'course_management',
  '/edu/classes': 'class_management',
  '/edu/schedules': 'schedule_management',
  '/classroom/list': 'classroom_view',
  '/classroom/records': 'recording_view',
  '/finance/orders': 'order_management',
  '/finance/refunds': 'refund_management',
  '/exam/questions': 'question_management',
  '/exam/papers': 'paper_management',
  '/exam/exams': 'exam_management',
  '/exam/scores': 'score_view',
  '/statistics/revenue': 'revenue_statistics',
}

/**
 * 检查路由权限
 * @param {string} path - 路由路径
 * @returns {boolean} - 是否有权限访问
 */
export function checkRoutePermission(path) {
  const userStore = useUserStore()
  
  // 超级管理员拥有所有权限
  if (userStore.userInfo?.is_superuser) {
    return true
  }
  
  // 检查路由权限映射
  const requiredPermission = routePermissionMap[path]
  if (!requiredPermission) {
    return true // 没有配置的路由默认放行
  }
  
  return checkPermission(requiredPermission)
}