import { View, Text } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Recordings() {
  const [children, setChildren] = useState<any[]>([])
  const [recordings, setRecordings] = useState<any[]>([])

  useEffect(() => {
    fetchRecordings()
  }, [])

  const fetchRecordings = async () => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const phone = user?.phone || user?.username
      const studentsRes = await api.get('/edu/students/', { parent_phone: phone })
      const studentList = studentsRes.results || studentsRes || []
      setChildren(studentList)

      if (!studentList.length) {
        setRecordings([])
        return
      }

      const scheduleRequests = studentList.map((student) => api.get(`/edu/students/${student.id}/schedules/`))
      const scheduleResults = await Promise.all(scheduleRequests)
      const scheduleIds = new Set(
        scheduleResults.flatMap((result: any) => (Array.isArray(result) ? result : [])).map((item: any) => item.id)
      )

      const playbackRes = await api.get('/classroom/playbacks/', { page_size: 100 })
      const playbackList = playbackRes.results || playbackRes || []
      setRecordings(playbackList.filter((item: any) => scheduleIds.has(item.recording_task?.meeting_room?.schedule)))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取回放失败', icon: 'none' })
    }
  }

  const handleCopy = (url: string) => {
    if (!url) return
    Taro.navigateTo({
      url: `/pages/link/index?title=${encodeURIComponent('孩子课堂回放')}&type=playback&url=${encodeURIComponent(url)}`
    })
  }

  const formatDuration = (seconds: number) => {
    if (!seconds) return '0:00'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <View className='recordings-page'>
      <View className='header'>
        <Text className='title'>孩子回放</Text>
        <Text className='subtitle'>共关联 {children.length} 位孩子</Text>
      </View>

      <View className='content'>
        {recordings.length > 0 ? (
          recordings.map((item, index) => (
            <View className='recording-card' key={index}>
              <View className='class-name'>{item.recording_task_class}</View>
              <View className='course-name'>{item.recording_task_course}</View>
              <View className='info-row'>
                <Text className='date'>{item.recording_task_date}</Text>
                <Text className='duration'>时长: {formatDuration(item.duration || 0)}</Text>
              </View>
              <View className='status-row'>
                <Text className={`status ${item.status}`}>{item.status === 'ready' ? '可播放' : '处理中'}</Text>
                {item.status === 'ready' && (
                  <Text className='play-btn' onClick={() => handleCopy(item.file_url)}>复制回放链接</Text>
                )}
              </View>
            </View>
          ))
        ) : (
          <View className='empty'>暂无可查看回放</View>
        )}
      </View>
    </View>
  )
}
