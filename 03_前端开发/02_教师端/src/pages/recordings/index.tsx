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
      const res = await api.get('/classroom/playbacks/')
      setRecordings(res.data?.results || res.data || [])
    } catch (e) { console.error(e) }
  }

  const handlePlay = (url: string) => {
    if (url) {
      Taro.navigateTo({ url: `/pages/webview/index?url=${encodeURIComponent(url)}` })
    }
  }

  const formatDuration = (seconds: number) => {
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
          recordings.map((item: any, index: number) => (
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
                  <Text className="play-btn" onClick={() => handlePlay(item.file_url)}>播放</Text>
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