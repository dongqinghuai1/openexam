<template>
  <div class="webrtc-meeting">
    <el-dialog
      :model-value="visible"
      @update:model-value="$emit('update:visible', $event)"
      :title="`在线课堂 - ${meetingInfo?.schedule?.edu_class?.name || ''} - ${meetingInfo?.schedule?.course?.name || ''}`"
      width="90%"
      height="90vh"
      destroy-on-close
    >
      <div class="meeting-container">
        <!-- 本地视频 -->
        <div class="local-video-container">
          <video ref="localVideo" autoplay muted></video>
          <div class="video-controls">
            <el-button @click="toggleAudio" :icon="audioEnabled ? 'Microphone' : 'Mute'" :type="audioEnabled ? 'primary' : 'info'" circle></el-button>
            <el-button @click="toggleVideo" :icon="videoEnabled ? 'VideoCamera' : 'VideoCameraOff'" :type="videoEnabled ? 'primary' : 'info'" circle></el-button>
            <el-button @click="toggleScreenShare" :icon="screenSharing ? 'Monitor' : 'Monitor'" :type="screenSharing ? 'primary' : 'info'" circle></el-button>
            <el-button @click="toggleWhiteboard" :icon="'Notebook'" :type="whiteboardVisible ? 'primary' : 'info'" circle></el-button>
            <el-button @click="leaveMeeting" icon="Close" type="danger" circle></el-button>
          </div>
        </div>
        
        <!-- 互动白板 -->
        <div v-if="whiteboardVisible" class="whiteboard-container">
          <div class="whiteboard-header">
            <span>互动白板</span>
            <el-button @click="toggleWhiteboard" icon="Close" circle></el-button>
          </div>
          <div class="whiteboard-content">
            <canvas ref="whiteboardCanvas" width="800" height="600"></canvas>
            <div class="whiteboard-controls">
              <el-button @click="setTool('pen')" :type="currentTool === 'pen' ? 'primary' : 'info'">画笔</el-button>
              <el-button @click="setTool('eraser')" :type="currentTool === 'eraser' ? 'primary' : 'info'">橡皮擦</el-button>
              <el-button @click="setTool('text')" :type="currentTool === 'text' ? 'primary' : 'info'">文本</el-button>
              <el-button @click="clearWhiteboard">清空</el-button>
              <el-color-picker v-model="penColor" @change="updatePenColor" />
              <el-input-number v-model="penSize" :min="1" :max="10" @change="updatePenSize" />
            </div>
          </div>
        </div>
        
        <!-- 远程视频 -->
        <div class="remote-videos">
          <div v-for="(remoteStream, id) in remoteStreams" :key="id" class="remote-video">
            <video :ref="el => setRemoteVideo(el, id)" autoplay></video>
            <div class="remote-info">{{ getRemoteUserName(id) }}</div>
          </div>
          <div v-if="remoteStreams.size === 0" class="no-remote">
            <el-empty description="暂无其他参会者" />
          </div>
        </div>
        
        <!-- 聊天区域 -->
        <div class="chat-container">
          <div class="chat-header">
            <span>聊天</span>
          </div>
          <div class="chat-messages" ref="chatMessages">
            <div v-for="(message, index) in messages" :key="index" class="chat-message">
              <span class="message-sender">{{ message.sender }}:</span>
              <span class="message-content">{{ message.content }}</span>
            </div>
          </div>
          <div class="chat-input">
            <el-input v-model="chatInput" placeholder="输入消息..." @keyup.enter="sendMessage" />
            <el-button @click="sendMessage" type="primary">发送</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '@/stores/user'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  meetingRoomId: {
    type: Number,
    required: true
  },
  meetingInfo: {
    type: Object,
    default: () => {}
  }
})

const emit = defineEmits(['update:visible', 'leave'])

