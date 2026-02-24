import request from '@/utils/request'

// 查询字典列表
export function getDictList(data) {
  return request({
    url: 'sys/dataDict/getDataDictListPageVo',
    method: 'post',
    data: data
  })
}
// 查询所有字典
export function getAllDict() {
    return request({
      url: 'sys/dataDict/getDataDict',
      method: 'get',
    })
  }
// 通过id获取数据字典树形列表
export function getDictById(id) {
    return request({
      url: 'sys/dataDict/getDataDictTreeById/' + id,
      method: 'get',
    })
}
// 添加数据字典
export function addDict(data) {
  return request({
    url: 'sys/dataDict/addDataDict',
    method: 'post',
    data: data
  })
}
// 修改数据字典
export function updateDict(data) {
  return request({
    url: 'sys/dataDict/updateDataDict',
    method: 'post',
    data: data
  })
}
// 删除数据字典
export function delDict(id) {
  return request({
    url: 'sys/dataDict/deleteDataDictById/' + id,
    method: 'get'
  })
}
