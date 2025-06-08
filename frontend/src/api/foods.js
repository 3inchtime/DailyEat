import api from './index'

// 食物管理相关API
export const foodsAPI = {
  // 获取食物列表
  getFoods(params = {}) {
    return api.get('/foods/', { params })
  },

  // 创建食物
  createFood(foodData) {
    return api.post('/foods/', foodData)
  },

  // 获取食物详情
  getFoodDetail(foodId) {
    return api.get(`/foods/${foodId}/`)
  },

  // 更新食物
  updateFood(foodId, foodData) {
    return api.put(`/foods/${foodId}/`, foodData)
  },

  // 部分更新食物
  patchFood(foodId, foodData) {
    return api.patch(`/foods/${foodId}/`, foodData)
  },

  // 删除食物
  deleteFood(foodId) {
    return api.delete(`/foods/${foodId}/`)
  },

  // 获取食物推荐
  getSuggestedFood(mealType) {
    return api.get('/foods/suggest/', { params: { meal_type: mealType } })
  },

  // 获取食物库统计
  getFoodStats() {
    return api.get('/foods/stats/')
  }
}
