<template>
  <el-container class="layout-container">
    <el-aside width="264px" class="layout-aside">
      <div class="logo">
        <div class="logo-mark">EA</div>
        <div class="logo-copy">
          <strong>OPENEXAM</strong>
          <span>Operations Console</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        :unique-opened="true"
        background-color="transparent"
        text-color="#667085"
        active-text-color="#111827"
        class="side-menu"
      >
        <template v-for="route in menus">
          <el-sub-menu v-if="route.children" :key="route.path" :index="route.path">
            <template #title>
              <el-icon><component :is="route.meta.icon" /></el-icon>
              <span>{{ route.meta.title }}</span>
            </template>
            <el-menu-item v-for="child in route.children" :key="child.path" :index="route.path + '/' + child.path">
              {{ child.meta.title }}
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :key="route.path" :index="route.path">
            <el-icon><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <div class="header-title">{{ currentRoute.meta?.title || '控制台' }}</div>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute">{{ currentRoute.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <div class="status-pill">OPENEXAM / PRODUCTION UI</div>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userInfo?.username || '用户' }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 检查用户是否有访问权限
function hasPermission(route) {
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

// 过滤菜单，只显示用户有权限的菜单项
function filterMenus(routes) {
  return routes.filter(route => {
    // 检查当前路由是否有权限
    if (!hasPermission(route)) {
      return false
    }
    
    // 检查子路由
    if (route.children && route.children.length > 0) {
      route.children = filterMenus(route.children)
      // 如果子路由都没有权限，则隐藏当前路由
      return route.children.length > 0
    }
    
    return true
  })
}

const menus = computed(() => {
  const allRoutes = router.getRoutes().filter(r => r.meta?.title && r.meta?.icon && !r.meta?.hidden)
  return filterMenus(allRoutes)
})

const activeMenu = computed(() => route.path)

const currentRoute = computed(() => route)

function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: transparent;
}

.layout-aside {
  overflow: hidden;
  padding: 18px 14px;
  background: rgba(255, 255, 255, 0.84);
  border-right: 1px solid rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(16px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 14px 22px;
}

.logo-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #0f172a, #334155);
}

.logo-copy strong {
  display: block;
  font-size: 19px;
  color: #111827;
  letter-spacing: -0.02em;
}

.logo-copy span {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: #98a2b3;
  text-transform: uppercase;
}

.side-menu {
  border-right: none;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
  padding: 0 28px;
  backdrop-filter: blur(16px);
}

.header-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 6px;
  letter-spacing: -0.03em;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-pill {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(0, 113, 227, 0.06);
  border: 1px solid rgba(0, 113, 227, 0.1);
  color: #0071e3;
  font-size: 12px;
  letter-spacing: 0.14em;
}

.header-right .user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.06);
}

:deep(.side-menu .el-sub-menu__title),
:deep(.side-menu .el-menu-item) {
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #475467 !important;
}

:deep(.side-menu .el-sub-menu__title .el-icon),
:deep(.side-menu .el-menu-item .el-icon) {
  width: 18px;
  height: 18px;
  margin-right: 2px;
  color: #94a3b8;
}

:deep(.side-menu .el-menu-item.is-active),
:deep(.side-menu .el-sub-menu__title:hover),
:deep(.side-menu .el-menu-item:hover) {
  color: #111827 !important;
}

:deep(.side-menu .el-menu-item.is-active .el-icon) {
  color: #2563eb !important;
}

.layout-main {
  padding: 22px;
  background: transparent;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  border-radius: 14px;
  margin-bottom: 6px;
}

:deep(.el-menu-item.is-active) {
  background: rgba(0, 113, 227, 0.08) !important;
}

:deep(.el-breadcrumb__inner) {
  color: #98a2b3 !important;
}
</style>
