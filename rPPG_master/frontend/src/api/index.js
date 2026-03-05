import axios from 'axios'
import { io } from 'socket.io-client'

// 创建axios实例
const http = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? '/api' : (process.env.VUE_APP_API_BASE_URL || '/api'),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    // 可以在这里添加认证token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API请求错误:', error)
    // 返回统一的错误格式
    return {
      status: 'error',
      message: error.response?.data?.message || error.message || '网络请求失败'
    }
  }
)

// API接口
export const api = {
  // 健康检查
  healthCheck: () => http.get('/health'),
  
  // 会话管理
  createSession: () => http.post('/sessions'),
  deleteSession: (sessionId) => http.delete(`/sessions/${sessionId}`),
  getSessionStatus: (sessionId) => http.get(`/sessions/${sessionId}`),
  listSessions: () => http.get('/sessions'),
  
  // 帧数据上传
  uploadFrame: (sessionId, frameData) => http.post(`/sessions/${sessionId}/frames`, { frame: frameData }),
  
  // 获取会话结果
  getSessionResults: (sessionId, count = 50) => http.get(`/sessions/${sessionId}/results?count=${count}`),
  
  // 重置会话
  resetSession: (sessionId) => http.post(`/sessions/${sessionId}/reset`),
  
  // 系统状态
  getSystemStatus: () => http.get('/system/status')
}

// WebSocket连接管理
class WebSocketManager {
  constructor() {
    this.socket = null
    this._isConnected = false
    this.eventHandlers = new Map()
  }

  connect() {
    if (this.socket && this.isConnected) {
      return this.socket
    }

    const wsUrl = process.env.VUE_APP_WS_URL || (process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5000')
    this.socket = io(wsUrl, {
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true
    })

    this.socket.on('connect', () => {
      this._isConnected = true
      console.log('WebSocket连接成功')
      
      // 重新注册所有事件监听器
      this.eventHandlers.forEach((handlers, event) => {
        handlers.forEach(handler => {
          this.socket.on(event, handler)
        })
      })
      
      this.emit('connected')
    })

    this.socket.on('disconnect', () => {
      this._isConnected = false
      console.log('WebSocket连接断开')
      this.emit('disconnected')
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket连接错误:', error)
      this.emit('error', error)
    })

    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this._isConnected = false
    }
  }

  joinSession(sessionId) {
    if (this.socket && this._isConnected) {
      this.socket.emit('join_session', { session_id: sessionId })
    }
  }

  leaveSession(sessionId) {
    if (this.socket && this._isConnected) {
      this.socket.emit('leave_session', { session_id: sessionId })
    }
  }
  
  get isConnected() {
    return this._isConnected
  }

  on(event, handler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, [])
    }
    this.eventHandlers.get(event).push(handler)
    
    // 如果已经连接，立即注册事件监听器
    if (this.socket && this._isConnected) {
      this.socket.on(event, handler)
    }
  }

  off(event, handler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
    
    if (this.socket) {
      this.socket.off(event, handler)
    }
  }

  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data)
    }
  }

  getConnectionStatus() {
    return this._isConnected
  }
}

export const wsManager = new WebSocketManager()

export default {
  api,
  wsManager
}
