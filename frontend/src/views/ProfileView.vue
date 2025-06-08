<template>
  <div class="profile-view">
    <div class="profile-container">
      <!-- 页面头部 -->
      <div class="page-header">
      <div class="header-content">
        <div class="user-avatar-section">
          <el-avatar :size="80" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-basic-info">
            <h1 class="username">{{ authStore.user?.username }}</h1>
            <p class="user-email">{{ authStore.user?.email || '未设置邮箱' }}</p>
            <p class="join-date">注册于 {{ formatDate(authStore.user?.date_joined) }}</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData" size="large">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button type="danger" @click="confirmLogout" size="large" plain>
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 数据概览卡片 -->
      <div class="overview-section">
        <h2 class="section-title">
          <el-icon><DataAnalysis /></el-icon>
          数据概览
        </h2>
        <div class="overview-grid">
          <div class="overview-card primary">
            <div class="card-icon">
              <el-icon><Food /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ foodStats?.total_foods || 0 }}</div>
              <div class="card-label">食物总数</div>
            </div>
          </div>

          <div class="overview-card success">
            <div class="card-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ Math.round(foodStats?.average_calories || 0) }}</div>
              <div class="card-label">平均热量 (kcal)</div>
            </div>
          </div>

          <div class="overview-card warning">
            <div class="card-icon">
              <el-icon><Target /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ currentGoal?.target_calories || '未设置' }}</div>
              <div class="card-label">每日目标 (kcal)</div>
            </div>
          </div>

          <div class="overview-card info">
            <div class="card-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ getDaysJoined() }}</div>
              <div class="card-label">使用天数</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 食物库统计 -->
      <div class="food-stats-section" v-if="foodStats">
        <h2 class="section-title">
          <el-icon><Food /></el-icon>
          食物库统计
        </h2>
        <div class="food-stats-grid">
          <div class="food-stat-card breakfast">
            <div class="stat-icon">
              <el-icon><Sunrise /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.breakfast_foods || 0 }}</div>
              <div class="stat-label">早餐食物</div>
            </div>
          </div>

          <div class="food-stat-card lunch">
            <div class="stat-icon">
              <el-icon><Sunny /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.lunch_foods || 0 }}</div>
              <div class="stat-label">中餐食物</div>
            </div>
          </div>

          <div class="food-stat-card afternoon">
            <div class="stat-icon">
              <el-icon><Coffee /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.afternoon_tea_foods || 0 }}</div>
              <div class="stat-label">下午茶食物</div>
            </div>
          </div>

          <div class="food-stat-card dinner">
            <div class="stat-icon">
              <el-icon><Moon /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.dinner_foods || 0 }}</div>
              <div class="stat-label">晚餐食物</div>
            </div>
          </div>

          <div class="food-stat-card supper">
            <div class="stat-icon">
              <el-icon><Moon /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.supper_foods || 0 }}</div>
              <div class="stat-label">夜宵食物</div>
            </div>
          </div>

          <div class="food-stat-card calories">
            <div class="stat-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ foodStats.foods_with_calories || 0 }}</div>
              <div class="stat-label">有热量数据</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速导航 -->
      <div class="quick-nav-section">
        <h2 class="section-title">
          <el-icon><Guide /></el-icon>
          快速导航
        </h2>
        <div class="nav-grid">
          <div class="nav-card" @click="$router.push('/foods')">
            <div class="nav-icon">
              <el-icon><Food /></el-icon>
            </div>
            <div class="nav-content">
              <h3>食物库</h3>
              <p>管理您的食物</p>
            </div>
          </div>

          <div class="nav-card" @click="$router.push('/meal-logs')">
            <div class="nav-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="nav-content">
              <h3>用餐记录</h3>
              <p>记录饮食情况</p>
            </div>
          </div>

          <div class="nav-card" @click="$router.push('/stats')">
            <div class="nav-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="nav-content">
              <h3>数据统计</h3>
              <p>查看饮食分析</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFoodsStore } from '@/stores/foods'
import { goalsAPI } from '@/api/goals'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Refresh, SwitchButton, DataAnalysis, Food, TrendCharts,
  Target, Calendar, Sunrise, Sunny, Coffee, Moon, Guide, Document
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const foodsStore = useFoodsStore()

