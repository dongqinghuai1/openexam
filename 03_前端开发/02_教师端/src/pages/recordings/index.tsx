import { View, Text } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Recordings() {
  const [recordings, setRecordings] = useState<any[]>([])

  useEffect(() => {
    fetchRecordings()
  }, [])

  const fetchRecordings = async () => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const teacherRes = await api.get('/edu/teachers/', { phone: user?.phone || user?.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      if (!teacher) {
        setRecordings([])
        return
      }

      const scheduleRes = await api.get('/edu/schedules/', { teacher: teacher.id, page_size: 100 })
      const schedules = scheduleRes.results || scheduleRes || []
      const scheduleIds = new Set(schedules.map((item) => item.id))

      const res = await api.get('/classroom/playbacks/', { page_size: 100 })
      const list = res.results || res || []
      setRecordings(list.filter((item) => scheduleIds.has(item.recording_task?.meeting_room?.schedule)))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取回放失败', icon: 'none' })
    }
  }

  const handlePlay = (url) => {
    if (url) {
      Taro.navigateTo({
        url: `/pages/link/index?title=${encodeURIComponent('课堂回放')}&type=playback&url=${encodeURIComponent(url)}`
      })
    }
  }

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <View className="recordings-page">
      <View className="header">
        <Text className="title">录屏回放</Text>
      </View>

      <View className="content">
        {recordings.length > 0 ? (
          recordings.map((item, index) => (
            <View className="recording-card" key={index}>
              <View className="class-name">{item.recording_task_class}</View>
              <View className="course-name">{item.recording_task_course}</View>
              <View className="info-row">
                <Text className="date">{item.recording_task_date}</Text>
                <Text className="duration">时长: {formatDuration(item.duration)}</Text>
              </View>
              <View className="status-row">
                <Text className={`status ${item.status}`}>
                  {item.status === 'ready' ? '可播放' : '处理中'}
                </Text>
                {item.status === 'ready' && (
                  <Text className="play-btn" onClick={() => handlePlay(item.file_url)}>复制回放链接</Text>
                )}
              </View>
            </View>
          ))
        ) : (
          <View className="empty">暂无录屏回放</View>
        )}
      </View>
    </View>
  )
}
