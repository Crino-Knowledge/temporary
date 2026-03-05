<template>
  <div class="monitoring-page">
    <el-container>
      <!-- 头部 -->
      <el-header class="page-header">
        <div class="header-content">
          <h1>🧬 实时心率监测</h1>
          <div class="header-actions">
            <el-button 
              type="primary" 
              size="large"
              :loading="isStarting"
              @click="startMonitoring"
              v-if="!isMonitoring"
            >
              <el-icon><VideoPlay /></el-icon>
              开始监测
            </el-button>
            <el-button 
              type="danger" 
              size="large"
              @click="stopMonitoring"
              v-if="isMonitoring"
            >
              <el-icon><VideoPause /></el-icon>
              停止监测
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="page-main">
        <el-row :gutter="20">
          <!-- 左侧：摄像头和状态 -->
          <el-col :span="12">
            <el-card class="camera-card">
              <template #header>
                <div class="card-header">
                  <span>📹 摄像头</span>
                  <el-tag 
                    :type="connectionStatus === 'connected' ? 'success' : 'danger'"
                    size="small"
                  >
                    {{ connectionStatus === 'connected' ? '已连接' : '未连接' }}
                  </el-tag>
                </div>
              </template>
              
              <div class="camera-container">
                <video 
                  ref="videoElement" 
                  autoplay 
                  muted 
                  playsinline
                  class="camera-video"
                  v-show="!maskedFrame"
                ></video>
                <img 
                  v-if="maskedFrame" 
                  :src="maskedFrame" 
                  class="masked-video"
                  alt="处理后的视频帧"
                />
                
                <!-- 人脸检测框 -->
                <div 
                  v-if="faceDetected" 
                  class="face-detection-box"
                ></div>
                
                <!-- 摄像头信息 -->
                <div class="camera-info">
                  <div class="info-item">
                    <span class="label">分辨率:</span>
                    <span class="value">{{ videoResolution }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">帧率:</span>
                    <span class="value">{{ frameRate }} FPS</span>
                  </div>
                  <div class="info-item">
                    <span class="label">处理延迟:</span>
                    <span class="value">{{ processingTime }} ms</span>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 状态卡片 -->
            <el-card class="status-card">
              <template #header>
                <span>📊 监测状态</span>
              </template>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon heart-rate">❤️</div>
                    <div class="status-content">
                      <div class="status-value">{{ heartRate || '--' }}</div>
                      <div class="status-label">心率 (BPM)</div>
                    </div>
                  </div>
                </el-col>
                
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon signal-quality">📊</div>
                    <div class="status-content">
                      <div class="status-value">{{ signalQuality || '--' }}</div>
                      <div class="status-label">信号质量 (%)</div>
                    </div>
                  </div>
                </el-col>
                
                <el-col :span="8">
                  <div class="status-item">
                    <div class="status-icon duration">⏱️</div>
                    <div class="status-content">
                      <div class="status-value">{{ monitoringDuration }}</div>
                      <div class="status-label">监测时长</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>

          <!-- 右侧：图表和数据 -->
          <el-col :span="12">
            <!-- BVP信号图表 -->
            <el-card class="chart-card">
              <template #header>
                <span>📈 BVP 信号波形</span>
              </template>
              
              <div class="chart-container">
                <Line 
                  v-if="bvpChartData.labels.length > 0"
                  :data="bvpChartData"
                  :options="bvpChartOptions"
                  class="chart"
                />
                <div v-else class="no-data">
                  <el-empty description="暂无数据" />
                </div>
              </div>
            </el-card>

            <!-- 心率频谱图表 -->
            <el-card class="chart-card">
              <template #header>
                <span>🎵 心率频谱</span>
              </template>
              
              <div class="chart-container">
                <Bar 
                  v-if="spectrumChartData.labels.length > 0"
                  :data="spectrumChartData"
                  :options="spectrumChartOptions"
                  class="chart"
                />
                <div v-else class="no-data">
                  <el-empty description="暂无数据" />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 底部：详细数据 -->
        <el-row :gutter="20" class="data-section">
          <el-col :span="24">
            <el-card class="data-card">
              <template #header>
                <span>📋 详细数据</span>
              </template>
              
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">当前心率:</span>
                    <span class="data-value">{{ heartRate || '--' }} BPM</span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">平均心率:</span>
                    <span class="data-value">{{ averageHeartRate || '--' }} BPM</span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">最高心率:</span>
                    <span class="data-value">{{ maxHeartRate || '--' }} BPM</span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">最低心率:</span>
                    <span class="data-value">{{ minHeartRate || '--' }} BPM</span>
                  </div>
                </el-col>
              </el-row>
              
              <el-row :gutter="20" class="mt-20">
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">处理帧数:</span>
                    <span class="data-value">{{ frameCount || '--' }}</span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">信号强度:</span>
                    <span class="data-value">{{ signalStrength || '--' }}%</span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">人脸检测:</span>
                    <span class="data-value">
                      <el-tag :type="faceDetected ? 'success' : 'info'">
                        {{ faceDetected ? '已检测' : '未检测' }}
                      </el-tag>
                    </span>
                  </div>
                </el-col>
                
                <el-col :span="6">
                  <div class="data-item">
                    <span class="data-label">系统状态:</span>
                    <span class="data-value">
                      <el-tag :type="systemHealthType">
                        {{ systemHealthText }}
                      </el-tag>
                    </span>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Line, Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js'
import { api, wsManager } from '@/api'

// 注册Chart.js组件
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend)

