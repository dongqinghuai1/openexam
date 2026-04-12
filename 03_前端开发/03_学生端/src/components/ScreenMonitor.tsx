import { View, Text } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import './ScreenMonitor.scss'

export default function ScreenMonitor({ examId, studentId }) {
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [screenActivity, setScreenActivity] = useState([])
  const [warningCount, setWarningCount] = useState(0)
  const [lastActivityTime, setLastActivityTime] = useState(Date.now())

  useEffect(() => {
    startMonitoring()
    return () => {
      stopMonitoring()
    }
  }, [])

  const startMonitoring = () => {
    setIsMonitoring(true)
    
    // 模拟屏幕监控
    const interval = setInterval(() => {
      monitorScreenActivity()
    }, 5000) // 每5秒检查一次

    return () => clearInterval(interval)
  }

  const stopMonitoring = () => {
    setIsMonitoring(false)
  }

  const monitorScreenActivity = () => {
    const now = Date.now()
    
    // 模拟屏幕活动检测
    const activities = [
      '正常答题',
      '切换窗口',
      '打开新标签',
      '复制粘贴',
      '使用快捷键'
    ]
    
    // 随机生成屏幕活动（实际应用中应该使用真实的屏幕监控API）
    const randomActivity = activities[Math.floor(Math.random() * activities.length)]
    const activityTime = new Date().toLocaleTimeString()
    
    const newActivity = {
      time: activityTime,
      activity: randomActivity
    }
    
    setScreenActivity(prev => [...prev, newActivity].slice(-10)) // 只保留最近10条记录
    
    // 检测异常活动
    if (randomActivity !== '正常答题') {
      setWarningCount(prev => prev + 1)
      // 发送警告
      sendWarning(randomActivity)
    }
    
    setLastActivityTime(now)
  }

  const sendWarning = (activity) => {
    // 模拟发送警告到后端
    console.log('发送警告:', activity)
    // 实际应用中应该调用API发送警告
  }

  return (
    <View className="screen-monitor-container">
      <View className="header">
        <Text className="title">屏幕监控</Text>
        <Text className={`status ${isMonitoring ? 'active' : 'inactive'}`}>
          {isMonitoring ? '监控中' : '未监控'}
        </Text>
      </View>
      
      <View className="warning-section">
        <Text className="warning-title">警告次数: <Text className="warning-count">{warningCount}</Text></Text>
      </View>
      
      <View className="activity-log">
        <Text className="log-title">最近活动</Text>
        <View className="log-list">
          {screenActivity.map((activity, index) => (
            <View key={index} className="log-item">
              <Text className="log-time">{activity.time}</Text>
              <Text className={`log-activity ${activity.activity !== '正常答题' ? 'warning' : ''}`}>
                {activity.activity}
              </Text>
            </View>
          ))}
          {screenActivity.length === 0 && (
            <Text className="empty-log">暂无活动记录</Text>
          )}
        </View>
      </View>
      
      <View className="monitoring-info">
        <Text className="info-text">系统正在监控您的屏幕活动，请保持专注答题。</Text>
        <Text className="info-text">异常活动将被记录并可能影响您的考试成绩。</Text>
      </View>
    </View>
  )
}
