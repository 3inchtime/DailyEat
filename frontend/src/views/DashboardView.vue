<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎回来，{{ authStore.userName }}！</h1>
          <p>今天想吃什么呢？让我们来看看您的饮食情况吧～</p>
        </div>
        <div class="welcome-image">
          <el-icon class="banner-icon"><Food /></el-icon>
        </div>
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="section">
      <h2 class="section-title">
        <el-icon><Lightning /></el-icon>
        快速操作
      </h2>
      <el-row :gutter="24" class="quick-actions">
        <el-col :span="6" :xs="12" :sm="6">
          <div class="action-card" @click="getSuggestion('早餐')">
            <div class="action-icon breakfast">
              <el-icon><Sunrise /></el-icon>
            </div>
            <h3>早餐推荐</h3>
            <p>获取健康早餐建议</p>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <div class="action-card" @click="getSuggestion('中餐')">
            <div class="action-icon lunch">
              <el-icon><Sunny /></el-icon>
            </div>
            <h3>中餐推荐</h3>
            <p>获取营养中餐建议</p>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <div class="action-card" @click="getSuggestion('晚餐')">
            <div class="action-icon dinner">
              <el-icon><Moon /></el-icon>
            </div>
            <h3>晚餐推荐</h3>
            <p>获取美味晚餐建议</p>
          </div>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <div class="action-card" @click="$router.push('/foods')">
            <div class="action-icon manage">
              <el-icon><Plus /></el-icon>
            </div>
            <h3>管理食物</h3>
            <p>添加和管理食物库</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 今日统计 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><DataAnalysis /></el-icon>
          今日饮食统计
        </h2>
        <el-button type="primary" :icon="Refresh" @click="refreshStats" plain>
          刷新数据
        </el-button>
      </div>

      <div v-if="todayStats" class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ todayStats.total_calories_consumed || 0 }}</div>
            <div class="stat-label">已摄入热量 (kcal)</div>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-icon">
            <el-icon><Target /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ todayStats.target_calories || 0 }}</div>
            <div class="stat-label">目标热量 (kcal)</div>
          </div>
        </div>

        <div class="stat-card" :class="remainingCaloriesClass">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ todayStats.remaining_calories || 0 }}</div>
            <div class="stat-label">剩余热量 (kcal)</div>
          </div>
        </div>

        <div class="stat-card info">
          <div class="stat-icon">
            <el-icon><Dish /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ Object.keys(todayStats.breakdown_by_meal_type || {}).length }}</div>
            <div class="stat-label">用餐次数</div>
          </div>
        </div>
      </div>

      <!-- 餐次分布 -->
      <div v-if="todayStats && Object.keys(todayStats.breakdown_by_meal_type || {}).length > 0" class="meal-breakdown">
        <h3>餐次热量分布</h3>
        <el-row :gutter="16">
          <el-col
            v-for="(calories, mealType) in todayStats.breakdown_by_meal_type"
            :key="mealType"
            :span="6"
            :xs="12"
            :sm="6"
          >
            <div class="meal-item">
              <div class="meal-calories">{{ calories }} kcal</div>
              <div class="meal-type">{{ mealType }}</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <div v-else class="no-stats">
        <el-empty description="暂无今日数据">
          <el-button type="primary" @click="$router.push('/meal-logs')">
            添加用餐记录
          </el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFoodsStore } from '@/stores/foods'
import { statsAPI } from '@/api/stats'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Sunrise, Sunny, Moon, Plus, Food, Lightning, DataAnalysis,
  Refresh, TrendCharts, Target, Timer, Dish
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const foodsStore = useFoodsStore()

const todayStats = ref(null)

const remainingCaloriesClass = computed(() => {
  const remaining = todayStats.value?.remaining_calories || 0
  if (remaining > 0) return 'warning'
  if (remaining < 0) return 'danger'
  return 'success'
})

const getSuggestion = async (mealType) => {
  const suggestion = await foodsStore.getSuggestedFood(mealType)
  if (suggestion) {
    ElMessageBox.alert(
      `推荐您今天${mealType}吃：${suggestion.name}${suggestion.description ? `\n\n${suggestion.description}` : ''}`,
      `${mealType}推荐`,
      {
        confirmButtonText: '好的',
        type: 'success'
      }
    )
  }
}