export default {
  name: 'Monitoring',
  components: {
    Line,
    Bar
  },
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
         // 响应式数据
     const videoElement = ref(null)
     const isStarting = ref(false)
     
     // 摄像头相关
     let stream = null
     let frameInterval = null
     let localFrameCount = 0
     let lastFrameTime = 0
     
     // 摄像头信息
     const videoResolution = ref('640x480')
     const frameRate = ref(30)
     const signalStrength = computed(() => signalQuality.value || 0)
    
    // 计算属性
    const isMonitoring = computed(() => store.state.monitoring.isMonitoring)
    const heartRate = computed(() => store.state.monitoring.heartRate)
    const bvpSignal = computed(() => store.state.monitoring.bvpSignal)
    const signalQuality = computed(() => store.state.monitoring.signalQuality)
    const frameCount = computed(() => store.state.monitoring.frameCount)
    const processingTime = computed(() => store.state.monitoring.processingTime)
    const maskedFrame = computed(() => store.state.monitoring.maskedFrame)
    const faceDetected = computed(() => store.state.monitoring.faceDetected)
    const monitoringDuration = computed(() => store.state.monitoring.monitoringDuration)
    
    const averageHeartRate = computed(() => store.getters['monitoring/averageHeartRate'])
    const maxHeartRate = computed(() => store.getters['monitoring/maxHeartRate'])
    const minHeartRate = computed(() => store.getters['monitoring/minHeartRate'])
    
    const connectionStatus = computed(() => store.state.system.connectionStatus)
    const systemHealth = computed(() => store.getters['system/systemHealth'])
    
    const systemHealthType = computed(() => {
      const health = systemHealth.value
      if (health === 'healthy') return 'success'
      if (health === 'overloaded') return 'warning'
      if (health === 'model_error') return 'danger'
      return 'info'
    })
    
    const systemHealthText = computed(() => {
      const health = systemHealth.value
      if (health === 'healthy') return '正常'
      if (health === 'overloaded') return '过载'
      if (health === 'model_error') return '模型错误'
      if (health === 'disconnected') return '未连接'
      return '未知'
    })
    
    // 图表数据
    const bvpChartData = computed(() => ({
      labels: bvpSignal.value.map((_, index) => (index * 0.01).toFixed(2)),
      datasets: [{
        label: 'BVP信号',
        data: bvpSignal.value,
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0
      }]
    }))
    
    const spectrumChartData = computed(() => {
      if (heartRate.value > 0) {
        const frequencies = Array.from({length: 50}, (_, i) => (i * 0.5).toFixed(1))
        const powerSpectrum = frequencies.map(f => {
          const hrFreq = heartRate.value / 60
          return Math.exp(-Math.pow(f - hrFreq, 2) / 0.1) + Math.random() * 0.1
        })
        
        return {
          labels: frequencies,
          datasets: [{
            label: '功率谱密度',
            data: powerSpectrum,
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderColor: '#667eea',
            borderWidth: 1
          }]
        }
      }
      return { labels: [], datasets: [{ data: [] }] }
    })
    
    // 图表配置
    const bvpChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          title: { display: true, text: '时间 (s)' },
          grid: { color: 'rgba(0,0,0,0.1)' }
        },
        y: {
          title: { display: true, text: '信号强度' },
          grid: { color: 'rgba(0,0,0,0.1)' }
        }
      },
      animation: { duration: 0 }
    }
    
    const spectrumChartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          title: { display: true, text: '频率 (Hz)' },
          grid: { color: 'rgba(0,0,0,0.1)' }
        },
        y: {
          title: { display: true, text: '功率' },
          grid: { color: 'rgba(0,0,0,0.1)' }
        }
      }
    }
    
    // 方法
    const startMonitoring = async () => {
      console.log('🚀 开始监测按钮被点击')
      
      if (isStarting.value || isMonitoring.value) {
        console.log('⚠️ 监测已在进行中或正在启动')
        return
      }
      
      try {
        isStarting.value = true
        console.log('📝 设置启动状态为true')
        
        // 1. 首先启动摄像头
        console.log('📹 启动摄像头...')
        await startCamera()
        console.log('✅ 摄像头启动成功')
        
        // 2. 创建会话
        console.log('🔗 创建会话...')
        const sessionId = await store.dispatch('session/createSession')
        console.log('✅ 创建会话成功:', sessionId)
        
        // 3. 连接WebSocket
        console.log('🌐 连接WebSocket...')
        wsManager.connect()
        
        // 4. 等待WebSocket连接成功
        const waitForConnection = () => {
          return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
              reject(new Error('WebSocket连接超时'))
            }, 10000) // 10秒超时
            
            if (wsManager.isConnected) {
               clearTimeout(timeout)
               resolve()
             } else {
               const onConnected = () => {
                 wsManager.off('connected', onConnected)
                 clearTimeout(timeout)
                 resolve()
               }
               wsManager.on('connected', onConnected)
             }
          })
        }
        
        await waitForConnection()
        console.log('✅ WebSocket连接成功')
        
        // 5. 加入会话
        console.log('🏠 加入会话:', sessionId)
        wsManager.joinSession(sessionId)
        
        // 6. 开始监测
        console.log('▶️ 开始监测...')
        store.dispatch('monitoring/startMonitoring')
        
        // 7. 开始帧捕获
        console.log('📸 开始帧捕获...')
        startFrameCapture(sessionId)
        
        console.log('🎉 监测启动完成')
        ElMessage.success('监测已开始')
        
      } catch (error) {
        console.error('❌ 启动监测失败:', error)
        ElMessage.error(`启动失败: ${error.message}`)
        
        // 清理资源
        stopCamera()
        store.dispatch('monitoring/stopMonitoring')
        
        // 如果会话已创建，尝试删除
        const sessionId = store.getters['session/currentSessionId']
        if (sessionId) {
          try {
            await store.dispatch('session/deleteSession', sessionId)
          } catch (deleteError) {
            console.error('删除会话失败:', deleteError)
          }
        }
      } finally {
        isStarting.value = false
      }
    }
    
    const stopMonitoring = async () => {
      try {
        // 停止摄像头
        stopCamera()
        
        // 停止监测
        store.dispatch('monitoring/stopMonitoring')
        
        // 删除会话
        const sessionId = store.getters['session/currentSessionId']
        if (sessionId) {
          await store.dispatch('session/deleteSession', sessionId)
          wsManager.leaveSession(sessionId)
        }
        
        ElMessage.success('监测已停止')
        
      } catch (error) {
        ElMessage.error(`停止失败: ${error.message}`)
        console.error('停止监测失败:', error)
      }
    }
    
    const startCamera = async () => {
      try {
        // 检查浏览器是否支持摄像头
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('您的浏览器不支持摄像头功能')
        }
        
        // 检查是否为HTTPS环境（localhost除外）
        const isSecureContext = window.isSecureContext || location.hostname === 'localhost' || location.hostname === '127.0.0.1'
        if (!isSecureContext) {
          throw new Error('摄像头访问需要HTTPS安全连接。请使用HTTPS协议访问，或者在本地环境（localhost）中使用。')
        }
        
        console.log('🔍 检查摄像头权限...')
        
        // 请求摄像头权限
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640, max: 1280 },
            height: { ideal: 480, max: 720 },
            facingMode: 'user',
            frameRate: { ideal: 30, max: 60 }
          }
        })
        
        console.log('📹 摄像头流获取成功')
        
        if (!videoElement.value) {
          throw new Error('视频元素未找到')
        }
        
        // 设置视频流
        videoElement.value.srcObject = stream
        
        // 等待视频加载并播放
        return new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            reject(new Error('视频加载超时'))
          }, 5000)
          
          videoElement.value.onloadedmetadata = () => {
            clearTimeout(timeout)
            videoElement.value.play()
              .then(() => {
                console.log('▶️ 视频播放成功')
                resolve()
              })
              .catch(reject)
          }
          
          videoElement.value.onerror = () => {
            clearTimeout(timeout)
            reject(new Error('视频加载失败'))
          }
        })
        
      } catch (error) {
        console.error('摄像头启动错误:', error)
        
        // 根据错误类型提供更友好的错误信息
        let errorMessage = '摄像头启动失败'
        
        if (error.name === 'NotAllowedError') {
          errorMessage = '摄像头权限被拒绝，请允许访问摄像头后重试'
        } else if (error.name === 'NotFoundError') {
          errorMessage = '未找到摄像头设备，请检查摄像头是否连接'
        } else if (error.name === 'NotReadableError') {
          errorMessage = '摄像头被其他应用占用，请关闭其他使用摄像头的应用'
        } else if (error.name === 'OverconstrainedError') {
          errorMessage = '摄像头不支持所需的分辨率或帧率'
        } else {
          errorMessage = error.message || '摄像头启动失败'
        }
        
        throw new Error(errorMessage)
      }
    }
    
    const stopCamera = () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
        stream = null
      }
      
      if (frameInterval) {
        clearInterval(frameInterval)
        frameInterval = null
      }
    }
    
         const startFrameCapture = (sessionId) => {
       const targetFPS = 10
       const interval = 1000 / targetFPS
       
       frameInterval = setInterval(async () => {
         if (isMonitoring.value && videoElement.value?.readyState === 4) {
           await captureAndSendFrame(sessionId)
         }
       }, interval)
     }
    
    const captureAndSendFrame = async (sessionId) => {
      try {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')
        
        canvas.width = videoElement.value.videoWidth
        canvas.height = videoElement.value.videoHeight
        
        ctx.drawImage(videoElement.value, 0, 0)
        const frameData = canvas.toDataURL('image/jpeg', 0.8)
        
                 // 通过WebSocket发送帧数据到后端
         wsManager.emit('frame_data', {
           session_id: sessionId,
           frame: frameData
         })
         
         localFrameCount++
         lastFrameTime = Date.now()
        
      } catch (error) {
        console.error('帧捕获错误:', error)
      }
    }
    
    // 生命周期
    onMounted(() => {
      // 设置WebSocket事件监听器
      wsManager.on('connected', () => {
        console.log('🌐 WebSocket已连接')
        store.dispatch('system/setConnectionStatus', 'connected')
      })
      
      wsManager.on('disconnected', () => {
        console.log('🌐 WebSocket已断开')
        store.dispatch('system/setConnectionStatus', 'disconnected')
      })
      
      // 页面加载时自动连接WebSocket
      console.log('🚀 页面加载，自动连接WebSocket...')
      wsManager.connect()
      
      // 监听rPPG结果更新事件
      wsManager.on('rppg_result', (data) => {
        console.log('收到rPPG结果:', data)
        store.dispatch('monitoring/updateRppgResult', data)
      })
      
      // 监听错误事件
      wsManager.on('error', (data) => {
        console.error('WebSocket错误:', data)
        ElMessage.error(data.message || '处理过程中发生错误')
      })
      
      // 监听会话加入事件
      wsManager.on('session_joined', (data) => {
        console.log('会话加入结果:', data)
        if (data.status === 'success') {
          console.log('成功加入会话:', data.session_id)
        } else {
          console.error('加入会话失败:', data.message)
        }
      })
      
      // 监听会话离开事件
      wsManager.on('session_left', (data) => {
        console.log('会话离开结果:', data)
      })
      
      // 检查系统状态
      checkSystemStatus()
      
      // 定期检查系统状态
      setInterval(checkSystemStatus, 5000)
    })
    
    onUnmounted(() => {
      stopCamera()
      wsManager.disconnect()
    })
    
    // 监听监测状态变化
    watch(isMonitoring, (newVal, oldVal) => {
      if (!newVal && oldVal) {
        stopCamera()
      }
    })
    
    // 定期检查系统状态
    const checkSystemStatus = async () => {
      try {
        // 检查WebSocket连接状态
        const wsConnected = wsManager.isConnected
        
        if (!wsConnected) {
          store.dispatch('system/setConnectionStatus', 'disconnected')
          store.dispatch('system/updateSystemStatus', {
            status: 'disconnected',
            timestamp: new Date().toISOString()
          })
          return
        }
        
        // 如果WebSocket连接正常，再检查后端健康状态
        const response = await api.healthCheck()
        if (response.status === 'healthy' || response.status === 'success') {
          store.dispatch('system/setConnectionStatus', 'connected')
          store.dispatch('system/updateSystemStatus', {
            status: 'healthy',
            device: response.device,
            timestamp: response.timestamp
          })
        } else {
          store.dispatch('system/updateSystemStatus', {
            status: 'model_error',
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('检查系统状态失败:', error)
        store.dispatch('system/setConnectionStatus', 'disconnected')
        store.dispatch('system/updateSystemStatus', {
          status: 'disconnected',
          timestamp: new Date().toISOString()
        })
      }
    }
    
         return {
       // 响应式引用
       videoElement,
       isStarting,
       
       // 计算属性
       isMonitoring,
       heartRate,
       bvpSignal,
       signalQuality,
       frameCount,
       processingTime,
       maskedFrame,
       faceDetected,
       monitoringDuration,
       averageHeartRate,
       maxHeartRate,
       minHeartRate,
       connectionStatus,
       systemHealth,
       systemHealthType,
       systemHealthText,
       
       // 摄像头信息
       videoResolution,
       frameRate,
       signalStrength,
       
       // 图表数据
       bvpChartData,
       spectrumChartData,
       bvpChartOptions,
       spectrumChartOptions,
       
       // 方法
       startMonitoring,
       stopMonitoring
     }
  }
}
</script>

<style lang="scss" scoped>
.monitoring-page {
  height: 100vh;
  background: #f5f7fa;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
    
    h1 {
      margin: 0;
      color: #303133;
      font-size: 24px;
    }
  }
}

