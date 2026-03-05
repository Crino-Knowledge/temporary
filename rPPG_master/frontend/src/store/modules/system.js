const state = {
  systemStatus: 'unknown',
  connectionStatus: 'disconnected',
  modelStatus: 'unknown',
  queueSize: 0,
  maxQueueSize: 30,
  activeSessions: 0,
  lastUpdate: null
}

const mutations = {
  SET_SYSTEM_STATUS(state, status) {
    state.systemStatus = status
  },
  SET_CONNECTION_STATUS(state, status) {
    state.connectionStatus = status
  },
  SET_MODEL_STATUS(state, status) {
    state.modelStatus = status
  },
  SET_QUEUE_SIZE(state, size) {
    state.queueSize = size
  },
  SET_ACTIVE_SESSIONS(state, count) {
    state.activeSessions = count
  },
  SET_LAST_UPDATE(state, timestamp) {
    state.lastUpdate = timestamp
  }
}

const actions = {
  async getSystemStatus({ commit }) {
    try {
      // 调用健康检查API
      const { api } = await import('@/api')
      const response = await api.healthCheck()
      
      if (response.status === 'healthy') {
        commit('SET_SYSTEM_STATUS', 'normal')
        commit('SET_CONNECTION_STATUS', 'connected')
        commit('SET_MODEL_STATUS', 'loaded')
        commit('SET_LAST_UPDATE', Date.now())
        
        return {
          status: 'success',
          data: response
        }
      } else {
        commit('SET_SYSTEM_STATUS', 'error')
        commit('SET_CONNECTION_STATUS', 'disconnected')
        return {
          status: 'error',
          message: 'System unhealthy'
        }
      }
    } catch (error) {
      console.error('获取系统状态失败:', error)
      commit('SET_SYSTEM_STATUS', 'error')
      commit('SET_CONNECTION_STATUS', 'disconnected')
      commit('SET_MODEL_STATUS', 'unknown')
      return {
        status: 'error',
        message: error.message
      }
    }
  },

  updateSystemStatus({ commit }, data) {
    commit('SET_QUEUE_SIZE', data.queue_size || 0)
    commit('SET_ACTIVE_SESSIONS', data.active_sessions || 0)
    commit('SET_LAST_UPDATE', Date.now())
    
    // 根据队列大小判断系统状态
    const queueRatio = data.queue_size / state.maxQueueSize
    if (queueRatio > 0.8) {
      commit('SET_SYSTEM_STATUS', 'busy')
    } else if (queueRatio > 0.5) {
      commit('SET_SYSTEM_STATUS', 'moderate')
    } else {
      commit('SET_SYSTEM_STATUS', 'normal')
    }
  },

  setConnectionStatus({ commit }, status) {
    commit('SET_CONNECTION_STATUS', status)
  },

  setModelStatus({ commit }, status) {
    commit('SET_MODEL_STATUS', status)
  }
}

const getters = {
  isConnected: state => state.connectionStatus === 'connected',
  isModelLoaded: state => state.modelStatus === 'loaded',
  systemHealth: state => {
    if (state.connectionStatus === 'disconnected') return 'disconnected'
    if (state.modelStatus !== 'loaded') return 'model_error'
    if (state.systemStatus === 'busy') return 'overloaded'
    return 'healthy'
  },
  
  queueUtilization: state => {
    return Math.round((state.queueSize / state.maxQueueSize) * 100)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
