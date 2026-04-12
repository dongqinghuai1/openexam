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