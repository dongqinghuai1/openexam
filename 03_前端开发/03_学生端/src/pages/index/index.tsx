import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [schedules, setSchedules] = useState<any[]>([])
  const [hoursAccounts, setHoursAccounts] = useState<any[]>([])
  const [scores, setScores] = useState<any[]>([])
  const [exams, setExams] = useState<any[]>([])
  const [activeGroup, setActiveGroup] = useState('overview')
  const [activeItem, setActiveItem] = useState('dashboard')

  useEffect(() => {
    const user = Taro.getStorageSync('userInfo')
    if (user) {
      setUserInfo(user)
      fetchStudentData(user)
    } else {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  }, [])

  const fetchStudentData = async (user) => {
    try {
      const studentRes = await api.get('/edu/students/', { phone: user.phone || user.username })
      const students = studentRes.results || studentRes || []
      const student = Array.isArray(students) ? students[0] : null
      if (!student) return
      Taro.setStorageSync('studentId', student.id)
      const [scheduleRes, hoursRes, scoreRes, examRes] = await Promise.all([
        api.get(`/edu/students/${student.id}/schedules/`),
        api.get('/edu/hours/accounts/', { student: student.id }),
        api.get('/exam/scores/', { student_id: student.id }),
        api.get('/exam/exams/'),
      ])
      setSchedules(scheduleRes || [])
      setHoursAccounts(hoursRes.results || hoursRes || [])
      setScores(scoreRes.results || scoreRes || [])
      setExams(examRes.results || examRes || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleLogout = () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('userInfo')
    Taro.removeStorageSync('studentId')
    Taro.redirectTo({ url: '/pages/login/index' })
  }

  const handleJoinClass = async (schedule) => {
    try {
      const meetingList = await api.get('/classroom/meeting_rooms/', { page_size: 100 })
      const meetings = meetingList.results || meetingList || []
      const meeting = meetings.find((item) => item.schedule === schedule.id || item.schedule_id === schedule.id)
      if (!meeting?.join_url) {
        Taro.showToast({ title: '当前课程尚未开放进入', icon: 'none' })
        return
      }
      Taro.navigateTo({
        url: `/pages/link/index?title=${encodeURIComponent('课堂入口')}&type=classroom&url=${encodeURIComponent(meeting.join_url)}`
      })
    } catch (e: any) {
      Taro.showToast({ title: e.message || '进入课堂失败', icon: 'none' })
    }
  }

  const getScheduleStatus = (schedule) => {
    const now = new Date().getTime()
    const startAt = new Date(`${schedule.date}T${schedule.start_time}`).getTime()
    const endAt = new Date(`${schedule.date}T${schedule.end_time}`).getTime()
    if (now < startAt) return 'upcoming'
    if (now > endAt) return 'finished'
    return 'ongoing'
  }

  const totalHours = hoursAccounts.reduce((sum, acc) => sum + (acc.remaining_hours || 0), 0)
  const upcomingSchedules = schedules.filter((item) => item.status === 'scheduled')
  const availableExams = exams.filter((item) => item.status !== 'ended')
  const latestScore = scores[0]?.score ?? '-'

  const groups = [
    {
      key: 'overview',
      label: '学习概览',
      items: [{ key: 'dashboard', label: '控制台' }],
    },
    {
      key: 'course',
      label: '课程学习',
      items: [
        { key: 'schedule', label: '我的课表', action: () => Taro.navigateTo({ url: '/pages/schedule/index' }) },
        { key: 'recordings', label: '录屏回放', action: () => Taro.navigateTo({ url: '/pages/recordings/index' }) },
      ],
    },
    {
      key: 'exam',
      label: '考试成绩',
      items: [
        { key: 'exam', label: '考试答题', action: () => Taro.navigateTo({ url: '/pages/exam/index' }) },
        { key: 'scores', label: '成绩查询', action: () => Taro.navigateTo({ url: '/pages/scores/index' }) },
        { key: 'profile', label: '个人中心', action: () => Taro.navigateTo({ url: '/pages/profile/index' }) },
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
    return { group: '学习概览', title: '控制台' }
  }, [activeItem])

  const renderDashboard = () => (
    <>
      <View className='stats-grid'>
        <View className='stat-card'><Text className='stat-label'>我的课时</Text><Text className='stat-value'>{totalHours}</Text></View>
        <View className='stat-card'><Text className='stat-label'>待上课程</Text><Text className='stat-value'>{upcomingSchedules.length}</Text></View>
        <View className='stat-card'><Text className='stat-label'>待参加考试</Text><Text className='stat-value'>{availableExams.length}</Text></View>
        <View className='stat-card'><Text className='stat-label'>最近成绩</Text><Text className='stat-value'>{latestScore}</Text></View>
      </View>

      <View className='panel'>
        <View className='panel-head'>
          <Text className='panel-title'>近期课程</Text>
          <Text className='panel-subtitle'>优先处理最近课程与课堂入口</Text>
        </View>
        {upcomingSchedules.length > 0 ? upcomingSchedules.slice(0, 4).map((item) => (
          <View className='list-row' key={item.id}>
            <View className='list-main'>
              <Text className='list-title'>{item.class_name}</Text>
              <Text className='list-desc'>{item.course_name} | {item.date} {item.start_time?.substring(0, 5)} - {item.end_time?.substring(0, 5)}</Text>
            </View>
            <View className='list-actions'>
              <Button className='ghost-btn' onClick={() => Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${item.id}` })}>详情</Button>
              <Button className='primary-btn' onClick={() => handleJoinClass(item)}>{getScheduleStatus(item) === 'ongoing' ? '进入课堂' : '查看准备'}</Button>
            </View>
          </View>
        )) : <Text className='empty'>暂无近期课程</Text>}
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
            <Text className='logo-subtitle'>Student Portal</Text>
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
            <Text className='page-desc'>{activeMeta.group} / 学生学习台</Text>
          </View>
          <View className='user-box'>
            <View className='user-chip'>
              <Text className='user-name'>{userInfo?.name || userInfo?.username || '学生'}</Text>
              <Text className='user-role'>学生</Text>
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
                <Text className='panel-subtitle'>通过左侧导航切换学习功能</Text>
              </View>
              <Text className='empty'>已切换到 {activeMeta.title}，如需继续重构该页面，我继续直接统一到后台骨架。</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  )
}
