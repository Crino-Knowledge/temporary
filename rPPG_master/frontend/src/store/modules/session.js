import { api } from '@/api'

const state = {
  currentSession: null,
  sessionList: [],
  isLoading: false,
  error: null
}

const mutations = {
  SET_CURRENT_SESSION(state, session) {
    state.currentSession = session
  },
  SET_SESSION_LIST(state, sessions) {
    state.sessionList = sessions
  },
  SET_LOADING(state, loading) {
    state.isLoading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  }
}

const actions = {
  async createSession({ commit }) {
    commit('SET_LOADING', true)
    commit('CLEAR_ERROR')
    
    try {
      const response = await api.createSession()
      if (response.status === 'success') {
        commit('SET_CURRENT_SESSION', {
          id: response.session_id,
          status: 'active',
          createdAt: new Date()
        })
        return response.session_id
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async deleteSession({ commit, state }, sessionId) {
    commit('SET_LOADING', true)
    
    try {
      await api.deleteSession(sessionId)
      if (state.currentSession && state.currentSession.id === sessionId) {
        commit('SET_CURRENT_SESSION', null)
      }
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async getSessionStatus({ commit }, sessionId) {
    try {
      const response = await api.getSessionStatus(sessionId)
      if (response.status === 'success') {
        return response.data
      }
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    }
  },

  async listSessions({ commit }) {
    commit('SET_LOADING', true)
    
    try {
      const response = await api.listSessions()
      if (response.status === 'success') {
        commit('SET_SESSION_LIST', response.data.sessions)
      }
    } catch (error) {
      commit('SET_ERROR', error.message)
    } finally {
      commit('SET_LOADING', false)
    }
  },

  clearCurrentSession({ commit }) {
    commit('SET_CURRENT_SESSION', null)
  }
}

const getters = {
  hasActiveSession: state => !!state.currentSession,
  currentSessionId: state => state.currentSession?.id,
  sessionCount: state => state.sessionList.length
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
