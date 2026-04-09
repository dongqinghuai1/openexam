import { View, Text } from '@tarojs/components'
import { useMemo, useState, useEffect } from 'react'
import Taro from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function Scores() {
  const [scores, setScores] = useState<any[]>([])
  const [selectedExam, setSelectedExam] = useState('all')

  useEffect(() => {
    fetchScores()
  }, [])

  const fetchScores = async () => {
    try {
      const studentId = Taro.getStorageSync('studentId')
      const res = await api.get('/exam/scores/', { student_id: studentId })
      setScores(res.results || res || [])
    } catch (e) { console.error(e) }
  }

  const getScoreLevel = (score: number, total: number) => {
    const percent = (score / total) * 100
    if (percent >= 90) return 'A'
    if (percent >= 80) return 'B'
    if (percent >= 70) return 'C'
    if (percent >= 60) return 'D'
    return 'F'
  }

  const examOptions = useMemo(() => {
    const map = new Map()
    scores.forEach((item) => {
      const name = item.exam_name || item.exam?.name || '考试'
      if (!map.has(name)) {
        map.set(name, name)
      }
    })
    return ['all', ...Array.from(map.values())]
  }, [scores])

  const filteredScores = useMemo(() => {
    if (selectedExam === 'all') return scores
    return scores.filter((item) => (item.exam_name || item.exam?.name || '考试') === selectedExam)
  }, [scores, selectedExam])

  const summary = useMemo(() => {
    if (!scores.length) {
      return { latest: '-', highest: '-', average: '-' }
    }
    const latest = scores[0]?.score ?? '-'
    const highest = Math.max(...scores.map(item => Number(item.score || 0)))
    const average = Math.round(scores.reduce((sum, item) => sum + Number(item.score || 0), 0) / scores.length)
    return { latest, highest, average }
  }, [scores])

  const trendData = useMemo(() => {
    return scores.slice(0, 5).reverse().map((item, index) => ({
      label: item.exam_name || `考试${index + 1}`,
      score: Number(item.score || 0),
      total: Number(item.total_score || 100),
    }))
  }, [scores])

  const levelDistribution = useMemo(() => {
    const base = { A: 0, B: 0, C: 0, D: 0, F: 0 }
    scores.forEach((item) => {
      const level = getScoreLevel(item.score, item.total_score)
      base[level] += 1
    })
    return base
  }, [scores])

  return (
    <View className="scores-page">
      <View className="header">
        <Text className="title">成绩查询</Text>
      </View>

      <View className="content">
        <View className="summary-card">
          <View className="summary-item">
            <Text className="summary-label">最近得分</Text>
            <Text className="summary-value">{summary.latest}</Text>
          </View>
          <View className="summary-item">
            <Text className="summary-label">最高分</Text>
            <Text className="summary-value">{summary.highest}</Text>
          </View>
          <View className="summary-item">
            <Text className="summary-label">平均分</Text>
            <Text className="summary-value">{summary.average}</Text>
          </View>
        </View>

        <View className="filter-row">
          {examOptions.map((item) => (
            <View
              key={item}
              className={`filter-chip ${selectedExam === item ? 'active' : ''}`}
              onClick={() => setSelectedExam(item)}
            >
              <Text>{item === 'all' ? '全部考试' : item}</Text>
            </View>
          ))}
        </View>

        <View className="trend-card">
          <Text className="block-title">最近成绩趋势</Text>
          {trendData.length ? trendData.map((item, index) => (
            <View className="trend-row" key={index}>
              <Text className="trend-label">{item.label}</Text>
              <View className="trend-bar-wrap">
                <View className="trend-bar" style={{ width: `${Math.max(8, Math.round((item.score / item.total) * 100))}%` }} />
              </View>
              <Text className="trend-score">{item.score}</Text>
            </View>
          )) : <Text className="empty-inline">暂无趋势数据</Text>}
        </View>

        <View className="distribution-card">
          <Text className="block-title">等级分布</Text>
          <View className="distribution-grid">
            {Object.entries(levelDistribution).map(([level, count]) => (
              <View className={`distribution-item level-${level}`} key={level}>
                <Text className="distribution-level">{level}</Text>
                <Text className="distribution-count">{count}</Text>
              </View>
            ))}
          </View>
        </View>

        {filteredScores.length > 0 ? (
          filteredScores.map((item: any, index: number) => (
            <View className="score-card" key={index}>
              <View className="exam-name">{item.exam_name || item.exam?.name || '考试'}</View>
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
              <View className="exam-time">{item.created_at}</View>
            </View>
          ))
        ) : (
          <View className="empty">当前筛选下暂无成绩记录</View>
        )}
      </View>
    </View>
  )
}
