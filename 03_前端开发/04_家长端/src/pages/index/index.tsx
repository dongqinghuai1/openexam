import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

// 内联样式确保样式被正确应用
const styles = {
  adminShell: {
    minHeight: '100vh',
    display: 'grid',
    gridTemplateColumns: '280px minmax(0, 1fr)',
    background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
    margin: 0,
    padding: 0,
    boxSizing: 'border-box'
  },
  aside: {
    minHeight: '100vh',
    padding: '24px 20px',
    background: 'rgba(255, 255, 255, 0.95)',
    borderRight: '1px solid rgba(15, 23, 42, 0.08)',
    boxShadow: '0 0 32px rgba(0, 0, 0, 0.04)'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '14px 14px',
    borderRadius: '16px',
    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(139, 92, 246, 0.06))',
    marginBottom: '24px',
    width: '100%'
  },
  logoMark: {
    width: '40px',
    height: '40px',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#fff',
    fontWeight: '700',
    fontSize: '16px',
    boxShadow: '0 6px 16px rgba(99, 102, 241, 0.3)'
  },
  logoTitle: {
    fontSize: '14px',
    fontWeight: '700',
    color: '#1e293b',
    letterSpacing: '0.02em',
    whiteSpace: 'nowrap'
  },
  logoSubtitle: {
    marginTop: '2px',
    fontSize: '10px',
    letterSpacing: '0.1em',
    color: '#94a3b8',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap'
  },
  menuGroup: {
    marginBottom: '24px'
  },
  groupTitle: {
    padding: '0 16px 12px',
    fontSize: '12px',
    color: '#94a3b8',
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    fontWeight: '600'
  },
  menuItem: {
    marginBottom: '8px',
    padding: '14px 16px',
    borderRadius: '14px',
    background: 'transparent',
    transition: 'all 0.3s ease',
    cursor: 'pointer'
  },
  menuItemActive: {
    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.12))',
    border: '1px solid rgba(99, 102, 241, 0.2)'
  },
  menuText: {
    fontSize: '14px',
    color: '#475569',
    fontWeight: '600',
    letterSpacing: '0.02em'
  },
  menuTextActive: {
    color: '#6366f1',
    fontWeight: '700'
  },
  main: {
    minWidth: 0,
    display: 'flex',
    flexDirection: 'column'
  },
  topbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '24px 32px',
    background: 'rgba(255, 255, 255, 0.95)',
    borderBottom: '1px solid rgba(15, 23, 42, 0.08)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)'
  },
  pageTitle: {
    fontSize: '32px',
    fontWeight: '700',
    color: '#1e293b',
    letterSpacing: '-0.03em'
  },
  pageDesc: {
    marginTop: '8px',
    fontSize: '14px',
    color: '#94a3b8',
    letterSpacing: '0.02em'
  },
  userBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  },
  userChip: {
    padding: '12px 16px',
    borderRadius: '999px',
    background: 'rgba(99, 102, 241, 0.06)',
    border: '1px solid rgba(99, 102, 241, 0.12)',
    transition: 'all 0.3s ease'
  },
  userName: {
    fontSize: '14px',
    fontWeight: '700',
    color: '#1e293b',
    letterSpacing: '0.02em'
  },
  userRole: {
    fontSize: '12px',
    color: '#94a3b8',
    letterSpacing: '0.02em'
  },
  logoutBtn: {
    minHeight: '40px',
    padding: '0 16px',
    borderRadius: '12px',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#fff',
    fontSize: '14px',
    fontWeight: '600',
    letterSpacing: '0.02em',
    transition: 'all 0.3s ease',
    border: 'none'
  },
  content: {
    padding: '32px'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '20px',
    marginBottom: '24px'
  },
  statCard: {
    padding: '24px 24px',
    borderRadius: '20px',
    background: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid rgba(15, 23, 42, 0.08)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.06)',
    transition: 'all 0.3s ease'
  },
  statLabel: {
    fontSize: '14px',
    color: '#64748b',
    marginBottom: '12px',
    letterSpacing: '0.02em',
    fontWeight: '600'
  },
  statValue: {
    fontSize: '36px',
    fontWeight: '700',
    color: '#1e293b',
    letterSpacing: '-0.03em',
    lineHeight: '1.2'
  },
  statValueSmall: {
    fontSize: '20px',
    color: '#6366f1',
    fontWeight: '600'
  },
  panel: {
    padding: '24px 24px',
    borderRadius: '20px',
    background: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid rgba(15, 23, 42, 0.08)',
    boxShadow: '0 12px 32px rgba(0, 0, 0, 0.06)',
    marginBottom: '24px'
  },
  panelHead: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    gap: '16px',
    marginBottom: '24px',
    paddingBottom: '16px',
    borderBottom: '1px solid rgba(15, 23, 42, 0.08)'
  },
  panelTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#1e293b',
    letterSpacing: '-0.02em'
  },
  panelSubtitle: {
    fontSize: '14px',
    color: '#94a3b8',
    letterSpacing: '0.02em'
  },
  listRow: {
    display: 'flex',
    justifyContent: 'space-between',
    gap: '20px',
    alignItems: 'center',
    padding: '20px 0',
    borderBottom: '1px solid rgba(15, 23, 42, 0.06)',
    transition: 'all 0.3s ease'
  },
  listMain: {
    flex: 1,
    minWidth: 0
  },
  listTitle: {
    fontSize: '16px',
    fontWeight: '700',
    color: '#1e293b',
    marginBottom: '6px',
    letterSpacing: '0.02em'
  },
  listDesc: {
    fontSize: '14px',
    color: '#64748b',
    lineHeight: '1.6',
    letterSpacing: '0.02em'
  },
  listActions: {
    display: 'flex',
    gap: '12px'
  },
  primaryBtn: {
    minHeight: '40px',
    padding: '0 16px',
    borderRadius: '12px',
    fontSize: '14px',
    fontWeight: '600',
    letterSpacing: '0.02em',
    transition: 'all 0.3s ease',
    border: 'none',
    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    color: '#fff',
    boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)'
  },
  ghostBtn: {
    minHeight: '40px',
    padding: '0 16px',
    borderRadius: '12px',
    fontSize: '14px',
    fontWeight: '600',
    letterSpacing: '0.02em',
    transition: 'all 0.3s ease',
    border: '1px solid rgba(99, 102, 241, 0.2)',
    background: 'rgba(255, 255, 255, 0.95)',
    color: '#6366f1'
  },
  empty: {
    padding: '40px 0',
    color: '#94a3b8',
    textAlign: 'center',
    fontSize: '14px',
    letterSpacing: '0.02em'
  }
}

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [children, setChildren] = useState<any[]>([])
  const [schedules, setSchedules] = useState<any[]>([])
  const [activeGroup, setActiveGroup] = useState('overview')
  const [activeItem, setActiveItem] = useState('dashboard')

  useEffect(() => {
    const user = Taro.getStorageSync('userInfo')
    if (user) {
      setUserInfo(user)
      fetchChildren(user)
    } else {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  }, [])

  const fetchChildren = async (user) => {
    try {
      const phone = user?.phone || user?.username
      const res = await api.get('/edu/students/', { parent_phone: phone })
      const list = res.results || res || []
      setChildren(list)
      fetchTodaySchedules(list)
    } catch (e) {
      console.error(e)
    }
  }

  const fetchTodaySchedules = async (studentList) => {
    try {
      const res = await api.get('/edu/schedules/', { date: new Date().toISOString().split('T')[0] })
      const list = res.results || res || []
      const classIds = new Set(studentList.flatMap(student => (student.class_name ? [student.class_name] : [])))
      setSchedules(list.filter(item => classIds.has(item.class_name)))
    } catch (e) {
      console.error(e)
    }
  }

  const handleLogout = () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('userInfo')
    Taro.redirectTo({ url: '/pages/login/index' })
  }

  const groups = [
    {
      key: 'overview',
      label: '家庭概览',
      items: [{ key: 'dashboard', label: '控制台' }],
    },
    {
      key: 'course',
      label: '课程跟进',
      items: [
        { key: 'calendar', label: '课程日历', action: () => Taro.navigateTo({ url: '/pages/calendar/index' }) },
        { key: 'recordings', label: '录屏回放', action: () => Taro.navigateTo({ url: '/pages/recordings/index' }) },
      ],
    },
    {
      key: 'feedback',
      label: '学习反馈',
      items: [
        { key: 'children', label: '孩子管理', action: () => Taro.navigateTo({ url: '/pages/children/index' }) },
        { key: 'scores', label: '成绩查询', action: () => Taro.navigateTo({ url: '/pages/scores/index' }) },
      ],
    },
  ]

  const activeMeta = useMemo(() => {
    for (const group of groups) {
      const found = group.items.find(item => item.key === activeItem)
      if (found) {
        return { group: group.label, title: found.label }
      }
    }
    return { group: '家庭概览', title: '控制台' }
  }, [activeItem])

  const renderDashboard = () => (
    <>
      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>孩子人数</Text>
          <Text style={styles.statValue}>{children.length}</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statLabel}>今日课程</Text>
          <Text style={styles.statValue}>{schedules.length}</Text>
        </View>
      </View>

      <View style={styles.panel}>
        <View style={styles.panelHead}>
          <Text style={styles.panelTitle}>孩子概览</Text>
          <Text style={styles.panelSubtitle}>查看当前在读孩子的基础信息</Text>
        </View>
        {children.length > 0 ? children.map((child) => (
          <View style={styles.listRow} key={child.id}>
            <View style={styles.listMain}>
              <Text style={styles.listTitle}>{child.name}</Text>
              <Text style={styles.listDesc}>年级: {child.grade} | 学校: {child.school || '-'}</Text>
            </View>
          </View>
        )) : <Text style={styles.empty}>暂无绑定孩子</Text>}
      </View>

      <View style={styles.panel}>
        <View style={styles.panelHead}>
          <Text style={styles.panelTitle}>今日课程</Text>
          <Text style={styles.panelSubtitle}>跟踪当天课程安排与班级信息</Text>
        </View>
        {schedules.length > 0 ? schedules.map((item, index) => (
          <View style={styles.listRow} key={index}>
            <View style={styles.listMain}>
              <Text style={styles.listTitle}>{item.class_name}</Text>
              <Text style={styles.listDesc}>{item.course_name} | {item.start_time?.substring(0, 5)} - {item.end_time?.substring(0, 5)}</Text>
            </View>
          </View>
        )) : <Text style={styles.empty}>暂无今日课程</Text>}
      </View>
    </>
  )

  const handleMenuClick = (groupKey, item) => {
    setActiveGroup(groupKey)
    setActiveItem(item.key)
    if (item.action) item.action()
  }

  return (
    <View style={styles.adminShell}>
      <View style={styles.aside}>
        <View style={styles.logo}>
          <View style={styles.logoMark}>OX</View>
          <View style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Text style={styles.logoTitle}>OPENEXAM</Text>
            <Text style={styles.logoSubtitle}>Parent PORTAL</Text>
          </View>
        </View>

        {groups.map((group) => (
          <View style={styles.menuGroup} key={group.key}>
            <Text style={styles.groupTitle}>{group.label}</Text>
            {group.items.map((item) => (
              <View
                key={item.key}
                style={activeItem === item.key ? { ...styles.menuItem, ...styles.menuItemActive } : styles.menuItem}
                onClick={() => handleMenuClick(group.key, item)}
              >
                <Text style={activeItem === item.key ? { ...styles.menuText, ...styles.menuTextActive } : styles.menuText}>{item.label}</Text>
              </View>
            ))}
          </View>
        ))}
      </View>

      <View style={styles.main}>
        <View style={styles.topbar}>
          <View>
            <Text style={styles.pageTitle}>{activeMeta.title}</Text>
            <Text style={styles.pageDesc}>{activeMeta.group} / 家长工作台</Text>
          </View>
          <View style={styles.userBox}>
            <View style={styles.userChip}>
              <Text style={styles.userName}>{userInfo?.name || userInfo?.username || '家长'}</Text>
              <Text style={styles.userRole}>家长</Text>
            </View>
            <Button style={styles.logoutBtn} onClick={handleLogout}>退出登录</Button>
          </View>
        </View>

        <View style={styles.content}>
          {activeItem === 'dashboard' && renderDashboard()}
          {activeItem !== 'dashboard' && (
            <View style={styles.panel}>
              <View style={styles.panelHead}>
                <Text style={styles.panelTitle}>{activeMeta.title}</Text>
                <Text style={styles.panelSubtitle}>通过左侧导航切换家庭与学习功能</Text>
              </View>
              <Text style={styles.empty}>已切换到 {activeMeta.title}，如需继续重构该页面，我继续直接统一到后台骨架。</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  )
}
