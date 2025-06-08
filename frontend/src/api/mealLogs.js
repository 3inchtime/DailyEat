import api from './index'

// 用餐记录相关API
export const mealLogsAPI = {
  // 获取用餐记录列表
  getMealLogs(params = {}) {
    return api.get('/meal-logs/', { params })
  },

  // 创建用餐记录
  createMealLog(logData) {
    return api.post('/meal-logs/', logData)
  },

  // 获取用餐记录详情
  getMealLogDetail(logId) {
    return api.get(`/meal-logs/${logId}/`)
  },

  // 更新用餐记录
  updateMealLog(logId, logData) {
    return api.put(`/meal-logs/${logId}/`, logData)
  },

  // 部分更新用餐记录
  patchMealLog(logId, logData) {
    return api.patch(`/meal-logs/${logId}/`, logData)
  },

  // 删除用餐记录
  deleteMealLog(logId) {
    return api.delete(`/meal-logs/${logId}/`)
  },

  // 获取最近用餐记录
  getRecentMealLogs(limit = 10) {
    return api.get('/meal-logs/recent/', { params: { limit } })
  }
}
