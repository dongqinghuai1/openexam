import { View, Text, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import './index.scss'

export default function Profile() {
  const userInfo = Taro.getStorageSync('userInfo') || {}

  const handleLogout = () => {
    Taro.showModal({
      title: '退出登录',
      content: '确定退出当前教师账号吗？',
      success: (res) => {
        if (!res.confirm) return
        Taro.removeStorageSync('token')
        Taro.removeStorageSync('userInfo')
        Taro.reLaunch({ url: '/pages/login/index' })
      }
    })
  }

  return (
    <View className='profile-page'>
      <View className='header-card'>
        <View className='avatar'>{(userInfo.username || 'T').charAt(0).toUpperCase()}</View>
        <Text className='name'>{userInfo.username || '教师用户'}</Text>
        <Text className='meta'>{userInfo.phone || '未绑定手机号'}</Text>
        <Text className='meta'>角色: {(userInfo.role_names || []).join(' / ') || '教师'}</Text>
      </View>

      <View className='panel'>
        <Text className='panel-title'>账号信息</Text>
        <View className='info-row'><Text className='label'>用户名</Text><Text className='value'>{userInfo.username || '-'}</Text></View>
        <View className='info-row'><Text className='label'>手机号</Text><Text className='value'>{userInfo.phone || '-'}</Text></View>
        <View className='info-row'><Text className='label'>状态</Text><Text className='value'>{userInfo.status === 'active' ? '启用' : '禁用'}</Text></View>
      </View>

      <View className='panel'>
        <Text className='panel-title'>使用提示</Text>
        <Text className='hint'>可以从首页进入课表、学生和回放页面。课堂链接会统一进入链接页，便于复制和分享。</Text>
      </View>

      <Button className='logout-btn' onClick={handleLogout}>退出登录</Button>
    </View>
  )
}
