import { View, Text, Input, Button } from '@tarojs/components'
import { useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Login() {
  const [account, setAccount] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    if (!account || !password) {
      Taro.showToast({ title: '请输入账号和密码', icon: 'none' })
      return
    }

    setLoading(true)
    try {
      const res = await api.post('/users/login', { username: account, password })
      const roleCodes = (res.user?.roles || []).map((item) => item.code)
      if (!res.user?.is_superuser && !roleCodes.includes('student')) {
        Taro.showToast({ title: '当前账号不是学生，不能进入学生端', icon: 'none' })
        return
      }
      Taro.setStorageSync('token', res.token)
      Taro.setStorageSync('refresh_token', res.refresh_token)
      Taro.setStorageSync('userInfo', res.user)
      Taro.redirectTo({ url: '/pages/index/index' })
    } catch (e: any) {
      Taro.showToast({ title: e.message || '登录失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className="login">
      <View className="logo">EduAdmin</View>
      <Text className="title">学生端登录</Text>
      <View className="form">
        <Input className="input" placeholder="请输入用户名 / 手机号 / 邮箱" value={account} onInput={(e) => setAccount(e.detail.value)} />
        <Input className="input" type="password" placeholder="请输入密码" value={password} onInput={(e) => setPassword(e.detail.value)} />
        <Button className="btn" loading={loading} onClick={handleLogin}>登录</Button>
      </View>
    </View>
  )
}
