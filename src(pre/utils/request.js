import axios from 'axios'
import store from '@/store'
import { Notification, MessageBox, Message, Loading } from 'element-ui'

//const baseURL="localhost:8088/api"

//创建axios实例
const service = axios.create({
  baseURL: `${process.env.BASE_API?process.env.BASE_API:'/api'}`, // api的base_url
})
// request 请求拦截
service.interceptors.request.use(
  config => {

    if (store.state.token) {
      config.headers['token'] = window.sessionStorage.getItem("token")
    }
    return config
  },
  error => {
    // do something with request error
    console.log(error) // for debug
    return Promise.reject(error)
  }
)

//response响应拦截
service.interceptors.response.use(response => {
    let res = response.data;
    

    if (res.code === 200) {
      return response
    } else {
      Message({ message: response.data.msg, type: 'error' })
      return Promise.reject(response.data.msg)
    }
  },
  error => {
    console.log(error)
    if (error.response.data) {
      error.msg = error.response.data.msg
    }

    if (error.response.status === 401) {
      router.push("/sys/auth/login")
    }
    Message({ message: error.msg, type: 'error' })
    return Promise.reject(error.msg)
  }
)


export default service
