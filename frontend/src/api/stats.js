import api from './index'

// 统计相关API
export const statsAPI = {
  // 获取每日热量统计
  getDailyCaloriesStats(date) {
    return api.get('/stats/daily-calories/', { params: { date } })
  },

  // 获取周统计
  getWeeklyStats(date = null) {
    const params = date ? { date } : {}
    return api.get('/stats/weekly/', { params })
  }
}
