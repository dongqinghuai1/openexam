import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Profile() {
  const userInfo = Taro.getStorageSync('userInfo') || {}
  const [teacherInfo, setTeacherInfo] = useState<any>(null)
  const [classes, setClasses] = useState<any[]>([])
  const [schedules, setSchedules] = useState<any[]>([])

  const summary = useMemo(() => {
    const classCount = classes.length
    const scheduleCount = schedules.length
    const upcomingCount = schedules.filter(item => item.status === 'scheduled').length
    return { classCount, scheduleCount, upcomingCount }
  }, [classes, schedules])

  useEffect(() => {
    fetchProfileData()
  }, [])

  const fetchProfileData = async () => {
    try {
      const teacherRes = await api.get('/edu/teachers/', { phone: userInfo.phone || userInfo.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      setTeacherInfo(teacher)

      if (!teacher) return

      const [classRes, scheduleRes] = await Promise.all([
        api.get('/edu/classes/', { teacher: teacher.id, page_size: 100 }),
        api.get(`/edu/teachers/${teacher.id}/schedules/`),
      ])
      setClasses(classRes.results || classRes || [])
      setSchedules(scheduleRes || [])
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取教师档案失败', icon: 'none' })
    }
  }

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
        <Text className='name'>{teacherInfo?.name || userInfo.username || '教师用户'}</Text>
        <Text className='meta'>{userInfo.phone || teacherInfo?.phone || '未绑定手机号'}</Text>
        <Text className='meta'>角色: {(userInfo.role_names || []).join(' / ') || '教师'}</Text>
      </View>

      <View className='summary-card'>
        <View className='summary-item'><Text className='summary-label'>授课班级</Text><Text className='summary-value'>{summary.classCount}</Text></View>
        <View className='summary-item'><Text className='summary-label'>总课次</Text><Text className='summary-value'>{summary.scheduleCount}</Text></View>
        <View className='summary-item'><Text className='summary-label'>待上课程</Text><Text className='summary-value'>{summary.upcomingCount}</Text></View>
      </View>

      <View className='panel'>
        <Text className='panel-title'>教师档案</Text>
        <View className='info-row'><Text className='label'>用户名</Text><Text className='value'>{userInfo.username || '-'}</Text></View>
        <View className='info-row'><Text className='label'>教师姓名</Text><Text className='value'>{teacherInfo?.name || '-'}</Text></View>
        <View className='info-row'><Text className='label'>手机号</Text><Text className='value'>{teacherInfo?.phone || userInfo.phone || '-'}</Text></View>
        <View className='info-row'><Text className='label'>授课科目</Text><Text className='value'>{(teacherInfo?.subjects || []).map((item) => item.name).join('、') || '-'}</Text></View>
        <View className='info-row'><Text className='label'>状态</Text><Text className='value'>{userInfo.status === 'active' ? '启用' : '禁用'}</Text></View>
      </View>

      <View className='panel'>
        <Text className='panel-title'>授课概览</Text>
        {classes.length ? classes.map((item) => (
          <View className='class-row' key={item.id}>
            <Text className='class-name'>{item.name}</Text>
            <Text className='class-meta'>{item.course_name} | 已报名 {item.student_count} 人</Text>
          </View>
        )) : <Text className='hint'>当前暂无授课班级</Text>}
      </View>

      <View className='panel'>
        <Text className='panel-title'>快捷入口</Text>
        <View className='action-row'><Text className='action-link' onClick={() => Taro.navigateTo({ url: '/pages/schedule/index' })}>查看课表</Text></View>
        <View className='action-row'><Text className='action-link' onClick={() => Taro.navigateTo({ url: '/pages/students/index' })}>查看学生</Text></View>
        <View className='action-row'><Text className='action-link' onClick={() => Taro.navigateTo({ url: '/pages/notes/index' })}>课堂笔记</Text></View>
      </View>

      <Button className='logout-btn' onClick={handleLogout}>退出登录</Button>
    </View>
  )
}
