import { View, Text, Button } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Profile() {
  const [userInfo, setUserInfo] = useState<any>(Taro.getStorageSync('userInfo') || {})
  const [studentInfo, setStudentInfo] = useState<any>(null)
  const [scoreCount, setScoreCount] = useState(0)

  useEffect(() => {
    fetchProfileData()
  }, [])

  const fetchProfileData = async () => {
    try {
      const currentUser = Taro.getStorageSync('userInfo') || {}
      setUserInfo(currentUser)

      const studentRes = await api.get('/edu/students/', { phone: currentUser.phone || currentUser.username })
      const students = studentRes.results || studentRes || []
      const student = Array.isArray(students) ? students[0] : null
      setStudentInfo(student)

      const studentId = student?.id || Taro.getStorageSync('studentId')
      if (studentId) {
        Taro.setStorageSync('studentId', studentId)
        const scoreRes = await api.get('/exam/scores/', { student_id: studentId })
        const scores = scoreRes.results || scoreRes || []
        setScoreCount(scores.length)
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取个人信息失败', icon: 'none' })
    }
  }

  const handleLogout = () => {
    Taro.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          Taro.removeStorageSync('token')
          Taro.removeStorageSync('userInfo')
          Taro.removeStorageSync('studentId')
          Taro.reLaunch({ url: '/pages/login/index' })
        }
      }
    })
  }

  return (
    <View className="profile-page">
      <View className="header">
        <View className="avatar">{(userInfo.name || userInfo.username || 'U').charAt(0)}</View>
        <Text className="name">{studentInfo?.name || userInfo.name || userInfo.username || '学生'}</Text>
        <Text className="phone">{userInfo.phone || studentInfo?.phone || ''}</Text>
      </View>

      <View className="summary-card">
        <View className="summary-item">
          <Text className="summary-label">班级</Text>
          <Text className="summary-value">{studentInfo?.class_name || '未分班'}</Text>
        </View>
        <View className="summary-item">
          <Text className="summary-label">年级</Text>
          <Text className="summary-value">{studentInfo?.grade || '-'}</Text>
        </View>
        <View className="summary-item">
          <Text className="summary-label">成绩记录</Text>
          <Text className="summary-value">{scoreCount}</Text>
        </View>
      </View>

      <View className="menu-list">
        <View className="menu-item">
          <Text className="icon">👤</Text>
          <View className="menu-main">
            <Text className="label">个人档案</Text>
            <Text className="desc">学校: {studentInfo?.school || '-'} | 状态: {studentInfo?.status === 'active' ? '在读' : (studentInfo?.status || '-')}</Text>
          </View>
        </View>
        <View className="menu-item" onClick={() => Taro.switchTab({ url: '/pages/exam/index' })}>
          <Text className="icon">📝</Text>
          <View className="menu-main">
            <Text className="label">考试中心</Text>
            <Text className="desc">进入考试页查看当前可参加考试</Text>
          </View>
        </View>
        <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/scores/index' })}>
          <Text className="icon">📊</Text>
          <View className="menu-main">
            <Text className="label">成绩记录</Text>
            <Text className="desc">查看最近考试成绩和排名</Text>
          </View>
        </View>
        <View className="menu-item" onClick={() => Taro.navigateTo({ url: '/pages/recordings/index' })}>
          <Text className="icon">📹</Text>
          <View className="menu-main">
            <Text className="label">课堂回放</Text>
            <Text className="desc">查看与本人课次关联的课堂回放</Text>
          </View>
        </View>
      </View>

      <Button className="logout-btn" onClick={handleLogout}>退出登录</Button>
    </View>
  )
}
