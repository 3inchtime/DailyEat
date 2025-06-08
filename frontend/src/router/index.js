import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/FoodWheelView.vue')
        },
        {
          path: 'foods',
          name: 'foods',
          component: () => import('../views/FoodsView.vue')
        },
        {
          path: 'meal-logs',
          name: 'mealLogs',
          component: () => import('../views/MealLogsView.vue')
        },
        {
          path: 'stats',
          name: 'stats',
          component: () => import('../views/StatsView.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue')
        }
      ]
    }
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('access_token')

  console.log('路由守卫检查:', {
    to: to.path,
    from: from.path,
    isAuthenticated: authStore.isAuthenticated,
    requiresAuth: to.meta.requiresAuth,
    requiresGuest: to.meta.requiresGuest,
    hasToken: !!token
  })

  // 如果有token但未认证，先尝试初始化认证状态
  if (token && !authStore.isAuthenticated) {
    try {
      console.log('发现token但未认证，尝试初始化认证状态')
      await authStore.initAuth()
      console.log('认证状态初始化结果:', authStore.isAuthenticated)
    } catch (error) {
      console.error('认证状态初始化失败:', error)
      // 清除无效token
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      authStore.isAuthenticated = false
    }
  }

  // 如果是登录页面且已经认证，直接跳转到首页
  if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('已登录用户访问登录页，跳转到首页')
    next('/')
    return
  }

  // 如果是注册页面且已经认证，直接跳转到首页
  if (to.path === '/register' && authStore.isAuthenticated) {
    console.log('已登录用户访问注册页，跳转到首页')
    next('/')
    return
  }

  // 如果需要认证的页面但未认证，跳转到登录页
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('需要认证但未登录，跳转到登录页')
    next('/login')
    return
  }

  console.log('路由检查通过，继续导航到:', to.path)
  next()
})

export default router
