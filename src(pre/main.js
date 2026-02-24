// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
//引入ElementUI
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import "@/assets/styles/base.css"; //flex css
import "@/assets/styles/common.css"; 
import store from './store'
import '@/utils/rem'
import {
  getAllDict
} from "@/api/jsDict";
import {

  resetForm,

} from '@/utils/ruoyi'
var axios = require('axios')
// 全局注册，之后可在其他组件中通过 this.$axios 发送数据
Vue.prototype.$axios = axios
// 设置反向代理，前端请求默认发送到 http://localhost:8888/api
// axios.defaults.baseURL = 'http://localhost:8088/api'
Vue.config.productionTip = false
Vue.prototype.resetForm = resetForm
/* eslint-disable no-new */

Vue.use(ElementUI)
// getAllDict().then((res) => {

// });
//钩子函数，访问路由前调用
router.beforeEach((to, from, next) => {
  //路由需要认证
  if (to.meta.requireAuth) {
    //判断store里是否有token
    if (store.state.token) {
      next()
    } else {
      next({
        path: 'login',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    next()
  }
}
)


new Vue({
  el: '#app',
  router,
  // 注意这里
  store,
  components: { App },
  template: '<App/>'
})
