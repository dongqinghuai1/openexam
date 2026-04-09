import { View, Text, Button } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [schedules, setSchedules] = useState<any[]>([])

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
      const teachers = teacherRes.results || teacherRes.data?.results || teacherRes.data || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      if (!teacher) {
        Taro.showToast({ title: '未找到教师档案', icon: 'none' })
        return
      }
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

      const meetingId = meeting.id
      const activeMeeting = meeting.status === 'ongoing' ? meeting : await api.post(`/classroom/meeting_rooms/${meetingId}/start_meeting/`)
      if (activeMeeting.join_url) {
        Taro.navigateTo({
          url: `/pages/link/index?title=${encodeURIComponent('课堂入口')}&type=classroom&url=${encodeURIComponent(activeMeeting.join_url)}`
        })
      } else {
        Taro.showToast({ title: '课堂已开始', icon: 'success' })
      }
      fetchTeacherAndSchedules(Taro.getStorageSync('userInfo'))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '开始上课失败', icon: 'none' })
    }
  }

  const handleProfile = () => {
    Taro.navigateTo({ url: '/pages/profile/index' })
  }

  return (
    <View className="index">
      <View className="header">
        <Text className="title">教师端</Text>
        <Text className="username">{userInfo?.username || '教师'}</Text>
        <Button className="logout-btn" onClick={handleLogout}>退出</Button>
      </View>

      <View className="section">
        <Text className="section-title">今日课程</Text>
          {schedules.length > 0 ? (
          schedules.map((item, index) => (
            <View className="schedule-card" key={index}>
              <View className="time">{item.start_time?.substring(0,5)} - {item.end_time?.substring(0,5)}</View>
              <View className="class-name">{item.class_name}</View>
              <View className="course-name">{item.course_name}</View>
              <Button className="start-btn" onClick={() => Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${item.id}` })}>查看详情</Button>
              <Button className="start-btn" onClick={() => handleStartClass(item)}>开始上课</Button>
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
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/students/index' })}>
            <Text className="icon">👨‍🎓</Text>
            <Text className="label">我的学生</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/recordings/index' })}>
            <Text className="icon">📹</Text>
            <Text className="label">录屏回放</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/notes/index' })}>
            <Text className="icon">📝</Text>
            <Text className="label">课堂笔记</Text>
          </View>
          <View className="menu-item" onClick={handleProfile}>
            <Text className="icon">👤</Text>
            <Text className="label">个人中心</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
