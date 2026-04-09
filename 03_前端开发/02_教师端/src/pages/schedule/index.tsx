import { View, Text, Button } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Schedule() {
  const [schedules, setSchedules] = useState<any[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])

  useEffect(() => {
    fetchSchedules(selectedDate)
  }, [selectedDate])

  const fetchSchedules = async (date = selectedDate) => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const teacherRes = await api.get('/edu/teachers/', { phone: user?.phone || user?.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      if (!teacher) {
        setSchedules([])
        return
      }
      const res = await api.get('/edu/schedules/', { date, teacher: teacher.id })
      setSchedules(res.results || res || [])
    } catch (e) { console.error(e) }
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
      } else {
        Taro.showToast({ title: '课堂已开始', icon: 'success' })
      }
      fetchSchedules()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '开始上课失败', icon: 'none' })
    }
  }

  const todaySchedule = schedules.filter((s) => s.status === 'scheduled')

  return (
    <View className="schedule-page">
      <View className="header">
        <Text className="title">我的课表</Text>
        <Text className="date">{selectedDate}</Text>
      </View>

      <View className="section">
        <Text className="section-title">今日课程 ({todaySchedule.length}节)</Text>
        {todaySchedule.length > 0 ? (
          todaySchedule.map((item, index) => (
            <View className="schedule-card" key={index}>
              <View className="time">{item.start_time?.substring(0,5)} - {item.end_time?.substring(0,5)}</View>
              <View className="class-name">{item.class_name}</View>
              <View className="course-name">{item.course_name}</View>
              <Button className="start-btn" onClick={() => Taro.navigateTo({ url: `/pages/schedule-detail/index?id=${item.id}` })}>查看详情</Button>
              <Button className="start-btn" onClick={() => handleStartClass(item)}>开始上课</Button>
            </View>
          ))
        ) : (
          <View className="empty">今日无课程</View>
        )}
      </View>

      <View className="section">
        <Text className="section-title">未来7天课程</Text>
        <View className="week-list">
          {[0,1,2,3,4,5,6].map((offset) => {
            const date = new Date()
            date.setDate(date.getDate() + offset)
            const dateStr = date.toISOString().split('T')[0]
            const dayName = ['今天','明天','后天','周一','周二','周三','周四','周五','周六','周日'][date.getDay()]
            return (
              <View key={offset} className="day-item" onClick={() => setSelectedDate(dateStr)}>
                <Text className="day-name">{dayName}</Text>
                <Text className="day-date">{dateStr}</Text>
              </View>
            )
          })}
        </View>
      </View>
    </View>
  )
}
