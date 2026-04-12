import { View, Text, Button, ScrollView, InputNumber, Form } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function ExamGrading() {
  const [exams, setExams] = useState<any[]>([])
  const [selectedExam, setSelectedExam] = useState<any>(null)
  const [essayAnswers, setEssayAnswers] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchExams()
  }, [])

  const fetchExams = async () => {
    try {
      const res = await api.get('/exam/exams/')
      setExams(res.results || res || [])
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取考试失败', icon: 'none' })
    }
  }

  const handleSelectExam = async (exam) => {
    setSelectedExam(exam)
    setLoading(true)
    try {
      const res = await api.get(`/exam/exams/${exam.id}/essay_answers/`)
      setEssayAnswers(res.answers || [])
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取主观题答案失败', icon: 'none' })
    } finally {
      setLoading(false)
    }
  }

  const handleGrade = async (answer) => {
    if (answer.score === null || answer.score === undefined) {
      Taro.showToast({ title: '请输入分数', icon: 'none' })
      return
    }

    try {
      await api.post(`/exam/exams/${selectedExam.id}/grade_essay/`, {
        answer_id: answer.id,
        score: answer.score
      })
      Taro.showToast({ title: '批改成功', icon: 'success' })
      // 重新获取答案列表
      handleSelectExam(selectedExam)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '批改失败', icon: 'none' })
    }
  }

  return (
    <View className="exam-grading-container">
      <View className="header">
        <Text className="title">主观题批改</Text>
      </View>

      <View className="exam-list">
        <Text className="section-title">选择考试</Text>
        {exams.map((exam, index) => (
          <View 
            key={index} 
            className={`exam-item ${selectedExam?.id === exam.id ? 'active' : ''}`}
            onClick={() => handleSelectExam(exam)}
          >
            <Text className="exam-name">{exam.name}</Text>
            <Text className="exam-info">{exam.paper_name} - {exam.edu_class?.name || '无班级'}</Text>
            <Text className="exam-time">{exam.start_time} 至 {exam.end_time}</Text>
          </View>
        ))}
      </View>

      {selectedExam && (
        <View className="grading-section">
          <Text className="section-title">主观题答案</Text>
          {loading ? (
            <Text className="loading">加载中...</Text>
          ) : essayAnswers.length > 0 ? (
            <ScrollView className="answer-list">
              {essayAnswers.map((answer, index) => (
                <View key={index} className="answer-card">
                  <View className="answer-header">
                    <Text className="student-id">学生ID: {answer.student_id}</Text>
                    <Text className="question-score">满分: {answer.question_score}</Text>
                  </View>
                  <View className="question-content">
                    <Text className="label">题目:</Text>
                    <Text className="content">{answer.question_content}</Text>
                  </View>
                  <View className="student-answer">
                    <Text className="label">学生答案:</Text>
                    <Text className="content">{answer.answer}</Text>
                  </View>
                  <View className="grading-area">
                    <Text className="label">得分:</Text>
                    <View className="score-input">
                      <InputNumber 
                        min={0} 
                        max={answer.question_score} 
                        value={answer.score} 
                        onChange={(value) => {
                          const updatedAnswers = [...essayAnswers]
                          updatedAnswers[index].score = value
                          setEssayAnswers(updatedAnswers)
                        }}
                      />
                      <Text className="score-unit">分</Text>
                    </View>
                    <Button 
                      className="grade-btn" 
                      onClick={() => handleGrade(answer)}
                    >
                      提交批改
                    </Button>
                  </View>
                </View>
              ))}
            </ScrollView>
          ) : (
            <Text className="empty">暂无主观题答案</Text>
          )}
        </View>
      )}
    </View>
  )
}
