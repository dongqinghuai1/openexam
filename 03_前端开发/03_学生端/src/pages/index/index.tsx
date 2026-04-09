import { View, Text, Button } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [schedules, setSchedules] = useState<any[]>([])
  const [hoursAccounts, setHoursAccounts] = useState<any[]>([])
  const [scores, setScores] = useState<any[]>([])
  const [exams, setExams] = useState<any[]>([])

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
      const students = studentRes.results || studentRes.data?.results || studentRes.data || []
      const student = Array.isArray(students) ? students[0] : null
      if (!student) {
        Taro.showToast({ title: '未找到学生档案', icon: 'none' })
        return
      }
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
    } catch (e) { console.error(e) }
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

  const getScheduleStatusText = (schedule) => {
    const status = getScheduleStatus(schedule)
    if (status === 'upcoming') return '未开始'
    if (status === 'ongoing') return '可进入'
    return '已结束'
  }

  const handleScheduleAction = (schedule) => {
    const status = getScheduleStatus(schedule)
    if (status === 'ongoing') {
      handleJoinClass(schedule)
      return
    }
    Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${schedule.id}` })
  }

  const totalHours = hoursAccounts.reduce((sum, acc) => sum + (acc.remaining_hours || 0), 0)
  const upcomingSchedules = schedules.filter((item) => item.status === 'scheduled')
  const availableExams = exams.filter((item) => item.status !== 'ended')
  const latestScore = scores[0]?.score ?? '-'

  return (
    <View className="index">
      <View className="header">
        <Text className="title">学生端</Text>
        <Text className="username">{userInfo?.name || '学生'}</Text>
        <Button className="logout-btn" onClick={handleLogout}>退出</Button>
      </View>

      <View className="hours-card">
        <Text className="label">我的课时</Text>
        <Text className="value">{totalHours}</Text>
        <Text className="unit">课时</Text>
      </View>

      <View className="dashboard-grid">
        <View className="dashboard-card">
          <Text className="dashboard-label">待上课程</Text>
          <Text className="dashboard-value">{upcomingSchedules.length}</Text>
          <Text className="dashboard-desc">最近课程尽在课次详情</Text>
        </View>
        <View className="dashboard-card">
          <Text className="dashboard-label">待参加考试</Text>
          <Text className="dashboard-value">{availableExams.length}</Text>
          <Text className="dashboard-desc">进入考试中心查看安排</Text>
        </View>
        <View className="dashboard-card full">
          <Text className="dashboard-label">最近成绩</Text>
          <Text className="dashboard-value">{latestScore}</Text>
          <Text className="dashboard-desc">最近一次考试成绩与排名可在成绩页查看</Text>
        </View>
      </View>

      <View className="section">
        <Text className="section-title">今日课程</Text>
        {upcomingSchedules.length > 0 ? (
          upcomingSchedules.slice(0, 3).map((item, index) => (
            <View className="schedule-card" key={index}>
              <View className="time">{item.start_time?.substring(0,5)} - {item.end_time?.substring(0,5)}</View>
              <View className="class-name">{item.class_name}</View>
              <View className="course-name">{item.course_name}</View>
              <Text className={`schedule-status ${getScheduleStatus(item)}`}>{getScheduleStatusText(item)}</Text>
              <Button className="join-btn secondary" onClick={() => Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${item.id}` })}>查看详情</Button>
              <Button className="join-btn" onClick={() => handleScheduleAction(item)}>
                {getScheduleStatus(item) === 'ongoing' ? '进入课堂' : getScheduleStatus(item) === 'upcoming' ? '查看准备' : '查看回放'}
              </Button>
            </View>
          ))
        ) : (
          <Text className="empty">暂无今日课程</Text>
        )}
      </View>

      <View className="section">
        <Text className="section-title">快捷功能</Text>
        <View className="menu-grid">
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/schedule/index' })}>
            <Text className="icon">📅</Text>
            <Text className="label">我的课表</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/exam/index' })}>
            <Text className="icon">📝</Text>
            <Text className="label">考试答题</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/recordings/index' })}>
            <Text className="icon">📹</Text>
            <Text className="label">录屏回放</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/scores/index' })}>
            <Text className="icon">📊</Text>
            <Text className="label">成绩查询</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
