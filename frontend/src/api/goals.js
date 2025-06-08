import api from './index'

// 热量目标相关API
export const goalsAPI = {
  // 获取热量目标
  getCalorieGoal() {
    return api.get('/goals/daily-calorie/')
  },

  // 创建热量目标
  createCalorieGoal(goalData) {
    return api.post('/goals/daily-calorie/', goalData)
  },

  // 更新热量目标
  updateCalorieGoal(goalData) {
    return api.put('/goals/daily-calorie/', goalData)
  },

  // 删除热量目标
  deleteCalorieGoal() {
    return api.delete('/goals/daily-calorie/')
  }
}
