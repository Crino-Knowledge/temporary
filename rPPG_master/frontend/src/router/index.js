import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Monitoring from '@/views/Monitoring.vue'
import History from '@/views/History.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: Monitoring,
    meta: { title: '实时监测' }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { title: '历史记录' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { title: '系统设置' }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `rPPG - ${to.meta.title}`
  next()
})

export default router
