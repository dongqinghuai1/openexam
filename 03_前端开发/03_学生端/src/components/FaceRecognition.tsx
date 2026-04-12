import { View, Text, Button, Camera } from '@tarojs/components'
import { useState, useEffect, useRef } from 'react'
import Taro from '@tarojs/taro'
import './FaceRecognition.scss'

export default function FaceRecognition({ onVerifySuccess, onVerifyFail, onCancel }) {
  const [isCapturing, setIsCapturing] = useState(false)
  const [captureResult, setCaptureResult] = useState('')
  const [verificationStatus, setVerificationStatus] = useState('')
  const cameraRef = useRef(null)

  const captureImage = async () => {
    setIsCapturing(true)
    setVerificationStatus('正在拍摄照片...')
    
    try {
      // 模拟人脸识别过程
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 模拟人脸识别结果
      const isSuccess = Math.random() > 0.3 // 70%的概率验证成功
      
      if (isSuccess) {
        setVerificationStatus('人脸识别成功！')
        setCaptureResult('验证通过')
        setTimeout(() => {
          onVerifySuccess()
        }, 1000)
      } else {
        setVerificationStatus('人脸识别失败，请重试')
        setCaptureResult('验证失败')
        setTimeout(() => {
          onVerifyFail()
        }, 1000)
      }
    } catch (error) {
      console.error('人脸识别失败:', error)
      setVerificationStatus('人脸识别失败，请重试')
      setCaptureResult('验证失败')
      setTimeout(() => {
        onVerifyFail()
      }, 1000)
    } finally {
      setIsCapturing(false)
    }
  }

  return (
    <View className="face-recognition-container">
      <View className="header">
        <Text className="title">身份验证</Text>
        <Text className="subtitle">请确保光线充足，正面面对摄像头</Text>
      </View>
      
      <View className="camera-container">
        <Camera
          ref={cameraRef}
          style={{ width: '100%', height: '300px' }}
          mode="user"
          device-position="front"
          flash="off"
        />
        <View className="guide">
          <View className="face-frame">
            <Text className="guide-text">请将面部置于框内</Text>
          </View>
        </View>
      </View>
      
      <View className="status">
        <Text className={`status-text ${verificationStatus.includes('成功') ? 'success' : verificationStatus.includes('失败') ? 'error' : ''}`}>
          {verificationStatus}
        </Text>
      </View>
      
      <View className="actions">
        <Button 
          className="capture-btn" 
          onClick={captureImage} 
          disabled={isCapturing}
        >
          {isCapturing ? '验证中...' : '开始验证'}
        </Button>
        <Button className="cancel-btn" onClick={onCancel}>
          取消
        </Button>
      </View>
    </View>
  )
}
