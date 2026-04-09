import { View, Text, Button } from '@tarojs/components'
import { useEffect, useMemo, useState } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import api from '../../utils/api'
import './index.scss'

export default function ExamResult() {
  const router = useRouter()
  const examId = Number(router.params?.examId)
  const [result, setResult] = useState<any>(null)

  const level = useMemo(() => {
    if (!result?.total_score) return '-'
    const percent = (result.score / result.total_score) * 100
    if (percent >= 90) return 'A'
    if (percent >= 80) return 'B'
    if (percent >= 70) return 'C'
    if (percent >= 60) return 'D'
    return 'F'
  }, [result])

  useEffect(() => {
    fetchResult()
  }, [examId])

  const fetchResult = async () => {
    try {
      const studentId = Taro.getStorageSync('studentId')
      const res = await api.get('/exam/scores/', { student_id: studentId, exam: examId })
      const list = res.results || res || []
      setResult(list[0] || null)
    } catch (e: any) {
      Taro.showToast({ title: e.message || '获取考试结果失败', icon: 'none' })
    }
  }

  if (!result) {
    return <View className='exam-result-page'><View className='empty'>考试结果加载中...</View></View>
  }

  return (
    <View className='exam-result-page'>
      <View className='hero-card'>
        <Text className='hero-title'>{result.exam_name || '考试结果'}</Text>
        <Text className='hero-score'>{result.score} / {result.total_score}</Text>
        <Text className={`hero-level level-${level}`}>等级 {level}</Text>
      </View>

      <View className='section score-grid'>
        <View className='score-item'><Text className='label'>得分</Text><Text className='value'>{result.score}</Text></View>
        <View className='score-item'><Text className='label'>总分</Text><Text className='value'>{result.total_score}</Text></View>
        <View className='score-item'><Text className='label'>排名</Text><Text className='value'>{result.rank || '-'}</Text></View>
        <View className='score-item'><Text className='label'>等级</Text><Text className='value'>{level}</Text></View>
      </View>

      <View className='section'>
        <Text className='section-title'>结果说明</Text>
        <Text className='desc'>你已完成本次考试，可在成绩记录中查看历史结果，也可以返回考试中心继续查看其他待参加考试。</Text>
      </View>

      <View className='section action-list'>
        <Button className='primary-btn' onClick={() => Taro.navigateTo({ url: '/pages/scores/index' })}>查看成绩记录</Button>
        <Button className='secondary-btn' onClick={() => Taro.switchTab({ url: '/pages/exam/index' })}>返回考试中心</Button>
      </View>
    </View>
  )
}
