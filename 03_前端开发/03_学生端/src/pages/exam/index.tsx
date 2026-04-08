import { View, Text, Button, Radio, RadioGroup, Input } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Exam() {
  const [exams, setExams] = useState([])
  const [currentExam, setCurrentExam] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})

  useEffect(() => {
    fetchExams()
  }, [])

  const fetchExams = async () => {
    try {
      const res = await api.get('/exam/exams/')
      setExams(res.data?.results || res.data || [])
    } catch (e) { console.error(e) }
  }

  const startExam = (exam) => {
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
      await api.post(`/exam/exams/${currentExam.id}/submit/`, { answers })
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
                <Text>时间: {exam.start_time} - {exam.end_time}</Text>
              </View>
              <Button className="start-btn" onClick={() => startExam(exam)}>开始答题</Button>
            </View>
          ))
        ) : (
          <Text className="empty">暂无考试</Text>
        )}
      </View>
    </View>
  )
}