const localVideo = ref(null)
const chatMessages = ref(null)
const chatInput = ref('')
const messages = ref([])
const audioEnabled = ref(true)
const videoEnabled = ref(true)
const screenSharing = ref(false)
const whiteboardVisible = ref(false)
const currentTool = ref('pen')
const penColor = ref('#000000')
const penSize = ref(2)
const remoteStreams = ref(new Map())
const peerConnections = ref(new Map())
const remoteVideos = ref(new Map())
const signalingInterval = ref(null)
const localStream = ref(null)
const screenStream = ref(null)
const whiteboardCanvas = ref(null)
const canvasContext = ref(null)
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)

// 生成唯一标识符
const userId = ref(Math.random().toString(36).substr(2, 9))
const userName = ref('User' + userId.value)

// 设置远程视频元素
function setRemoteVideo(el, id) {
  if (el) {
    remoteVideos.value.set(id, el)
  }
}

// 获取远程用户名称
function getRemoteUserName(id) {
  return 'User' + id.substring(0, 5)
}

// 切换音频
function toggleAudio() {
  if (localStream.value) {
    localStream.value.getAudioTracks().forEach(track => {
      track.enabled = !audioEnabled.value
    })
    audioEnabled.value = !audioEnabled.value
  }
}

// 切换视频
function toggleVideo() {
  if (localStream.value) {
    localStream.value.getVideoTracks().forEach(track => {
      track.enabled = !videoEnabled.value
    })
    videoEnabled.value = !videoEnabled.value
  }
}

// 离开会议
function leaveMeeting() {
  // 关闭所有peer连接
  peerConnections.value.forEach(pc => {
    pc.close()
  })
  peerConnections.value.clear()
  remoteStreams.value.clear()
  
  // 停止本地流
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => {
      track.stop()
    })
  }
  
  // 停止屏幕共享流
  if (screenStream.value) {
    screenStream.value.getTracks().forEach(track => {
      track.stop()
    })
  }
  
  // 清除信令轮询
  if (signalingInterval.value) {
    clearInterval(signalingInterval.value)
  }
  
  // 关闭对话框
  emit('update:visible', false)
  emit('leave')
}

// 切换屏幕共享
async function toggleScreenShare() {
  try {
    if (!screenSharing.value) {
      // 开始屏幕共享
      screenStream.value = await navigator.mediaDevices.getDisplayMedia({
        video: true
      })
      
      // 替换本地流中的视频轨道
      if (localStream.value) {
        const videoTrack = screenStream.value.getVideoTracks()[0]
        const sender = localStream.value.getVideoTracks()[0]
        
        // 替换所有peer连接中的视频轨道
        peerConnections.value.forEach(pc => {
          const senders = pc.getSenders()
          senders.forEach(sender => {
            if (sender.track.kind === 'video') {
              sender.replaceTrack(videoTrack)
            }
          })
        })
        
        // 更新本地视频显示
        if (localVideo.value) {
          localVideo.value.srcObject = screenStream.value
        }
        
        // 监听屏幕共享结束
        screenStream.value.getVideoTracks()[0].onended = () => {
          screenSharing.value = false
          // 恢复摄像头
          navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            localStream.value = stream
            if (localVideo.value) {
              localVideo.value.srcObject = stream
            }
            // 替换所有peer连接中的视频轨道
            peerConnections.value.forEach(pc => {
              const senders = pc.getSenders()
              senders.forEach(sender => {
                if (sender.track.kind === 'video') {
                  sender.replaceTrack(stream.getVideoTracks()[0])
                }
              })
            })
          })
        }
        
        screenSharing.value = true
      }
    } else {
      // 停止屏幕共享
      if (screenStream.value) {
        screenStream.value.getTracks().forEach(track => {
          track.stop()
        })
      }
      
      // 恢复摄像头
      navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
        localStream.value = stream
        if (localVideo.value) {
          localVideo.value.srcObject = stream
        }
        // 替换所有peer连接中的视频轨道
        peerConnections.value.forEach(pc => {
          const senders = pc.getSenders()
          senders.forEach(sender => {
            if (sender.track.kind === 'video') {
              sender.replaceTrack(stream.getVideoTracks()[0])
            }
          })
        })
      })
      
      screenSharing.value = false
    }
  } catch (error) {
    console.error('屏幕共享失败:', error)
    ElMessage.error('屏幕共享失败，请检查权限设置')
  }
}

