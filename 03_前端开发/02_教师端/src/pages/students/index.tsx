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
      const user = Taro.getStorageSync('userInfo')
      const teacherRes = await api.get('/edu/teachers/', { phone: user?.phone || user?.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null

      if (!teacher) {
        setStudents([])
        Taro.showToast({ title: '未找到教师档案', icon: 'none' })
        return
      }

      const classRes = await api.get('/edu/classes/', { teacher: teacher.id, page_size: 100 })
      const classes = classRes.results || classRes || []

      if (!classes.length) {
        setStudents([])
        return
      }

      const classDetailList = await Promise.all(classes.map((item) => api.get(`/edu/classes/${item.id}/`)))
      const studentMap = new Map()

      classDetailList.forEach((detail: any) => {
        const className = detail.name
        ;(detail.class_students || []).forEach((item: any) => {
          if (item.status !== 'studying' || !item.student) return
          const existing = studentMap.get(item.student.id)
          if (existing) {
            existing.classNames.push(className)
            return
          }
          studentMap.set(item.student.id, {
            ...item.student,
            classNames: className ? [className] : []
          })
        })
      })

      setStudents(Array.from(studentMap.values()))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取学生失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetail = (student) => {
    Taro.showModal({
      title: student.name,
      content: `手机: ${student.phone}\n年级: ${student.grade}\n学校: ${student.school || '-'}\n班级: ${(student.classNames || []).join('、') || '-'}`,
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
          students.map((student, index) => (
            <View className="student-card" key={index} onClick={() => handleViewDetail(student)}>
              <View className="avatar">{student.name?.charAt(0) || 'S'}</View>
                <View className="info">
                  <Text className="name">{student.name}</Text>
                  <Text className="detail">{student.grade} | {student.school}</Text>
                  <Text className="classes">班级: {(student.classNames || []).join('、') || '-'}</Text>
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
