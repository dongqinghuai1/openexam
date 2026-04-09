import { View, Text } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function CalendarPage() {
  const [schedules, setSchedules] = useState<any[]>([])

  useEffect(() => {
    fetchSchedules()
  }, [])

  const fetchSchedules = async () => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const phone = user?.phone || user?.username
      const studentsRes = await api.get('/edu/students/', { parent_phone: phone })
      const students = studentsRes.results || studentsRes || []
      const scheduleResults = await Promise.all(students.map((student) => api.get(`/edu/students/${student.id}/schedules/`)))
      const merged = scheduleResults.flatMap((item: any) => Array.isArray(item) ? item : [])
      const deduped = Array.from(new Map(merged.map((item: any) => [item.id, item])).values())
      setSchedules(deduped.sort((a: any, b: any) => `${a.date} ${a.start_time}`.localeCompare(`${b.date} ${b.start_time}`)))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取课程日历失败', icon: 'none' })
    }
  }

  return (
    <View className='calendar-page'>
      <View className='header'>
        <Text className='title'>课程日历</Text>
        <Text className='subtitle'>查看孩子近期课程安排</Text>
      </View>

      <View className='content'>
        {schedules.length > 0 ? schedules.map((item, index) => (
          <View className='schedule-card' key={index}>
            <Text className='date'>{item.date}</Text>
            <Text className='time'>{item.start_time?.substring(0, 5)} - {item.end_time?.substring(0, 5)}</Text>
            <Text className='class-name'>{item.class_name}</Text>
            <Text className='course-name'>{item.course_name}</Text>
            <Text className='teacher'>教师: {item.teacher_name}</Text>
          </View>
        )) : <View className='empty'>暂无课程安排</View>}
      </View>
    </View>
  )
}