// 切换白板
function toggleWhiteboard() {
  whiteboardVisible.value = !whiteboardVisible.value
  if (whiteboardVisible.value) {
    initWhiteboard()
  }
}

// 初始化白板
function initWhiteboard() {
  if (whiteboardCanvas.value) {
    canvasContext.value = whiteboardCanvas.value.getContext('2d')
    // 设置默认画笔样式
    canvasContext.value.lineWidth = penSize.value
    canvasContext.value.strokeStyle = penColor.value
    canvasContext.value.lineCap = 'round'
    
    // 添加鼠标事件
    whiteboardCanvas.value.addEventListener('mousedown', startDrawing)
    whiteboardCanvas.value.addEventListener('mousemove', draw)
    whiteboardCanvas.value.addEventListener('mouseup', stopDrawing)
    whiteboardCanvas.value.addEventListener('mouseout', stopDrawing)
  }
}

// 开始绘制
function startDrawing(e) {
  isDrawing.value = true
  const rect = whiteboardCanvas.value.getBoundingClientRect()
  lastX.value = e.clientX - rect.left
  lastY.value = e.clientY - rect.top
}

// 绘制
function draw(e) {
  if (!isDrawing.value) return
  
  const rect = whiteboardCanvas.value.getBoundingClientRect()
  const currentX = e.clientX - rect.left
  const currentY = e.clientY - rect.top
  
  if (currentTool.value === 'pen') {
    canvasContext.value.beginPath()
    canvasContext.value.moveTo(lastX.value, lastY.value)
    canvasContext.value.lineTo(currentX, currentY)
    canvasContext.value.stroke()
  } else if (currentTool.value === 'eraser') {
    canvasContext.value.clearRect(currentX - penSize.value, currentY - penSize.value, penSize.value * 2, penSize.value * 2)
  }
  
  lastX.value = currentX
  lastY.value = currentY
  
  // 发送白板绘制事件
  sendWhiteboardData({
    type: 'draw',
    tool: currentTool.value,
    startX: lastX.value,
    startY: lastY.value,
    endX: currentX,
    endY: currentY,
    color: penColor.value,
    size: penSize.value
  })
}

// 停止绘制
function stopDrawing() {
  isDrawing.value = false
}

// 设置工具
function setTool(tool) {
  currentTool.value = tool
}

// 更新画笔颜色
function updatePenColor(color) {
  penColor.value = color
  if (canvasContext.value) {
    canvasContext.value.strokeStyle = color
  }
}

// 更新画笔大小
function updatePenSize(size) {
  penSize.value = size
  if (canvasContext.value) {
    canvasContext.value.lineWidth = size
  }
}

// 清空白板
function clearWhiteboard() {
  if (canvasContext.value) {
    canvasContext.value.clearRect(0, 0, whiteboardCanvas.value.width, whiteboardCanvas.value.height)
  }
  
  // 发送清空白板事件
  sendWhiteboardData({
    type: 'clear'
  })
}

// 发送白板数据
function sendWhiteboardData(data) {
  sendWebRTCSignal({
    type: 'whiteboard',
    data: data
  })
}

// 处理白板数据
function handleWhiteboardData(data) {
  if (!canvasContext.value) return
  
  switch (data.type) {
    case 'draw':
      if (data.tool === 'pen') {
        canvasContext.value.strokeStyle = data.color
        canvasContext.value.lineWidth = data.size
        canvasContext.value.beginPath()
        canvasContext.value.moveTo(data.startX, data.startY)
        canvasContext.value.lineTo(data.endX, data.endY)
        canvasContext.value.stroke()
      } else if (data.tool === 'eraser') {
        canvasContext.value.clearRect(data.startX - data.size, data.startY - data.size, data.size * 2, data.size * 2)
      }
      break
    case 'clear':
      canvasContext.value.clearRect(0, 0, whiteboardCanvas.value.width, whiteboardCanvas.value.height)
      break
  }
}

