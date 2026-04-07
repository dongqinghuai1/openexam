import { View, Text } from '@tarojs/components'
import { useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Scores() {
  const [children, setChildren] = useState<any[]>([])
  const [selectedChild, setSelectedChild] = useState<any>(null)
  const [scores, setScores] = useState<any[]>([])

  useEffect(() => {
    fetchChildren()
  }, [])

  const fetchChildren = async () => {
    try {
      const res = await api.get('/edu/students/')
      const students = res.data?.results || res.data || []
      setChildren(students)
      if (students.length > 0) {
        setSelectedChild(students[0])
        fetchScores(students[0].id)
      }
    } catch (e) { console.error(e) }
  }

  const fetchScores = async (studentId: number) => {
    try {
      const res = await api.get('/exam/scores/', { student_id: studentId })
      setScores(res.data?.results || res.data || [])
    } catch (e) { console.error(e) }
  }

  const handleChildChange = (child: any) => {
    setSelectedChild(child)
    fetchScores(child.id)
  }

  const getScoreLevel = (score: number, total: number) => {
    const percent = (score / total) * 100
    if (percent >= 90) return 'A'
    if (percent >= 80) return 'B'
    if (percent >= 70) return 'C'
    if (percent >= 60) return 'D'
    return 'F'
  }

  return (
    <View className="scores-page">
      <View className="header">
        <Text className="title">成绩查询</Text>
      </View>

      {children.length > 1 && (
        <View className="child-selector">
          {children.map((child: any) => (
            <View 
              key={child.id} 
              className={`child-tag ${selectedChild?.id === child.id ? 'active' : ''}`}
              onClick={() => handleChildChange(child)}
            >
              {child.name}
            </View>
          ))}
        </View>
      )}

      <View className="content">
        {scores.length > 0 ? (
          scores.map((item: any, index: number) => (
            <View className="score-card" key={index}>
              <View className="exam-name">{item.exam?.name || '考试'}</View>
              <View className="score-info">
                <View className="score-item">
                  <Text className="label">得分</Text>
                  <Text className="value">{item.score}</Text>
                </View>
                <View className="score-item">
                  <Text className="label">总分</Text>
                  <Text className="value">{item.total_score}</Text>
                </View>
                <View className="score-item">
                  <Text className="label">等级</Text>
                  <Text className={`value level ${getScoreLevel(item.score, item.total_score)}`}>
                    {getScoreLevel(item.score, item.total_score)}
                  </Text>
                </View>
                <View className="score-item">
                  <Text className="label">排名</Text>
                  <Text className="value">{item.rank || '-'}</Text>
                </View>
              </View>
            </View>
          ))
        ) : (
          <View className="empty">暂无成绩记录</View>
        )}
      </View>
    </View>
  )
}