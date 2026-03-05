const state = {
  isMonitoring: false,
  heartRate: 0,
  bvpSignal: [],
  signalQuality: 0,
  frameCount: 0,
  processingTime: 0,
  maskedFrame: null,
  faceDetected: false,
  monitoringStartTime: null,
  heartRateHistory: [],
  bvpHistory: [],
  error: null
}

const mutations = {
  SET_MONITORING(state, status) {
    state.isMonitoring = status
  },
  SET_HEART_RATE(state, rate) {
    state.heartRate = rate
    if (rate > 0) {
      state.heartRateHistory.push({
        time: Date.now(),
        value: rate
      })
      // 保持最近100个数据点
      if (state.heartRateHistory.length > 100) {
        state.heartRateHistory.shift()
      }
    }
  },
  SET_BVP_SIGNAL(state, signal) {
    state.bvpSignal = signal
    if (signal.length > 0) {
      state.bvpHistory.push({
        time: Date.now(),
        data: [...signal]
      })
      // 保持最近50个数据点
      if (state.bvpHistory.length > 50) {
        state.bvpHistory.shift()
      }
    }
  },
  SET_SIGNAL_QUALITY(state, quality) {
    state.signalQuality = quality
  },
  SET_FRAME_COUNT(state, count) {
    state.frameCount = count
  },
  SET_PROCESSING_TIME(state, time) {
    state.processingTime = time
  },
  SET_MASKED_FRAME(state, frame) {
    state.maskedFrame = frame
  },
  SET_FACE_DETECTED(state, detected) {
    state.faceDetected = detected
  },
  SET_MONITORING_START_TIME(state, time) {
    state.monitoringStartTime = time
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  },
  CLEAR_DATA(state) {
    state.heartRate = 0
    state.bvpSignal = []
    state.signalQuality = 0
    state.frameCount = 0
    state.processingTime = 0
    state.maskedFrame = null
    state.faceDetected = false
    state.heartRateHistory = []
    state.bvpHistory = []
  },
  RESET_MONITORING(state) {
    state.isMonitoring = false
    state.monitoringStartTime = null
    // 调用CLEAR_DATA的mutations
    state.heartRate = 0
    state.bvpSignal = []
    state.signalQuality = 0
    state.frameCount = 0
    state.processingTime = 0
    state.maskedFrame = null
    state.faceDetected = false
    state.heartRateHistory = []
    state.bvpHistory = []
  }
}

const actions = {
  startMonitoring({ commit }) {
    commit('SET_MONITORING', true)
    commit('SET_MONITORING_START_TIME', Date.now())
    commit('CLEAR_ERROR')
  },

  stopMonitoring({ commit }) {
    commit('SET_MONITORING', false)
    commit('RESET_MONITORING')
  },

  updateFrameData({ commit, state }, data) {
    // 处理heart_rate_update事件（来自后端的实时心率数据）
    if (data.heart_rate !== undefined) {
      commit('SET_FACE_DETECTED', true) // 有心率数据说明检测到人脸
      commit('SET_HEART_RATE', data.heart_rate || 0)
      commit('SET_BVP_SIGNAL', data.bvp_signal || [])
      commit('SET_SIGNAL_QUALITY', data.signal_quality || 0)
      // 增加帧计数
      commit('SET_FRAME_COUNT', (state.frameCount || 0) + 1)
      if (data.processing_time) {
        commit('SET_PROCESSING_TIME', data.processing_time)
      }
      if (data.masked_frame) {
        commit('SET_MASKED_FRAME', data.masked_frame)
      }
    }
    // 处理frame_processed事件（原有逻辑）
    else if (data.face_detected !== undefined) {
      if (data.face_detected) {
        commit('SET_FACE_DETECTED', true)
        commit('SET_HEART_RATE', data.heart_rate || 0)
        commit('SET_BVP_SIGNAL', data.bvp_signal || [])
        commit('SET_SIGNAL_QUALITY', data.signal_quality || 0)
        commit('SET_FRAME_COUNT', data.frame_count || 0)
        commit('SET_PROCESSING_TIME', data.processing_time || 0)
        if (data.masked_frame) {
          commit('SET_MASKED_FRAME', data.masked_frame)
        }
      } else {
        commit('SET_FACE_DETECTED', false)
        if (data.clear_data) {
          commit('CLEAR_DATA')
        }
      }
    }
  },

  clearData({ commit }) {
    commit('CLEAR_DATA')
  },

  updateRppgResult({ commit, state }, data) {
    // 处理后端发送的rPPG结果
    console.log('更新rPPG结果:', data)
    
    // 如果是清空数据的信号
    if (data.clear_data) {
      commit('SET_HEART_RATE', 0)
      commit('SET_SIGNAL_QUALITY', 0)
      commit('SET_FACE_DETECTED', false)
      commit('SET_BVP_SIGNAL', [])
      return
    }
    
    if (data.heartrate !== undefined) {
      commit('SET_HEART_RATE', data.heartrate)
    }
    
    if (data.bvp && Array.isArray(data.bvp)) {
      commit('SET_BVP_SIGNAL', data.bvp)
    }
    
    if (data.frame_count !== undefined) {
      commit('SET_FRAME_COUNT', data.frame_count)
    }
    
    // 使用后端计算的信号质量
    if (data.signal_quality !== undefined) {
      commit('SET_SIGNAL_QUALITY', data.signal_quality)
    }
    
    // 如果有心率数据，说明检测到了人脸
    if (data.heartrate > 0) {
      commit('SET_FACE_DETECTED', true)
    } else {
      commit('SET_FACE_DETECTED', false)
    }
    
    // 模拟处理时间
    commit('SET_PROCESSING_TIME', Math.random() * 50 + 20)
  },
  
  // 当没有检测到人脸时清空数据
  clearCurrentData({ commit }) {
    commit('SET_HEART_RATE', 0)
    commit('SET_SIGNAL_QUALITY', 0)
    commit('SET_FACE_DETECTED', false)
    commit('SET_BVP_SIGNAL', [])
  }
}

const getters = {
  monitoringDuration: state => {
    if (!state.monitoringStartTime) return 0
    return Math.floor((Date.now() - state.monitoringStartTime) / 1000)
  },
  
  averageHeartRate: state => {
    if (state.heartRateHistory.length === 0) return 0
    const sum = state.heartRateHistory.reduce((acc, item) => acc + item.value, 0)
    return Math.round(sum / state.heartRateHistory.length)
  },
  
  maxHeartRate: state => {
    if (state.heartRateHistory.length === 0) return 0
    return Math.max(...state.heartRateHistory.map(item => item.value))
  },
  
  minHeartRate: state => {
    if (state.heartRateHistory.length === 0) return 0
    return Math.min(...state.heartRateHistory.map(item => item.value))
  },
  
  hasValidData: state => {
    return state.faceDetected && state.heartRate > 0
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
