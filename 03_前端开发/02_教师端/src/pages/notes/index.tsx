import { View, Text, Textarea, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro from '@tarojs/taro'
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

const stringifyNoteContent = (payload: { summary: string; homework: string; parentFeedback: string }) => {
  return JSON.stringify(payload)
}

export default function Notes() {
  const [schedules, setSchedules] = useState<any[]>([])
  const [notes, setNotes] = useState<any[]>([])
  const [selectedScheduleId, setSelectedScheduleId] = useState<number | null>(null)
  const [noteForm, setNoteForm] = useState({ summary: '', homework: '', parentFeedback: '' })
  const [saving, setSaving] = useState(false)

  const selectedSchedule = useMemo(
    () => schedules.find(item => item.id === selectedScheduleId) || null,
    [schedules, selectedScheduleId]
  )

  useEffect(() => {
    fetchSchedulesAndNotes()
  }, [])

  const fetchSchedulesAndNotes = async () => {
    try {
      const user = Taro.getStorageSync('userInfo')
      const teacherRes = await api.get('/edu/teachers/', { phone: user?.phone || user?.username })
      const teachers = teacherRes.results || teacherRes || []
      const teacher = Array.isArray(teachers) ? teachers[0] : null
      if (!teacher) {
        Taro.showToast({ title: '未找到教师档案', icon: 'none' })
        return
      }

      const today = new Date().toISOString().split('T')[0]
      const scheduleRes = await api.get('/edu/schedules/', {
        teacher: teacher.id,
        date__gte: today,
        page_size: 100,
      })
      const scheduleList = scheduleRes.results || scheduleRes || []
      setSchedules(scheduleList)

      if (scheduleList.length) {
        setSelectedScheduleId(scheduleList[0].id)
      }

      const noteRes = await api.get('/classroom/notes/', { page_size: 100 })
      setNotes(noteRes.results || noteRes || [])
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取课堂笔记失败', icon: 'none' })
    }
  }

  const saveNote = async () => {
    if (!selectedScheduleId || !noteForm.summary.trim()) {
      Taro.showToast({ title: '请选择课次并填写课堂总结', icon: 'none' })
      return
    }

    setSaving(true)
    try {
      const existing = notes.find(item => item.schedule === selectedScheduleId)
      const content = stringifyNoteContent(noteForm)
      if (existing) {
        await api.put(`/classroom/notes/${existing.id}/`, { schedule: selectedScheduleId, content })
      } else {
        await api.post('/classroom/notes/', { schedule: selectedScheduleId, content })
      }
      Taro.showToast({ title: '保存成功', icon: 'success' })
      await fetchSchedulesAndNotes()
    } catch (e: any) {
      Taro.showToast({ title: e.message || '保存课堂笔记失败', icon: 'none' })
    } finally {
      setSaving(false)
    }
  }

  useEffect(() => {
    if (!selectedScheduleId) {
      setNoteForm({ summary: '', homework: '', parentFeedback: '' })
      return
    }
    const note = notes.find(item => item.schedule === selectedScheduleId)
    setNoteForm(parseNoteContent(note?.content || ''))
  }, [selectedScheduleId, notes])

  return (
    <View className='notes-page'>
      <View className='header'>
        <Text className='title'>课堂笔记</Text>
        <Text className='subtitle'>记录课堂重点、学生状态和课后跟进</Text>
      </View>

      <View className='section'>
        <Text className='section-title'>选择课次</Text>
        <View className='schedule-list'>
          {schedules.length ? schedules.map((item) => (
            <View
              key={item.id}
              className={`schedule-card ${selectedScheduleId === item.id ? 'active' : ''}`}
              onClick={() => setSelectedScheduleId(item.id)}
            >
              <Text className='schedule-date'>{item.date}</Text>
              <Text className='schedule-main'>{item.class_name}</Text>
              <Text className='schedule-sub'>{item.course_name} | {item.start_time?.substring(0, 5)}-{item.end_time?.substring(0, 5)}</Text>
            </View>
          )) : <View className='empty'>暂无可记录的课次</View>}
        </View>
      </View>

      <View className='section'>
        <Text className='section-title'>课后跟进</Text>
        <View className='note-card'>
          <Text className='note-meta'>当前课次：{selectedSchedule ? `${selectedSchedule.class_name} / ${selectedSchedule.course_name}` : '未选择'}</Text>
          <Text className='field-label'>课堂总结</Text>
          <Textarea
            className='note-input'
            maxlength={1200}
            value={noteForm.summary}
            onInput={(e) => setNoteForm(prev => ({ ...prev, summary: e.detail.value }))}
            placeholder='记录课堂表现、重难点掌握、学生状态等'
          />
          <Text className='field-label'>作业布置</Text>
          <Textarea
            className='note-input small'
            maxlength={800}
            value={noteForm.homework}
            onInput={(e) => setNoteForm(prev => ({ ...prev, homework: e.detail.value }))}
            placeholder='填写课后作业、复习建议、下节课准备内容'
          />
          <Text className='field-label'>家长反馈</Text>
          <Textarea
            className='note-input small'
            maxlength={800}
            value={noteForm.parentFeedback}
            onInput={(e) => setNoteForm(prev => ({ ...prev, parentFeedback: e.detail.value }))}
            placeholder='记录要同步给家长的重点、提醒和沟通结论'
          />
          <Button className='save-btn' loading={saving} onClick={saveNote}>保存笔记</Button>
        </View>
      </View>
    </View>
  )
}
