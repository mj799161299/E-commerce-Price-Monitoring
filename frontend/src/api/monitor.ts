import request from '@/utils/request'

// 获取监控商品列表
export const getMonitorItems = () => {
  return request.get('/monitor/items')
}

// 添加监控商品
export const addMonitorItem = (data: any) => {
  return request.post('/monitor/items', data)
}

// 更新监控商品
export const updateMonitorItem = (id: number, data: any) => {
  return request.put(`/monitor/items/${id}`, data)
}

// 删除监控商品
export const deleteMonitorItem = (id: number) => {
  return request.delete(`/monitor/items/${id}`)
}

// 获取商品历史价格
export const getPriceHistory = (id: number) => {
  return request.get(`/monitor/items/${id}/history`)
}
