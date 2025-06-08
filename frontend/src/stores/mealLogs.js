import { defineStore } from 'pinia'
import { mealLogsAPI } from '@/api/mealLogs'
import { ElMessage } from 'element-plus'

export const useMealLogsStore = defineStore('mealLogs', {
  state: () => ({
    mealLogs: [],
    currentMealLog: null,
    loading: false,
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    allMealLogs: (state) => state.mealLogs,
    todayMealLogs: (state) => {
      const today = new Date().toDateString()
      return state.mealLogs.filter(log => 
        new Date(log.eaten_at_datetime).toDateString() === today
      )
    },
    todayCalories: (state) => {
      const today = new Date().toDateString()
      return state.mealLogs
        .filter(log => new Date(log.eaten_at_datetime).toDateString() === today)
        .reduce((total, log) => total + (log.food_detail?.calories || 0), 0)
    }
  },

  actions: {
    // 获取用餐记录列表
    async fetchMealLogs(params = {}) {
      this.loading = true
      try {
        const response = await mealLogsAPI.getMealLogs(params)
        this.mealLogs = response.data.results || response.data
        if (response.data.count !== undefined) {
          this.pagination.total = response.data.count
        }
        return this.mealLogs
      } catch (error) {
        console.error('获取用餐记录失败:', error)
        ElMessage.error('获取用餐记录失败')
        return []
      } finally {
        this.loading = false
      }
    },

    // 获取单条用餐记录详情
    async fetchMealLogDetail(logId) {
      this.loading = true
      try {
        const response = await mealLogsAPI.getMealLogDetail(logId)
        this.currentMealLog = response.data
        return response.data
      } catch (error) {
        console.error('获取用餐记录详情失败:', error)
        ElMessage.error('获取用餐记录详情失败')
        return null
      } finally {
        this.loading = false
      }
    },

    // 添加用餐记录
    async createMealLog(mealLogData) {
      this.loading = true
      try {
        const response = await mealLogsAPI.createMealLog(mealLogData)
        ElMessage.success('成功添加到用餐记录！')
        // 更新本地数据
        await this.fetchMealLogs()
        return response.data
      } catch (error) {
        console.error('添加用餐记录失败:', error)
        ElMessage.error('添加用餐记录失败')
        return null
      } finally {
        this.loading = false
      }
    },

    // 更新用餐记录
    async updateMealLog(logId, mealLogData) {
      this.loading = true
      try {
        const response = await mealLogsAPI.updateMealLog(logId, mealLogData)
        ElMessage.success('成功更新用餐记录！')
        // 更新本地数据
        await this.fetchMealLogs()
        return response.data
      } catch (error) {
        console.error('更新用餐记录失败:', error)
        ElMessage.error('更新用餐记录失败')
        return null
      } finally {
        this.loading = false
      }
    },

    // 删除用餐记录
    async deleteMealLog(logId) {
      this.loading = true
      try {
        await mealLogsAPI.deleteMealLog(logId)
        ElMessage.success('成功删除用餐记录！')
        // 更新本地数据
        await this.fetchMealLogs()
        return true
      } catch (error) {
        console.error('删除用餐记录失败:', error)
        ElMessage.error('删除用餐记录失败')
        return false
      } finally {
        this.loading = false
      }
    }
  }
}) 