const foodStats = ref(null)
const currentGoal = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getDaysJoined = () => {
  if (!authStore.user?.date_joined) return 0
  const joinDate = new Date(authStore.user.date_joined)
  const today = new Date()
  const diffTime = Math.abs(today - joinDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

const fetchFoodStats = async () => {
  await foodsStore.fetchFoodStats()
  foodStats.value = foodsStore.foodStats
}

const fetchCurrentGoal = async () => {
  try {
    const response = await goalsAPI.getCalorieGoal()
    currentGoal.value = response.data
  } catch (error) {
    console.error('Fetch goal error:', error)
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchFoodStats(),
    fetchCurrentGoal()
  ])
  ElMessage.success('数据已刷新')
}

const confirmLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '确认退出',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    authStore.logout()
    router.push('/login')
  })
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.profile-view {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  min-height: 100%;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.profile-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40px;
}

.user-avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-avatar {
  background: rgba(255, 255, 255, 0.2);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.user-basic-info {
  flex: 1;
}

.username {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.user-email {
  font-size: 16px;
  margin: 0 0 4px 0;
  opacity: 0.9;
}

.join-date {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
}

.header-actions {
  display: flex;
  gap: 16px;
}

/* 内容区域 */
.content-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
}

.section-title .el-icon {
  margin-right: 12px;
  font-size: 28px;
  color: #409eff;
}

/* 数据概览 */
.overview-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.overview-card.primary {
  border-left: 4px solid #409eff;
}

.overview-card.success {
  border-left: 4px solid #67c23a;
}

.overview-card.warning {
  border-left: 4px solid #e6a23c;
}

.overview-card.info {
  border-left: 4px solid #909399;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.overview-card.primary .card-icon {
  background: #409eff;
}

.overview-card.success .card-icon {
  background: #67c23a;
}

.overview-card.warning .card-icon {
  background: #e6a23c;
}

.overview-card.info .card-icon {
  background: #909399;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 食物库统计 */
.food-stats-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.food-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.food-stat-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.food-stat-card:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
  color: white;
}

.food-stat-card.breakfast .stat-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.food-stat-card.lunch .stat-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.food-stat-card.afternoon .stat-icon {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.food-stat-card.dinner .stat-icon {
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
}

.food-stat-card.supper .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.food-stat-card.calories .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

/* 快速导航 */
.quick-nav-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.nav-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 32px 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.nav-card:hover {
  background: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px);
  border-color: #409eff;
}

.nav-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.nav-content {
  flex: 1;
}

.nav-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.nav-content p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* PC端专用设计 - 移除响应式断点 */
.profile-view {
  min-width: 1024px;
  padding: 24px;
}

.header-content {
  flex-direction: row;
  align-items: center;
  gap: 32px;
  padding: 40px;
}

.user-avatar-section {
  width: auto;
  flex-direction: row;
  text-align: left;
  gap: 24px;
}

.header-actions {
  width: auto;
  justify-content: flex-end;
  flex-direction: row;
  gap: 16px;
}

.username {
  font-size: 32px;
}

.section-title {
  font-size: 24px;
}

.section-title .el-icon {
  font-size: 28px;
}

.overview-section,
.food-stats-section,
.quick-nav-section {
  padding: 32px;
}

.overview-grid {
  grid-template-columns: repeat(4, 1fr); /* PC端固定4列 */
}

.food-stats-grid {
  grid-template-columns: repeat(4, 1fr); /* PC端固定4列 */
}

.nav-grid {
  grid-template-columns: repeat(3, 1fr); /* PC端固定3列 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-container {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 24px;
    align-items: center;
    text-align: center;
    padding: 32px 24px;
  }

  .user-avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .username {
    font-size: 28px;
  }

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .overview-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .food-stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
  }

  .nav-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .overview-section,
  .food-stats-section,
  .quick-nav-section {
    padding: 24px;
  }
}

@media (min-width: 1200px) {
  .profile-container {
    padding: 32px;
  }

  .header-content {
    padding: 48px;
  }

  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }

  .food-stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }

  .overview-section,
  .food-stats-section,
  .quick-nav-section {
    padding: 40px;
  }
}
</style>
