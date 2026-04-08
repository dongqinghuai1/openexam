import { View, Text, Button, Input } from '@tarojs/components'
import { useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Schedule() {
  const [schedules, setSchedules] = useState([])
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])

  const fetchSchedules = async () => {
    try {
      const res = await api.get('/edu/schedules/', { date: selectedDate })
      setSchedules(res.data?.results || res.data || [])
    } catch (e) { console.error(e) }
  }

  const handleStartClass = (schedule) => {
    Taro.showToast({ title: `课堂功能开发中: ${schedule.id}`, icon: 'none' })
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
              <View key={offset} className="day-item" onClick={() => { setSelectedDate(dateStr); fetchSchedules() }}>
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
