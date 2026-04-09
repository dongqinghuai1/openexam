import { View, Text, Button } from '@tarojs/components'
import { useMemo } from 'react'
import Taro, { useRouter } from '@tarojs/taro'
import './index.scss'

export default function LinkPage() {
  const router = useRouter()
  const { title = '链接页', url = '', type = 'link' } = router.params || {}
  const decodedUrl = useMemo(() => decodeURIComponent(url || ''), [url])

  const handleCopy = () => {
    if (!decodedUrl) return
    Taro.setClipboardData({ data: decodedUrl })
    Taro.showToast({ title: '链接已复制', icon: 'none' })
  }

  return (
    <View className='link-page'>
      <View className='card'>
        <Text className='title'>{title}</Text>
        <Text className='tag'>{type === 'classroom' ? '课堂入口' : '回放入口'}</Text>
        <Text className='desc'>如果需要查看课堂或回放内容，请复制该链接后在浏览器中打开。</Text>
        <View className='url-box'>
          <Text className='url'>{decodedUrl || '暂无可用链接'}</Text>
        </View>
        <Button className='copy-btn' disabled={!decodedUrl} onClick={handleCopy}>复制链接</Button>
      </View>
    </View>
  )
}