.page-main {
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.camera-card, .status-card, .chart-card, .data-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.camera-container {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
}

.camera-video, .masked-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.face-detection-box {
  position: absolute;
  top: 20%;
  left: 20%;
  width: 60%;
  height: 60%;
  border: 3px solid #00ff88;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
}

.camera-info {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  
  .info-item {
    margin: 2px 0;
    
    .label {
      margin-right: 8px;
      opacity: 0.8;
    }
  }
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  
  .status-icon {
    font-size: 24px;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    
    &.heart-rate {
      background: linear-gradient(45deg, #ff6b6b, #ee5a24);
      color: white;
    }
    
    &.signal-quality {
      background: linear-gradient(45deg, #4ecdc4, #44a08d);
      color: white;
    }
    
    &.duration {
      background: linear-gradient(45deg, #45b7d1, #96c93d);
      color: white;
    }
  }
  
  .status-content {
    flex: 1;
    
    .status-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 5px;
    }
    
    .status-label {
      font-size: 12px;
      color: #909399;
    }
  }
}

.chart-container {
  height: 250px;
  position: relative;
  
  .chart {
    height: 100% !important;
  }
  
  .no-data {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.data-section {
  margin-top: 20px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 10px;
  
  .data-label {
    font-weight: 600;
    color: #606266;
  }
  
  .data-value {
    font-weight: bold;
    color: #303133;
  }
}

.mt-20 {
  margin-top: 20px;
}
</style>
