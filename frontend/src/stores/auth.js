import { defineStore } from 'pinia'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.user,
    userName: (state) => state.user?.username || '',
    userEmail: (state) => state.user?.email || ''
  },

  actions: {
    // 初始化认证状态
    async initAuth() {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          await this.getCurrentUser()
          console.log('认证状态初始化成功')
        } catch (error) {
          console.error('认证状态初始化失败:', error)
          this.logout()
          throw error // 重新抛出错误，让调用者知道初始化失败
        }
      }
    },

    // 用户登录
    async login(credentials) {
      this.loading = true
      try {
        console.log('开始登录请求...')
        const response = await authAPI.login(credentials)
        const { access, refresh } = response.data

        console.log('登录API成功，保存tokens...')
        // 保存tokens
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)

        // 获取用户信息
        try {
          console.log('获取用户信息...')
          await this.getCurrentUserForLogin() // 使用专门的登录版本
          console.log('登录流程完成，认证状态:', this.isAuthenticated)
          ElMessage.success('登录成功！')
          return true
        } catch (userError) {
          console.error('获取用户信息失败:', userError)
          // 登录时如果获取用户信息失败，先设置基本认证状态
          this.isAuthenticated = true
          this.user = { username: credentials.username } // 临时用户信息
          console.log('设置临时认证状态，稍后重试获取用户信息')
          ElMessage.success('登录成功！')
          return true
        }
      } catch (error) {
        console.error('登录失败:', error)
        const message = error.response?.data?.detail || '登录失败，请检查用户名和密码'
        ElMessage.error(message)
        return false
      } finally {
        this.loading = false
      }
    },

    // 用户注册
    async register(userData) {
      this.loading = true
      try {
        await authAPI.register(userData)
        ElMessage.success('注册成功！请登录')
        return true
      } catch (error) {
        const message = error.response?.data?.username?.[0] || 
                       error.response?.data?.email?.[0] || 
                       '注册失败，请检查输入信息'
        ElMessage.error(message)
        return false
      } finally {
        this.loading = false
      }
    },

    // 获取当前用户信息
    async getCurrentUser() {
      try {
        const response = await authAPI.getCurrentUser()
        this.user = response.data
        this.isAuthenticated = true
        console.log('用户信息获取成功:', this.user)
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        throw error
      }
    },

    // 专门用于登录时获取用户信息（不会在失败时清除认证状态）
    async getCurrentUserForLogin() {
      try {
        const response = await authAPI.getCurrentUser()
        this.user = response.data
        this.isAuthenticated = true
        console.log('登录时用户信息获取成功:', this.user)
      } catch (error) {
        console.error('登录时获取用户信息失败:', error)
        // 登录时不清除认证状态，让路由守卫处理
        throw error
      }
    },

    // 用户登出
    logout() {
      this.user = null
      this.isAuthenticated = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      ElMessage.info('已退出登录')
    }
  }
})
