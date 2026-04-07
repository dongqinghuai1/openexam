import { View, Text } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Students() {
  const [students, setStudents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchStudents()
  }, [])

  const fetchStudents = async () => {
    setLoading(true)
    try {
      const res = await api.get('/edu/students/')
      setStudents(res.data?.results || res.data || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetail = (student: any) => {
    Taro.showModal({
      title: student.name,
      content: `手机: ${student.phone}\n年级: ${student.grade}\n学校: ${student.school}`,
      showCancel: false
    })
  }

  return (
    <View className="students-page">
      <View className="header">
        <Text className="title">我的学生</Text>
        <Text className="count">共 {students.length} 人</Text>
      </View>

      <View className="content">
        {students.length > 0 ? (
          students.map((student: any, index: number) => (
            <View className="student-card" key={index} onClick={() => handleViewDetail(student)}>
              <View className="avatar">{student.name?.charAt(0) || 'S'}</View>
              <View className="info">
                <Text className="name">{student.name}</Text>
                <Text className="detail">{student.grade} | {student.school}</Text>
                <Text className="phone">📱 {student.phone}</Text>
              </View>
            </View>
          ))
        ) : (
          <View className="empty">{loading ? '加载中...' : '暂无学生'}</View>
        )}
      </View>
    </View>
  )
}