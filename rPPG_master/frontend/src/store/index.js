import { createStore } from 'vuex'
import monitoring from './modules/monitoring'
import session from './modules/session'
import system from './modules/system'

export default createStore({
  modules: {
    monitoring,
    session,
    system
  },
  state: {
    appName: 'rPPG实时心率监测系统',
    version: '2.0.0'
  },
  getters: {
    appInfo: state => ({
      name: state.appName,
      version: state.version
    })
  }
})
