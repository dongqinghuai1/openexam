import { View, Text, Button, Radio, RadioGroup, Input } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Exam() {
  const [exams, setExams] = useState<any[]>([])
  const [currentExam, setCurrentExam] = useState<any>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})

  const isExamAvailable = (exam: any) => {
    if (exam.status === 'ended') return false
    const now = new Date().getTime()
    const startAt = exam.start_time ? new Date(exam.start_time).getTime() : 0
    const endAt = exam.end_time ? new Date(exam.end_time).getTime() : 0
    if (endAt && endAt < now) return false
    return !startAt || startAt <= now
  }

  useEffect(() => {
    fetchExams()
  }, [])

  const fetchExams = async () => {
    try {
      const studentId = Taro.getStorageSync('studentId')
      if (!studentId) {
        setExams([])
        return
      }

      const scheduleRes = await api.get(`/edu/students/${studentId}/schedules/`)
      const schedules = scheduleRes || []
      const classIds = new Set(schedules.map((item: any) => item.edu_class).filter(Boolean))

      if (!classIds.size) {
        setExams([])
        return
      }

      const res = await api.get('/exam/exams/')
      const list = res.results || res || []
      setExams(
        list.filter((item) => item.edu_class && classIds.has(item.edu_class) && item.status !== 'ended')
      )
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取考试失败', icon: 'none' })
    }
  }

  const startExam = (exam) => {
    if (!isExamAvailable(exam)) {
      Taro.showToast({ title: '考试尚未开始', icon: 'none' })
      return
    }
    setCurrentExam(exam)
    setCurrentQuestion(0)
    setAnswers({})
  }

  const submitAnswer = (answer) => {
    setAnswers({ ...answers, [currentQuestion]: answer })
  }

  const nextQuestion = () => {
    if (currentQuestion < (currentExam.questions?.length || 0) - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const submitExam = async () => {
    try {
      const studentId = Taro.getStorageSync('studentId')
      await api.post(`/exam/exams/${currentExam.id}/submit/`, { answers, student_id: studentId })
      Taro.showToast({ title: '提交成功', icon: 'success' })
      setCurrentExam(null)
    } catch (e) {
      Taro.showToast({ title: '提交失败', icon: 'none' })
    }
  }

  if (currentExam) {
    const question = currentExam.questions?.[currentQuestion]
    return (
      <View className="exam-container">
        <View className="exam-header">
          <Text className="title">{currentExam.name}</Text>
          <Text className="progress">{currentQuestion + 1}/{currentExam.questions?.length || 0}</Text>
        </View>
        <View className="question-card">
          <Text className="q-title">第{currentQuestion + 1}题</Text>
          <Text className="q-content">{question?.content}</Text>
          <RadioGroup onChange={(e) => submitAnswer(e.detail.value)}>
            {question?.options?.map((opt, idx) => (
              <View className="option" key={idx}>
                <Radio value={opt.key} checked={answers[currentQuestion] === opt.key} />
                <Text className="opt-text">{opt.key}. {opt.value}</Text>
              </View>
            ))}
          </RadioGroup>
        </View>
        <View className="exam-actions">
          {currentQuestion < (currentExam.questions?.length || 0) - 1 ? (
            <Button className="next-btn" onClick={nextQuestion}>下一题</Button>
          ) : (
            <Button className="submit-btn" onClick={submitExam}>提交试卷</Button>
          )}
        </View>
      </View>
    )
  }

  return (
    <View className="exam-page">
      <View className="section">
        <Text className="section-title">可参加的考试</Text>
        {exams.length > 0 ? (
          exams.map((exam, index) => (
            <View className="exam-card" key={index}>
               <View className="exam-name">{exam.name}</View>
               <View className="exam-info">
                  <Text>试卷: {exam.paper_name}</Text>
                  <Text>班级: {exam.class_name || '-'}</Text>
                  <Text>时间: {exam.start_time} - {exam.end_time}</Text>
                  <Text>状态: {isExamAvailable(exam) ? '可参加' : '未开始'}</Text>
               </View>
               <Button className="start-btn" disabled={!isExamAvailable(exam)} onClick={() => startExam(exam)}>
                 {isExamAvailable(exam) ? '开始答题' : '等待开始'}
               </Button>
             </View>
           ))
        ) : (
          <Text className="empty">暂无考试</Text>
        )}
      </View>
    </View>
  )
}
