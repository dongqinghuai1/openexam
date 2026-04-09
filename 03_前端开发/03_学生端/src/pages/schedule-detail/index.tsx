import { View, Text, Button } from '@tarojs/components'
import { useEffect, useState } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function ScheduleDetail() {
  const router = useRouter()
  const scheduleId = Number(router.params?.id)
  const [schedule, setSchedule] = useState<any>(null)
  const [meeting, setMeeting] = useState<any>(null)
  const [playback, setPlayback] = useState<any>(null)

  useEffect(() => {
    if (scheduleId) fetchDetail()
  }, [scheduleId])

  const fetchDetail = async () => {
    try {
      const [scheduleRes, meetingRes, playbackRes] = await Promise.all([
        api.get(`/edu/schedules/${scheduleId}/`),
        api.get('/classroom/meeting_rooms/', { page_size: 100 }),
        api.get('/classroom/playbacks/', { page_size: 100 }),
      ])

      const meetingList = meetingRes.results || meetingRes || []
      const playbackList = playbackRes.results || playbackRes || []
      setSchedule(scheduleRes)
      setMeeting(meetingList.find((item) => item.schedule === scheduleId || item.schedule_id === scheduleId) || null)
      setPlayback(playbackList.find((item) => item.recording_task?.meeting_room?.schedule === scheduleId) || null)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取课次详情失败', icon: 'none' })
    }
  }

  const handleJoinClass = () => {
    if (!meeting?.join_url) {
      Taro.showToast({ title: '当前课程尚未开放进入', icon: 'none' })
      return
    }
    Taro.navigateTo({
      url: `/pages/link/index?title=${encodeURIComponent('课堂入口')}&type=classroom&url=${encodeURIComponent(meeting.join_url)}`
    })
  }

  const handleViewPlayback = () => {
    if (!playback?.file_url) {
      Taro.showToast({ title: '暂无回放记录', icon: 'none' })
      return
    }
    Taro.navigateTo({
      url: `/pages/link/index?title=${encodeURIComponent('课堂回放')}&type=playback&url=${encodeURIComponent(playback.file_url)}`
    })
  }

  if (!schedule) {
    return <View className='schedule-detail-page'><View className='empty'>课次信息加载中...</View></View>
  }

  return (
    <View className='schedule-detail-page'>
      <View className='hero-card'>
        <Text className='hero-title'>{schedule.course_name}</Text>
        <Text className='hero-sub'>{schedule.class_name}</Text>
        <Text className='hero-meta'>{schedule.date} {schedule.start_time?.substring(0, 5)} - {schedule.end_time?.substring(0, 5)}</Text>
        <Text className='hero-meta'>授课老师：{schedule.teacher_name}</Text>
      </View>

      <View className='section'>
        <Text className='section-title'>课堂操作</Text>
        <View className='action-list'>
          <Button className='primary-btn' onClick={handleJoinClass}>进入课堂</Button>
          <Button className='secondary-btn' onClick={handleViewPlayback}>查看回放</Button>
        </View>
      </View>

      <View className='section'>
        <Text className='section-title'>课程信息</Text>
        <View className='info-row'><Text className='label'>课程</Text><Text className='value'>{schedule.course_name}</Text></View>
        <View className='info-row'><Text className='label'>班级</Text><Text className='value'>{schedule.class_name}</Text></View>
        <View className='info-row'><Text className='label'>日期</Text><Text className='value'>{schedule.date}</Text></View>
        <View className='info-row'><Text className='label'>时间</Text><Text className='value'>{schedule.start_time?.substring(0, 5)} - {schedule.end_time?.substring(0, 5)}</Text></View>
        <View className='info-row'><Text className='label'>老师</Text><Text className='value'>{schedule.teacher_name}</Text></View>
        <View className='info-row'><Text className='label'>状态</Text><Text className='value'>{schedule.status === 'scheduled' ? '待上课' : schedule.status === 'completed' ? '已完成' : schedule.status}</Text></View>
      </View>

      <View className='section'>
        <Text className='section-title'>课堂回放</Text>
        <Text className='playback-meta'>
          {playback ? `${playback.recording_task_date} | ${playback.status === 'ready' ? '可查看' : '处理中'}` : '当前课次暂无回放'}
        </Text>
      </View>
    </View>
  )
}
