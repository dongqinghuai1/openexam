import { View, Text } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import dayjs from 'dayjs'
import './index.scss'

export default function Schedule() {
  const [schedules, setSchedules] = useState<any[]>([])
  const [currentDate, setCurrentDate] = useState(dayjs())

  useEffect(() => {
    fetchSchedules()
  }, [currentDate])

  const fetchSchedules = async () => {
    try {
      const startDate = currentDate.startOf('month').format('YYYY-MM-DD')
      const endDate = currentDate.endOf('month').format('YYYY-MM-DD')
      const res = await api.get('/edu/schedules/', { 
        date__gte: startDate, 
        date__lte: endDate 
      })
      setSchedules(res.data?.results || res.data || [])
    } catch (e) { console.error(e) }
  }

  const prevMonth = () => setCurrentDate(currentDate.subtract(1, 'month'))
  const nextMonth = () => setCurrentDate(currentDate.add(1, 'month'))

  const getDaysInMonth = () => {
    const days = []
    const start = currentDate.startOf('month').day()
    const total = currentDate.daysInMonth()
    
    for (let i = 0; i < start; i++) {
      days.push({ day: '', empty: true })
    }
    for (let i = 1; i <= total; i++) {
      const date = currentDate.date(i).format('YYYY-MM-DD')
      const daySchedules = schedules.filter(s => s.date === date)
      days.push({ day: i, date, schedules: daySchedules })
    }
    return days
  }

  return (
    <View className="schedule-page">
      <View className="header">
        <Text className="title">我的课表</Text>
      </View>

      <View className="month-nav">
        <Text className="nav-btn" onClick={prevMonth}>◀</Text>
        <Text className="month">{currentDate.format('YYYY年MM月')}</Text>
        <Text className="nav-btn" onClick={nextMonth}>▶</Text>
      </View>

      <View className="weekday">
        <Text>日</Text><Text>一</Text><Text>二</Text><Text>三</Text><Text>四</Text><Text>五</Text><Text>六</Text>
      </View>

      <View className="calendar">
        {getDaysInMonth().map((item: any, index: number) => (
          <View className={`day ${item.empty ? 'empty' : ''}`} key={index}>
            <Text className="day-num">{item.day}</Text>
            {item.schedules?.length > 0 && (
              <View className="day-schedule">
                {item.schedules.slice(0, 2).map((s: any, i: number) => (
                  <Text className="schedule-dot" key={i}>{s.course_name}</Text>
                ))}
              </View>
            )}
          </View>
        ))}
      </View>

      <View className="schedule-list">
        <Text className="list-title">当日课程</Text>
        {schedules
          .filter(s => s.date === dayjs().format('YYYY-MM-DD'))
          .map((item: any, index: number) => (
            <View className="schedule-card" key={index}>
              <Text className="time">{item.start_time?.substring(0,5)} - {item.end_time?.substring(0,5)}</Text>
              <Text className="class-name">{item.class_name}</Text>
              <Text className="course-name">{item.course_name}</Text>
              <Text className="teacher">教师: {item.teacher_name}</Text>
            </View>
          ))}
      </View>
    </View>
  )
}