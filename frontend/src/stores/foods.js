import { defineStore } from 'pinia'
import { foodsAPI } from '@/api/foods'
import { ElMessage } from 'element-plus'

export const useFoodsStore = defineStore('foods', {
  state: () => ({
    foods: [],
    currentFood: null,
    foodStats: null,
    loading: false,
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    foodsList: (state) => state.foods,
    totalFoods: (state) => state.pagination.total,
    breakfastFoods: (state) => state.foods.filter(food => food.is_for_breakfast),
    lunchFoods: (state) => state.foods.filter(food => food.is_for_lunch),
    dinnerFoods: (state) => state.foods.filter(food => food.is_for_dinner)
  },

  actions: {
    // 获取食物列表
    async fetchFoods(params = {}) {
      this.loading = true
      try {
        const response = await foodsAPI.getFoods(params)
        this.foods = response.data.results || response.data
        if (response.data.count !== undefined) {
          this.pagination.total = response.data.count
        }
      } catch (error) {
        ElMessage.error('获取食物列表失败')
        console.error('Fetch foods error:', error)
      } finally {
        this.loading = false
      }
    },

    // 创建食物
    async createFood(foodData) {
      this.loading = true
      try {
        const response = await foodsAPI.createFood(foodData)
        this.foods.unshift(response.data)
        ElMessage.success('食物创建成功！')
        return true
      } catch (error) {
        const message = error.response?.data?.name?.[0] || '创建食物失败'
        ElMessage.error(message)
        return false
      } finally {
        this.loading = false
      }
    },

    // 更新食物
    async updateFood(foodId, foodData) {
      this.loading = true
      try {
        const response = await foodsAPI.updateFood(foodId, foodData)
        const index = this.foods.findIndex(food => food.food_id === foodId)
        if (index !== -1) {
          this.foods[index] = response.data
        }
        ElMessage.success('食物更新成功！')
        return true
      } catch (error) {
        ElMessage.error('更新食物失败')
        return false
      } finally {
        this.loading = false
      }
    },

    // 删除食物
    async deleteFood(foodId) {
      this.loading = true
      try {
        await foodsAPI.deleteFood(foodId)
        this.foods = this.foods.filter(food => food.food_id !== foodId)
        ElMessage.success('食物删除成功！')
        return true
      } catch (error) {
        ElMessage.error('删除食物失败')
        return false
      } finally {
        this.loading = false
      }
    },

    // 获取食物推荐
    async getSuggestedFood(mealType) {
      try {
        const response = await foodsAPI.getSuggestedFood(mealType)
        return response.data
      } catch (error) {
        const message = error.response?.data?.error || '获取推荐失败'
        ElMessage.error(message)
        return null
      }
    },

    // 获取食物统计
    async fetchFoodStats() {
      try {
        const response = await foodsAPI.getFoodStats()
        this.foodStats = response.data
      } catch (error) {
        ElMessage.error('获取食物统计失败')
        console.error('Fetch food stats error:', error)
      }
    },

    // 设置当前食物
    setCurrentFood(food) {
      this.currentFood = food
    },

    // 清空当前食物
    clearCurrentFood() {
      this.currentFood = null
    }
  }
})
