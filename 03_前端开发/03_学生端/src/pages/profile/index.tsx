import { View, Text, Button } from '@tarojs/components'
import { useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Profile() {
  const [userInfo, setUserInfo] = useState<any>(Taro.getStorageSync('userInfo') || {})

  const handleLogout = () => {
    Taro.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          Taro.removeStorageSync('token')
          Taro.removeStorageSync('userInfo')
          Taro.reLaunch({ url: '/pages/login/index' })
        }
      }
    })
  }

  const menuList = [
    { icon: '👤', label: '个人信息', path: '/pages/profile/edit' },
    { icon: '🔔', label: '消息通知', path: '/pages/notifications/index' },
    { icon: '⚙️', label: '设置', path: '/pages/settings/index' },
    { icon: '❓', label: '帮助与反馈', path: '/pages/help/index' },
  ]

  return (
    <View className="profile-page">
      <View className="header">
        <View className="avatar">{(userInfo.name || userInfo.username || 'U').charAt(0)}</View>
        <Text className="name">{userInfo.name || userInfo.username || '用户'}</Text>
        <Text className="phone">{userInfo.phone || ''}</Text>
      </View>

      <View className="menu-list">
        {menuList.map((item, index) => (
          <View className="menu-item" key={index} onClick={() => Taro.navigateTo({ url: item.path })}>
            <Text className="icon">{item.icon}</Text>
            <Text className="label">{item.label}</Text>
            <Text className="arrow">▶</Text>
          </View>
        ))}
      </View>

      <Button className="logout-btn" onClick={handleLogout}>退出登录</Button>
    </View>
  )
}