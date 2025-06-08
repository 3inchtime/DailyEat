<template>
  <div class="simple-dashboard">
    <h1>🏠 简化版首页</h1>
    <p>用于测试页面是否能正常显示</p>
    
    <div class="info-section">
      <h2>认证信息</h2>
      <p><strong>用户名:</strong> {{ authStore.userName || '未获取' }}</p>
      <p><strong>认证状态:</strong> {{ authStore.isAuthenticated ? '✅ 已认证' : '❌ 未认证' }}</p>
      <p><strong>用户对象:</strong> {{ JSON.stringify(authStore.user) }}</p>
    </div>
    
    <div class="token-section">
      <h2>Token信息</h2>
      <p><strong>Access Token:</strong> {{ accessToken ? accessToken.substring(0, 50) + '...' : '无' }}</p>
      <p><strong>Refresh Token:</strong> {{ refreshToken ? refreshToken.substring(0, 50) + '...' : '无' }}</p>
    </div>
    
    <div class="test-section">
      <h2>功能测试</h2>
      <el-button @click="testUserAPI" type="primary">测试用户API</el-button>
      <el-button @click="testStatsAPI" type="success">测试统计API</el-button>
      <el-button @click="logout" type="danger">退出登录</el-button>
    </div>
    
    <div class="result-section" v-if="testResult">
      <h2>测试结果</h2>
      <pre>{{ testResult }}</pre>
    </div>
    
    <div class="navigation-section">
      <h2>页面导航</h2>
      <el-button @click="$router.push('/foods')">食物库</el-button>
      <el-button @click="$router.push('/meal-logs')">用餐记录</el-button>
      <el-button @click="$router.push('/stats')">数据统计</el-button>
      <el-button @click="$router.push('/profile')">个人资料</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { statsAPI } from '@/api/stats'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const testResult = ref('')

const accessToken = computed(() => localStorage.getItem('access_token'))
const refreshToken = computed(() => localStorage.getItem('refresh_token'))

const testUserAPI = async () => {
  try {
    testResult.value = '正在测试用户API...'
    const response = await authAPI.getCurrentUser()
    testResult.value = `用户API测试成功:\n${JSON.stringify(response.data, null, 2)}`
    ElMessage.success('用户API测试成功')
  } catch (error) {
    testResult.value = `用户API测试失败:\n${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`
    ElMessage.error('用户API测试失败')
  }
}

const testStatsAPI = async () => {
  try {
    testResult.value = '正在测试统计API...'
    const today = new Date().toISOString().split('T')[0]
    const response = await statsAPI.getDailyCaloriesStats(today)
    testResult.value = `统计API测试成功:\n${JSON.stringify(response.data, null, 2)}`
    ElMessage.success('统计API测试成功')
  } catch (error) {
    testResult.value = `统计API测试失败:\n${error.message}\n${JSON.stringify(error.response?.data, null, 2)}`
    ElMessage.error('统计API测试失败')
  }
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  console.log('SimpleDashboard 组件已挂载')
  console.log('认证状态:', authStore.isAuthenticated)
  console.log('用户信息:', authStore.user)
})
</script>

<style scoped>
.simple-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f5f5;
  min-height: 100vh;
}

.simple-dashboard h1 {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
}

.info-section,
.token-section,
.test-section,
.result-section,
.navigation-section {
  background: white;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.info-section h2,
.token-section h2,
.test-section h2,
.result-section h2,
.navigation-section h2 {
  color: #409eff;
  margin-top: 0;
  margin-bottom: 15px;
}

.info-section p,
.token-section p {
  margin: 10px 0;
  font-family: monospace;
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
}

.test-section .el-button,
.navigation-section .el-button {
  margin-right: 10px;
  margin-bottom: 10px;
}

.result-section pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  white-space: pre-wrap;
  font-size: 12px;
}
</style>