const refreshStats = async () => {
  try {
    console.log('开始获取今日统计数据...')
    const today = new Date().toISOString().split('T')[0]
    console.log('今日日期:', today)

    const response = await statsAPI.getDailyCaloriesStats(today)
    console.log('统计数据获取成功:', response.data)
    todayStats.value = response.data
  } catch (error) {
    console.error('获取今日统计失败:', error)
    console.error('错误详情:', error.response?.data)

    // 设置默认数据，避免页面空白
    todayStats.value = {
      total_calories_consumed: 0,
      target_calories: 2000,
      remaining_calories: 2000,
      breakdown_by_meal_type: {}
    }

    // 如果是认证错误，不显示错误消息（让路由守卫处理）
    if (error.response?.status !== 401) {
      ElMessage.warning('暂时无法获取统计数据，显示默认数据')
    }
  }
}

onMounted(() => {
  refreshStats()
})
</script>

<style scoped>
.dashboard {
  background: #f0f2f5;
  min-height: 100%;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  margin-bottom: 32px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px;
  color: white;
}

.welcome-text h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.welcome-text p {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
}

.banner-icon {
  font-size: 80px;
  opacity: 0.3;
  color: #ffd700;
}

/* 区域样式 */
.section {
  margin-bottom: 32px;
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* 快速操作卡片 */
.quick-actions {
  margin-bottom: 0;
}

.action-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.action-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 32px;
  color: white;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.action-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: all 0.6s ease;
}

.action-card:hover .action-icon::before {
  left: 100%;
}

.action-card:hover .action-icon {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.action-icon.breakfast {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  box-shadow: 0 8px 20px rgba(255, 154, 158, 0.4);
}

.action-icon.lunch {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  box-shadow: 0 8px 20px rgba(168, 237, 234, 0.4);
}

.action-icon.dinner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.action-icon.manage {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  box-shadow: 0 8px 20px rgba(252, 182, 159, 0.4);
}

.action-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.action-card p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 统计卡片网格 - PC端固定4列布局 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* PC端固定4列 */
  gap: 24px;
  margin-bottom: 32px;
  min-width: 1024px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-card.primary {
  border-left: 4px solid #409eff;
}

.stat-card.success {
  border-left: 4px solid #67c23a;
}

.stat-card.warning {
  border-left: 4px solid #e6a23c;
}

.stat-card.danger {
  border-left: 4px solid #f56c6c;
}

.stat-card.info {
  border-left: 4px solid #909399;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  color: white;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.8s ease;
}

.stat-card:hover .stat-icon::before {
  left: 100%;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
}

.stat-card.primary .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #3b82f6 100%);
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
}

.stat-card.success .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #10b981 100%);
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3);
}

.stat-card.warning .stat-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f59e0b 100%);
  box-shadow: 0 4px 15px rgba(230, 162, 60, 0.3);
}

.stat-card.danger .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #ef4444 100%);
  box-shadow: 0 4px 15px rgba(245, 108, 108, 0.3);
}

.stat-card.info .stat-icon {
  background: linear-gradient(135deg, #909399 0%, #6b7280 100%);
  box-shadow: 0 4px 15px rgba(144, 147, 153, 0.3);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 餐次分布 */
.meal-breakdown {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.meal-breakdown h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.meal-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.meal-calories {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.meal-type {
  font-size: 14px;
  color: #606266;
}

/* 无数据状态 */
.no-stats {
  background: white;
  border-radius: 16px;
  padding: 60px 24px;
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

/* PC端专用设计 - 移除响应式断点 */
.dashboard {
  min-width: 1024px;
}

.welcome-content {
  flex-direction: row;
  text-align: left;
  padding: 40px;
}

.welcome-text h1 {
  font-size: 32px;
}

.welcome-text p {
  font-size: 18px;
}

.banner-icon {
  font-size: 80px;
  margin-top: 0;
}

.section-header {
  flex-direction: row;
  align-items: center;
  gap: 24px;
}

.stats-grid {
  grid-template-columns: repeat(4, 1fr); /* 保持4列布局 */
}

.action-card {
  height: 180px;
  padding: 32px 24px;
}

.action-icon {
  width: 64px;
  height: 64px;
  font-size: 28px;
  margin-bottom: 16px;
}
</style>