// 发送消息
function sendMessage() {
  if (chatInput.value.trim()) {
    const message = {
      sender: userName.value,
      content: chatInput.value.trim()
    }
    messages.value.push(message)
    chatInput.value = ''
    
    // 发送消息到其他参会者
    sendWebRTCSignal({
      type: 'chat',
      message: message
    })
    
    // 滚动到底部
    setTimeout(() => {
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    }, 100)
  }
}

// 初始化WebRTC
async function initWebRTC() {
  try {
    // 获取本地媒体流
    localStream.value = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    })
    
    // 显示本地视频
    if (localVideo.value) {
      localVideo.value.srcObject = localStream.value
    }
    
    // 开始信令轮询
    startSignalingPolling()
    
    // 发送加入信号
    sendWebRTCSignal({
      type: 'join',
      userId: userId.value,
      userName: userName.value
    })
    
  } catch (error) {
    console.error('WebRTC初始化失败:', error)
    ElMessage.error('无法访问摄像头或麦克风，请检查权限设置')
  }
}

// 开始信令轮询
function startSignalingPolling() {
  signalingInterval.value = setInterval(async () => {
    try {
      const response = await api.get(`/classroom/meeting_rooms/${props.meetingRoomId}/webrtc_signals/`)
      const signals = response.data.signals
      
      signals.forEach(signal => {
        processWebRTCSignal(signal.signal)
      })
    } catch (error) {
      console.error('获取信令失败:', error)
    }
  }, 1000)
}

// 发送WebRTC信令
async function sendWebRTCSignal(signal) {
  try {
    await api.post(`/classroom/meeting_rooms/${props.meetingRoomId}/webrtc_signal/`, {
      signal: signal
    })
  } catch (error) {
    console.error('发送信令失败:', error)
  }
}

// 处理WebRTC信令
function processWebRTCSignal(signal) {
  switch (signal.type) {
    case 'join':
      // 新用户加入，创建peer连接
      createPeerConnection(signal.userId)
      break
    case 'offer':
      // 收到offer，创建answer
      handleOffer(signal)
      break
    case 'answer':
      // 收到answer，设置远程描述
      handleAnswer(signal)
      break
    case 'ice-candidate':
      // 收到ICE候选，添加到peer连接
      handleICECandidate(signal)
      break
    case 'chat':
      // 收到聊天消息
      messages.value.push(signal.message)
      setTimeout(() => {
        if (chatMessages.value) {
          chatMessages.value.scrollTop = chatMessages.value.scrollHeight
        }
      }, 100)
      break
    case 'whiteboard':
      // 收到白板数据
      handleWhiteboardData(signal.data)
      break
  }
}

// 创建peer连接
function createPeerConnection(remoteUserId) {
  if (peerConnections.value.has(remoteUserId)) {
    return
  }
  
  const pc = new RTCPeerConnection({
    iceServers: [
      {
        urls: ['stun:stun.l.google.com:19302']
      }
    ]
  })
  
  // 添加本地流
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => {
      pc.addTrack(track, localStream.value)
    })
  }
  
  // 处理远程流
  pc.ontrack = (event) => {
    if (!remoteStreams.value.has(remoteUserId)) {
      remoteStreams.value.set(remoteUserId, event.streams[0])
      setTimeout(() => {
        const video = remoteVideos.value.get(remoteUserId)
        if (video) {
          video.srcObject = event.streams[0]
        }
      }, 100)
    }
  }
  
  // 处理ICE候选
  pc.onicecandidate = (event) => {
    if (event.candidate) {
      sendWebRTCSignal({
        type: 'ice-candidate',
        target: remoteUserId,
        candidate: event.candidate
      })
    }
  }
  
  // 保存peer连接
  peerConnections.value.set(remoteUserId, pc)
  
  // 创建offer
  pc.createOffer().then(offer => {
    return pc.setLocalDescription(offer)
  }).then(() => {
    sendWebRTCSignal({
      type: 'offer',
      target: remoteUserId,
      offer: pc.localDescription
    })
  }).catch(error => {
    console.error('创建offer失败:', error)
  })
}

