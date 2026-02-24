import request from '@/utils/request'

//**HTTP推送日志**


//删除
export function deleteById(id) {
  return request({
    url: 'sys/httpPushLog/deleteHttpPushLogById/' + id,
    method: 'get'
  })
}


//详情
export function getById(id) {
  return request({
    url: 'sys/httpPushLog/getHttpPushLogById/' + id,
    method: 'get'
  })
}

//列表
export function listPage(data) {
  return request({
    url: 'sys/httpPushLog/getHttpPushLogListPageVo',
    method: 'post',
    data
  })
}


//手动重新推送
export function againPushLog(data) {
  return request({
    url: 'sys/httpPushLog/againPushLog',
    method: 'post',
    data
  })
}
