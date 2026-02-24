import request from '@/utils/request'

export function userLogin(data) {
  return request({
    url: '/sys/auth/login',
    method: 'post',
    data
  })
}

//获取用户列表
export function userList(data) {
  return request({
    //url: '/user/list',
    url: '/sys/user/getUserListPageVo',
    method: 'post',
    data
  })
}

//添加用户
export function userAdd(data) {
  return request({
    url: '/sys/user/addUser',
    method: 'post',
    data
  })
}

//修改用户
export function userUpdate(data) {
  return request({
    url: '/sys/user/updateUser',
    method: 'post',
    data
  })
}

//删除用户
export function userDelete(id) {
  return request({
    url: '/sys/user/deleteUserById',
    method: 'post',
    params: {
      id
    }
  })
}

//批量删除用户
export function userBatchDelete(data) {
  return request({
    url: '/user/delete/batch',
    method: 'post',
    data
  })
}