// 处理offer
function handleOffer(signal) {
  const pc = new RTCPeerConnection({
    iceServers: [
      {
        urls: ['stun:stun.l.google.com:19302']
      }
    ]
  })
  
  // 添加本地流
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => {
      pc.addTrack(track, localStream.value)
    })
  }
  
  // 处理远程流
  pc.ontrack = (event) => {
    if (!remoteStreams.value.has(signal.sender)) {
      remoteStreams.value.set(signal.sender, event.streams[0])
      setTimeout(() => {
        const video = remoteVideos.value.get(signal.sender)
        if (video) {
          video.srcObject = event.streams[0]
        }
      }, 100)
    }
  }
  
  // 处理ICE候选
  pc.onicecandidate = (event) => {
    if (event.candidate) {
      sendWebRTCSignal({
        type: 'ice-candidate',
        target: signal.sender,
        candidate: event.candidate
      })
    }
  }
  
  // 设置远程描述
  pc.setRemoteDescription(new RTCSessionDescription(signal.offer)).then(() => {
    return pc.createAnswer()
  }).then(answer => {
    return pc.setLocalDescription(answer)
  }).then(() => {
    sendWebRTCSignal({
      type: 'answer',
      target: signal.sender,
      answer: pc.localDescription
    })
  }).catch(error => {
    console.error('处理offer失败:', error)
  })
  
  // 保存peer连接
  peerConnections.value.set(signal.sender, pc)
}

// 处理answer
function handleAnswer(signal) {
  const pc = peerConnections.value.get(signal.sender)
  if (pc) {
    pc.setRemoteDescription(new RTCSessionDescription(signal.answer)).catch(error => {
      console.error('处理answer失败:', error)
    })
  }
}

// 处理ICE候选
function handleICECandidate(signal) {
  const pc = peerConnections.value.get(signal.sender)
  if (pc) {
    pc.addIceCandidate(new RTCIceCandidate(signal.candidate)).catch(error => {
      console.error('处理ICE候选失败:', error)
    })
  }
}

// 监听visible变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    initWebRTC()
  } else {
    leaveMeeting()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  leaveMeeting()
})
</script>

<style scoped>
.webrtc-meeting {
  width: 100%;
  height: 100%;
}

.meeting-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  grid-template-rows: 1fr;
  gap: 20px;
  height: 70vh;
}

.local-video-container {
  position: absolute;
  top: 20px;
  right: 320px;
  width: 200px;
  height: 150px;
  z-index: 10;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.local-video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 5px;
  background: rgba(0, 0, 0, 0.5);
}

.remote-videos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.remote-video {
  position: relative;
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.remote-video video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remote-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 5px 10px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 12px;
}

.no-remote {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  font-weight: bold;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.chat-message {
  margin-bottom: 10px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.message-sender {
  font-weight: bold;
  margin-right: 10px;
  color: #409eff;
}

.chat-input {
  display: flex;
  padding: 10px 20px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.chat-input .el-input {
  flex: 1;
  margin-right: 10px;
}

.whiteboard-container {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 320px;
  bottom: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 20;
  display: flex;
  flex-direction: column;
}

.whiteboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: #409eff;
  color: white;
  font-weight: bold;
  border-radius: 8px 8px 0 0;
}

.whiteboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.whiteboard-content canvas {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: crosshair;
}

.whiteboard-controls {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e4e7ed;
  flex-wrap: wrap;
}

.whiteboard-controls .el-color-picker {
  margin-left: 10px;
}

.whiteboard-controls .el-input-number {
  width: 80px;
  margin-left: 10px;
}
</style>