import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

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
      <View className='stats-grid'>
        <View className='stat-card'><Text className='stat-label'>孩子人数</Text><Text className='stat-value'>{children.length}</Text></View>
        <View className='stat-card'><Text className='stat-label'>今日课程</Text><Text className='stat-value'>{schedules.length}</Text></View>
      </View>

      <View className='panel'>
        <View className='panel-head'>
          <Text className='panel-title'>孩子概览</Text>
          <Text className='panel-subtitle'>查看当前在读孩子的基础信息</Text>
        </View>
        {children.length > 0 ? children.map((child) => (
          <View className='list-row' key={child.id}>
            <View className='list-main'>
              <Text className='list-title'>{child.name}</Text>
              <Text className='list-desc'>年级: {child.grade} | 学校: {child.school || '-'}</Text>
            </View>
          </View>
        )) : <Text className='empty'>暂无绑定孩子</Text>}
      </View>

      <View className='panel'>
        <View className='panel-head'>
          <Text className='panel-title'>今日课程</Text>
          <Text className='panel-subtitle'>跟踪当天课程安排与班级信息</Text>
        </View>
        {schedules.length > 0 ? schedules.map((item, index) => (
          <View className='list-row' key={index}>
            <View className='list-main'>
              <Text className='list-title'>{item.class_name}</Text>
              <Text className='list-desc'>{item.course_name} | {item.start_time?.substring(0, 5)} - {item.end_time?.substring(0, 5)}</Text>
            </View>
          </View>
        )) : <Text className='empty'>暂无今日课程</Text>}
      </View>
    </>
  )

  const handleMenuClick = (groupKey, item) => {
    setActiveGroup(groupKey)
    setActiveItem(item.key)
    if (item.action) item.action()
  }

  return (
    <View className='admin-shell'>
      <View className='aside'>
        <View className='logo'>
          <View className='logo-mark'>EA</View>
          <View>
            <Text className='logo-title'>OPENEXAM</Text>
            <Text className='logo-subtitle'>Parent Portal</Text>
          </View>
        </View>

        {groups.map((group) => (
          <View className='menu-group' key={group.key}>
            <Text className='group-title'>{group.label}</Text>
            {group.items.map((item) => (
              <View
                key={item.key}
                className={`menu-item ${activeItem === item.key ? 'active' : ''}`}
                onClick={() => handleMenuClick(group.key, item)}
              >
                <Text className='menu-text'>{item.label}</Text>
              </View>
            ))}
          </View>
        ))}
      </View>

      <View className='main'>
        <View className='topbar'>
          <View>
            <Text className='page-title'>{activeMeta.title}</Text>
            <Text className='page-desc'>{activeMeta.group} / 家长工作台</Text>
          </View>
          <View className='user-box'>
            <View className='user-chip'>
              <Text className='user-name'>{userInfo?.name || userInfo?.username || '家长'}</Text>
              <Text className='user-role'>家长</Text>
            </View>
            <Button className='logout-btn' onClick={handleLogout}>退出登录</Button>
          </View>
        </View>

        <View className='content'>
          {activeItem === 'dashboard' && renderDashboard()}
          {activeItem !== 'dashboard' && (
            <View className='panel'>
              <View className='panel-head'>
                <Text className='panel-title'>{activeMeta.title}</Text>
                <Text className='panel-subtitle'>通过左侧导航切换家庭与学习功能</Text>
              </View>
              <Text className='empty'>已切换到 {activeMeta.title}，如需继续重构该页面，我继续直接统一到后台骨架。</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  )
}
