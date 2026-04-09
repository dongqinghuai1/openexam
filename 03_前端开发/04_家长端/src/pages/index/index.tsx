import { View, Text, Button } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState<any>(null)
  const [children, setChildren] = useState<any[]>([])
  const [schedules, setSchedules] = useState<any[]>([])

  useEffect(() => {
    const user = Taro.getStorageSync('userInfo')
    if (user) {
      setUserInfo(user)
      fetchChildren(user)
    } else {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  }, [])

  const fetchChildren = async (user) => {
    try {
      const phone = user?.phone || user?.username
      const res = await api.get('/edu/students/', { parent_phone: phone })
      const list = res.results || res || []
      setChildren(list)
      fetchTodaySchedules(list)
    } catch (e) { console.error(e) }
  }

  const fetchTodaySchedules = async (studentList) => {
    try {
      const res = await api.get('/edu/schedules/', { date: new Date().toISOString().split('T')[0] })
      const list = res.results || res || []
      const classIds = new Set(studentList.flatMap(student => (student.class_name ? [student.class_name] : [])))
      setSchedules(list.filter(item => classIds.has(item.class_name)))
    } catch (e) { console.error(e) }
  }

  const handleLogout = () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('userInfo')
    Taro.redirectTo({ url: '/pages/login/index' })
  }

  return (
    <View className="index">
      <View className="header">
        <Text className="title">家长端</Text>
        <Text className="username">{userInfo?.name || '家长'}</Text>
        <Button className="logout-btn" onClick={handleLogout}>退出</Button>
      </View>

      <View className="section">
        <Text className="section-title">我的孩子</Text>
        {children.length > 0 ? (
          children.map((child, index) => (
            <View className="child-card" key={index}>
              <Text className="name">{child.name}</Text>
              <Text className="info">年级: {child.grade} | 学校: {child.school}</Text>
            </View>
          ))
        ) : (
          <Text className="empty">暂无绑定孩子</Text>
        )}
      </View>

      <View className="section">
        <Text className="section-title">今日课程</Text>
        {schedules.length > 0 ? (
          schedules.map((item, index) => (
            <View className="schedule-card" key={index}>
              <View className="time">{item.start_time?.substring(0,5)} - {item.end_time?.substring(0,5)}</View>
              <View className="class-name">{item.class_name}</View>
              <View className="course-name">{item.course_name}</View>
            </View>
          ))
        ) : (
          <Text className="empty">暂无今日课程</Text>
        )}
      </View>

      <View className="section">
        <Text className="section-title">快捷功能</Text>
        <View className="menu-grid">
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/children/index' })}>
            <Text className="icon">👶</Text>
            <Text className="label">孩子管理</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/calendar/index' })}>
            <Text className="icon">📅</Text>
            <Text className="label">课程日历</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/scores/index' })}>
            <Text className="icon">📊</Text>
            <Text className="label">成绩查询</Text>
          </View>
          <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/recordings/index' })}>
            <Text className="icon">📹</Text>
            <Text className="label">录屏回放</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
