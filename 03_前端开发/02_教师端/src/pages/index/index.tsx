import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [schedules, setSchedules] = useState<any[]>([])
  const [activeGroup, setActiveGroup] = useState('overview')
  const [activeItem, setActiveItem] = useState('dashboard')

  useEffect(() => {
    const user = Taro.getStorageSync('userInfo')
    if (user) {
      setUserInfo(user)
      fetchTeacherAndSchedules(user)
    } else {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  }, [])

  const fetchTeacherAndSchedules = async (user) => {
    try {
      const teacherRes = await api.get('/edu/teachers/', { phone: user.phone || user.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      if (!teacher) return
      const scheduleRes = await api.get(`/edu/teachers/${teacher.id}/schedules/`)
      setSchedules(scheduleRes || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleLogout = () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('userInfo')
    Taro.redirectTo({ url: '/pages/login/index' })
  }

  const handleStartClass = async (schedule) => {
    try {
      const meetingList = await api.get('/classroom/meeting_rooms/', { page_size: 100 })
      const meetings = meetingList.results || meetingList || []
      let meeting = meetings.find((item) => item.schedule === schedule.id || item.schedule_id === schedule.id)
      if (!meeting) {
        meeting = await api.post('/classroom/meeting_rooms/create_meeting/', { schedule_id: schedule.id })
      }
      const activeMeeting = meeting.status === 'ongoing' ? meeting : await api.post(`/classroom/meeting_rooms/${meeting.id}/start_meeting/`)
      if (activeMeeting.join_url) {
        Taro.navigateTo({
          url: `/pages/link/index?title=${encodeURIComponent('课堂入口')}&type=classroom&url=${encodeURIComponent(activeMeeting.join_url)}`
        })
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '开始上课失败', icon: 'none' })
    }
  }

  const upcomingSchedules = schedules.filter((item) => item.status === 'scheduled')

  const groups = [
    {
      key: 'overview',
      label: '工作概览',
      items: [
        { key: 'dashboard', label: '控制台' },
      ]
    },
    {
      key: 'teaching',
      label: '教学管理',
      items: [
        { key: 'schedule', label: '我的课表', action: () => Taro.navigateTo({ url: '/pages/schedule/index' }) },
        { key: 'students', label: '我的学生', action: () => Taro.navigateTo({ url: '/pages/students/index' }) },
      ]
    },
    {
      key: 'record',
      label: '教学记录',
      items: [
        { key: 'notes', label: '课堂笔记', action: () => Taro.navigateTo({ url: '/pages/notes/index' }) },
        { key: 'recordings', label: '录屏回放', action: () => Taro.navigateTo({ url: '/pages/recordings/index' }) },
        { key: 'profile', label: '个人中心', action: () => Taro.navigateTo({ url: '/pages/profile/index' }) },
      ]
    },
  ]

  const activeMeta = useMemo(() => {
    for (const group of groups) {
      const found = group.items.find(item => item.key === activeItem)
      if (found) {
        return { group: group.label, title: found.label }
      }
    }
    return { group: '工作概览', title: '控制台' }
  }, [activeItem])

  const renderDashboard = () => (
    <>
      <View className='stats-grid'>
        <View className='stat-card'><Text className='stat-label'>待上课程</Text><Text className='stat-value'>{upcomingSchedules.length}</Text></View>
        <View className='stat-card'><Text className='stat-label'>全部课次</Text><Text className='stat-value'>{schedules.length}</Text></View>
        <View className='stat-card'><Text className='stat-label'>当前状态</Text><Text className='stat-value small'>教学进行中</Text></View>
      </View>

      <View className='panel'>
        <View className='panel-head'>
          <Text className='panel-title'>近期课次</Text>
          <Text className='panel-subtitle'>优先处理最近待开始的课程</Text>
        </View>
        {upcomingSchedules.length > 0 ? upcomingSchedules.slice(0, 4).map((item) => (
          <View className='list-row' key={item.id}>
            <View className='list-main'>
              <Text className='list-title'>{item.class_name}</Text>
              <Text className='list-desc'>{item.course_name} | {item.date} {item.start_time?.substring(0, 5)} - {item.end_time?.substring(0, 5)}</Text>
            </View>
            <View className='list-actions'>
              <Button className='ghost-btn' onClick={() => Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${item.id}` })}>详情</Button>
              <Button className='primary-btn' onClick={() => handleStartClass(item)}>开始上课</Button>
            </View>
          </View>
        )) : <Text className='empty'>暂无待上课程</Text>}
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
            <Text className='logo-subtitle'>Teacher Portal</Text>
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
            <Text className='page-desc'>{activeMeta.group} / 教师工作台</Text>
          </View>
          <View className='user-box'>
            <View className='user-chip'>
              <Text className='user-name'>{userInfo?.username || '教师'}</Text>
              <Text className='user-role'>教师</Text>
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
                <Text className='panel-subtitle'>通过左侧导航选择具体功能</Text>
              </View>
              <Text className='empty'>已切换到 {activeMeta.title}，如需进一步细化该页面，我继续直接重构。</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  )
}
