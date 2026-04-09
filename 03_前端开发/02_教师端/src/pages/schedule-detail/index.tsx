import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

const parseNoteContent = (raw: string) => {
  if (!raw) {
    return { summary: '', homework: '', parentFeedback: '' }
  }
  try {
    const parsed = JSON.parse(raw)
    if (parsed && typeof parsed === 'object') {
      return {
        summary: parsed.summary || '',
        homework: parsed.homework || '',
        parentFeedback: parsed.parentFeedback || '',
      }
    }
  } catch (_) {
    return { summary: raw, homework: '', parentFeedback: '' }
  }
  return { summary: raw, homework: '', parentFeedback: '' }
}

export default function ScheduleDetail() {
  const router = useRouter()
  const scheduleId = Number(router.params?.id)
  const [schedule, setSchedule] = useState<any>(null)
  const [note, setNote] = useState<any>(null)
  const [playback, setPlayback] = useState<any>(null)
  const [meeting, setMeeting] = useState<any>(null)

  const notePreview = useMemo(() => {
    const parsed = parseNoteContent(note?.content || '')
    return {
      summary: parsed.summary || '暂无课堂总结',
      homework: parsed.homework || '暂无作业布置',
      parentFeedback: parsed.parentFeedback || '暂无家长反馈',
    }
  }, [note])

  useEffect(() => {
    if (scheduleId) {
      fetchDetail()
    }
  }, [scheduleId])

  const fetchDetail = async () => {
    try {
      const scheduleRes = await api.get(`/edu/schedules/${scheduleId}/`)
      setSchedule(scheduleRes)

      const [meetingRes, noteRes, playbackRes] = await Promise.all([
        api.get('/classroom/meeting_rooms/', { page_size: 100 }),
        api.get('/classroom/notes/', { schedule: scheduleId, page_size: 100 }),
        api.get('/classroom/playbacks/', { page_size: 100 }),
      ])

      const meetingList = meetingRes.results || meetingRes || []
      const noteList = noteRes.results || noteRes || []
      const playbackList = playbackRes.results || playbackRes || []

      setMeeting(meetingList.find((item) => item.schedule === scheduleId || item.schedule_id === scheduleId) || null)
      setNote(noteList[0] || null)
      setPlayback(playbackList.find((item) => item.recording_task?.meeting_room?.schedule === scheduleId) || null)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取课次详情失败', icon: 'none' })
    }
  }

  const handleStartClass = async () => {
    if (!schedule) return
    try {
      let activeMeeting = meeting
      if (!activeMeeting) {
        activeMeeting = await api.post('/classroom/meeting_rooms/create_meeting/', { schedule_id: schedule.id })
      }
      if (activeMeeting.status !== 'ongoing') {
        activeMeeting = await api.post(`/classroom/meeting_rooms/${activeMeeting.id}/start_meeting/`)
      }
      setMeeting(activeMeeting)
      if (activeMeeting.join_url) {
        Taro.navigateTo({
          url: `/pages/link/index?title=${encodeURIComponent('课堂入口')}&type=classroom&url=${encodeURIComponent(activeMeeting.join_url)}`
        })
      }
    } catch (e: any) {
      Taro.showToast({ title: e.message || '开始上课失败', icon: 'none' })
    }
  }

  const handleViewPlayback = () => {
    if (!playback?.file_url) {
      Taro.showToast({ title: '暂无可查看回放', icon: 'none' })
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
        <Text className='hero-title'>{schedule.class_name}</Text>
        <Text className='hero-sub'>{schedule.course_name}</Text>
        <Text className='hero-meta'>{schedule.date} {schedule.start_time?.substring(0, 5)} - {schedule.end_time?.substring(0, 5)}</Text>
        <Text className={`status status-${schedule.status}`}>状态：{schedule.status === 'scheduled' ? '待上课' : schedule.status === 'completed' ? '已完成' : schedule.status}</Text>
      </View>

      <View className='section'>
        <Text className='section-title'>课堂操作</Text>
        <View className='action-list'>
          <Button className='primary-btn' onClick={handleStartClass}>开始上课</Button>
          <Button className='secondary-btn' onClick={() => Taro.navigateTo({ url: '/pages/notes/index' })}>编辑课堂笔记</Button>
          <Button className='secondary-btn' onClick={handleViewPlayback}>查看课堂回放</Button>
        </View>
      </View>

      <View className='section'>
        <Text className='section-title'>课次信息</Text>
        <View className='info-row'><Text className='label'>班级</Text><Text className='value'>{schedule.class_name}</Text></View>
        <View className='info-row'><Text className='label'>课程</Text><Text className='value'>{schedule.course_name}</Text></View>
        <View className='info-row'><Text className='label'>教师</Text><Text className='value'>{schedule.teacher_name}</Text></View>
        <View className='info-row'><Text className='label'>日期</Text><Text className='value'>{schedule.date}</Text></View>
        <View className='info-row'><Text className='label'>时间</Text><Text className='value'>{schedule.start_time?.substring(0, 5)} - {schedule.end_time?.substring(0, 5)}</Text></View>
      </View>

      <View className='section'>
        <Text className='section-title'>课后跟进</Text>
        <Text className='note-label'>课堂总结</Text>
        <Text className='note-preview'>{notePreview.summary}</Text>
        <Text className='note-label'>作业布置</Text>
        <Text className='note-preview'>{notePreview.homework}</Text>
        <Text className='note-label'>家长反馈</Text>
        <Text className='note-preview'>{notePreview.parentFeedback}</Text>
      </View>

      <View className='section'>
        <Text className='section-title'>课堂回放</Text>
        <Text className='playback-meta'>
          {playback ? `${playback.recording_task_date} | 状态：${playback.status === 'ready' ? '可查看' : '处理中'}` : '暂无回放记录'}
        </Text>
      </View>
    </View>
  )
}
