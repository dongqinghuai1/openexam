import { View, Text, Button } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Index() {
  const [userInfo, setUserInfo] = useState(null)
  const [schedules, setSchedules] = useState([])

  useEffect(() => {
    const user = Taro.getStorageSync('userInfo')
    if (user) {
      setUserInfo(user)
      fetchTodaySchedules()
    } else {
      Taro.redirectTo({ url: '/pages/login/index' })
    }
  }, [])

  const fetchTodaySchedules = async () => {
    try {
      const res = await api.get('/edu/teachers/1/schedules/')
      setSchedules(res.data || [])
    } catch (e) {
      console.error(e)
    }
  }

  const handleLogout = () => {
    Taro.removeStorageSync('token')
    Taro.removeStorageSync('userInfo')
    Taro.redirectTo({ url: '/pages/login/index' })
  }

  const handleStartClass = (schedule) => {
    Taro.showToast({ title: `课堂功能开发中: ${schedule.id}`, icon: 'none' })
  }

  const handleProfile = () => {
    Taro.showToast({ title: '个人中心开发中', icon: 'none' })
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
          <View className="menu-item" onClick={handleProfile}>
            <Text className="icon">👤</Text>
            <Text className="label">个人中心</Text>
          </View>
        </View>
      </View>
    </View>
  )
}
