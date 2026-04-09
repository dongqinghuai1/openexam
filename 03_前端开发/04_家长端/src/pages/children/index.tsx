import { View, Text } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function ChildrenPage() {
  const [children, setChildren] = useState<any[]>([])

  useEffect(() => {
    fetchChildren()
  }, [])

  const fetchChildren = async () => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const phone = user?.phone || user?.username
      const res = await api.get('/edu/students/', { parent_phone: phone })
      setChildren(res.results || res || [])
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取孩子信息失败', icon: 'none' })
    }
  }

  return (
    <View className='children-page'>
      <View className='header'>
        <Text className='title'>孩子管理</Text>
        <Text className='subtitle'>当前已绑定 {children.length} 位孩子</Text>
      </View>

      <View className='content'>
        {children.length > 0 ? children.map((child, index) => (
          <View className='child-card' key={index}>
            <Text className='name'>{child.name}</Text>
            <Text className='line'>年级: {child.grade}</Text>
            <Text className='line'>学校: {child.school || '-'}</Text>
            <Text className='line'>手机号: {child.phone}</Text>
            <Text className='line'>状态: {child.status === 'active' ? '在读' : child.status}</Text>
            <Text className='line'>班级: {child.class_name || '未分班'}</Text>
          </View>
        )) : <View className='empty'>暂无绑定孩子</View>}
      </View>
    </View>
  )
}
