import { View, Text, Button } from '@tarojs/components'
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
      const studentId = Taro.getStorageSync('studentId')
      if (!studentId) {
        setRecordings([])
        return
      }

      const scheduleRes = await api.get(`/edu/students/${studentId}/schedules/`)
      const schedules = scheduleRes || []
      const scheduleIds = new Set(schedules.map((item: any) => item.id))

      const res = await api.get('/classroom/playbacks/', { page_size: 100 })
      const list = res.results || res || []
      setRecordings(list.filter((item: any) => scheduleIds.has(item.recording_task?.meeting_room?.schedule)))
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取回放失败', icon: 'none' })
    }
  }

  const handlePlay = (url: string) => {
    if (url) {
      Taro.navigateTo({
        url: `/pages/link/index?title=${encodeURIComponent('课堂回放')}&type=playback&url=${encodeURIComponent(url)}`
      })
    }
  }

  const formatDuration = (seconds: number) => {
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
          recordings.map((item: any, index: number) => (
            <View className="recording-card" key={index}>
              <View className="class-name">{item.recording_task_class}</View>
              <View className="course-name">{item.recording_task_course}</View>
              <View className="info-row">
                <Text className="date">{item.recording_task_date}</Text>
                <Text className="duration">时长: {formatDuration(item.duration || 0)}</Text>
              </View>
              <Button className="play-btn" onClick={() => handlePlay(item.file_url)}>复制回放链接</Button>
            </View>
          ))
        ) : (
          <View className="empty">暂无录屏回放</View>
        )}
      </View>
    </View>
  )
}
