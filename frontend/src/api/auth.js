import api from './index'

// 用户认证相关API
export const authAPI = {
  // 用户注册
  register(userData) {
    return api.post('/auth/register/', userData)
  },

  // 用户登录
  login(credentials) {
    return api.post('/auth/login/', credentials)
  },

  // 刷新token
  refreshToken(refreshToken) {
    return api.post('/auth/token/refresh/', { refresh: refreshToken })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/auth/me/')
  }
}
