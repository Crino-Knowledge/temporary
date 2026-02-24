import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
//导入登录页面组件
import Login from '@/views/login.vue'
import Home from '@/views/home.vue'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Default',
      redirect: '/home',
      component: Home
    },
    {
       // home页面并不需要被访问，只是作为其它组件的父组件
      path: '/home',
      name: 'Home',
      component: Home,
      meta: {
        requireAuth: true
      },
      redirect: '/index',
      children:[
        {
          path:'/index',
          name:'Index',
          component:() => import('@/views/home/index'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/user',
          name:'User',
          component:()=>import('@/views/user/index'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/algorithmModel',
          name:'algorithmModel',
          component:()=>import('@/views/algorithmModel/algorithmModel'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/task',
          name:'task',
          component:()=>import('@/views/task/algorithmTask'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/alarmCenter',
          name:'alarmCenter',
          component:()=>import('@/views/alarmCenter/alarmData'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/pushLog',
          name:'pushLog',
          component:()=>import('@/views/pushLog/httpPushLog'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/customer',
          name:'customer',
          component:()=>import('@/views/customer/index'),
          meta:{
            requireAuth:true
          }
        },
        {
          path:'/dict',
          name:'dict',
          component:()=>import('@/views/dict/index'),
          meta:{
            requireAuth:true
          }
        }
      ]
    },
    //添加登录页面路由
    {
      path:'/login',
      name: 'Login',
      component: Login
    }
  ]
})
