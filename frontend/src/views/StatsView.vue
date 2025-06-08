<template>
  <div class="stats-view">
    <div class="stats-container">
      <!-- 页面头部 -->
      <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon><DataAnalysis /></el-icon>
            数据统计
          </h1>
          <p class="page-subtitle">查看您的饮食数据分析，了解热量摄入趋势和目标完成情况</p>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 每日统计 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><Calendar /></el-icon>
            每日热量统计
          </h2>
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            @change="fetchDailyStats"
            size="large"
          />
        </div>

        <div v-if="dailyStats" class="daily-stats">
          <!-- 主要统计卡片 -->
          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dailyStats.total_calories_consumed || 0 }}</div>
                <div class="stat-label">已摄入热量 (kcal)</div>
              </div>
            </div>

            <div class="stat-card success">
              <div class="stat-icon">
                <el-icon><Aim /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dailyStats.target_calories || 0 }}</div>
                <div class="stat-label">目标热量 (kcal)</div>
              </div>
            </div>

            <div class="stat-card" :class="remainingCaloriesClass">
              <div class="stat-icon">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ dailyStats.remaining_calories || 0 }}</div>
                <div class="stat-label">剩余热量 (kcal)</div>
              </div>
            </div>

            <div class="stat-card info">
              <div class="stat-icon">
                <el-icon><Dish /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ mealCount }}</div>
                <div class="stat-label">用餐次数</div>
              </div>
            </div>
          </div>

          <!-- 餐次热量分布 -->
          <div class="meal-breakdown" v-if="Object.keys(dailyStats.breakdown_by_meal_type || {}).length > 0">
            <h3>餐次热量分布</h3>
            <div class="meal-grid">
              <div
                v-for="(calories, mealType) in dailyStats.breakdown_by_meal_type"
                :key="mealType"
                class="meal-item"
              >
                <div class="meal-icon" :class="getMealTypeClass(mealType)">
                  <el-icon>
                    <component :is="getMealTypeIcon(mealType)" />
                  </el-icon>
                </div>
                <div class="meal-info">
                  <div class="meal-calories">{{ calories }} kcal</div>
                  <div class="meal-type">{{ mealType }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 进度条和目标分析 -->
          <div class="progress-section" v-if="dailyStats.target_calories">
            <h3>目标完成度</h3>
            <div class="progress-container">
              <div class="progress-main">
                <el-progress
                  :percentage="progressPercentage"
                  :color="progressColor"
                  :stroke-width="24"
                  text-inside
                  class="progress-bar"
                />
                <div class="progress-info">
                  <span class="progress-text">
                    {{ dailyStats.calorie_deficit_or_surplus > 0 ? '超出目标' : '还需摄入' }}
                    <strong>{{ Math.abs(dailyStats.calorie_deficit_or_surplus || 0) }} kcal</strong>
                  </span>
                </div>
              </div>

              <!-- 目标达成建议 -->
              <div class="goal-suggestions">
                <div class="suggestion-card" v-if="dailyStats.calorie_deficit_or_surplus < -500">
                  <el-icon class="suggestion-icon warning"><Timer /></el-icon>
                  <div class="suggestion-content">
                    <div class="suggestion-title">热量摄入不足</div>
                    <div class="suggestion-text">建议增加健康食物摄入，确保营养均衡</div>
                  </div>
                </div>

                <div class="suggestion-card" v-else-if="dailyStats.calorie_deficit_or_surplus > 200">
                  <el-icon class="suggestion-icon danger"><TrendCharts /></el-icon>
                  <div class="suggestion-content">
                    <div class="suggestion-title">热量摄入过量</div>
                    <div class="suggestion-text">建议适量运动或调整下一餐的摄入量</div>
                  </div>
                </div>

                <div class="suggestion-card" v-else>
                  <el-icon class="suggestion-icon success"><Check /></el-icon>
                  <div class="suggestion-content">
                    <div class="suggestion-title">热量摄入合理</div>
                    <div class="suggestion-text">继续保持良好的饮食习惯</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-data">
          <el-empty description="暂无数据">
            <el-button type="primary" @click="$router.push('/meal-logs')">
              添加用餐记录
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 周统计 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><Calendar /></el-icon>
            周统计分析
          </h2>
          <div class="header-actions">
            <el-date-picker
              v-model="weeklyEndDate"
              type="date"
              placeholder="选择结束日期"
              @change="fetchWeeklyStats"
              size="large"
              style="margin-right: 12px"
            />
            <el-button type="primary" @click="fetchWeeklyStats" plain>
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </div>

        <div v-if="weeklyStats" class="weekly-stats">
          <div class="stats-grid">
            <div class="stat-card primary">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ weeklyStats.total_calories || 0 }}</div>
                <div class="stat-label">周总热量 (kcal)</div>
              </div>
            </div>

            <div class="stat-card success">
              <div class="stat-icon">
                <el-icon><Dish /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ weeklyStats.total_meals || 0 }}</div>
                <div class="stat-label">周总用餐次数</div>
              </div>
            </div>

            <div class="stat-card info">
              <div class="stat-icon">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ Math.round(weeklyStats.avg_daily_calories || 0) }}</div>
                <div class="stat-label">日均热量 (kcal)</div>
              </div>
            </div>

            <div class="stat-card" :class="weeklyTrendClass">
              <div class="stat-icon">
                <el-icon><component :is="weeklyTrendIcon" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ weeklyTrendValue }}</div>
                <div class="stat-label">周趋势</div>
              </div>
            </div>
          </div>

          <!-- 简化的数据可视化 -->
          <div class="visual-section" v-if="Object.keys(weeklyStats.daily_stats || {}).length > 0">
            <h3>每日热量趋势</h3>
            <div class="trend-chart">
              <div class="trend-bars">
                <div
                  v-for="(dayData, date) in weeklyStats.daily_stats"
                  :key="date"
                  class="trend-bar"
                >
                  <div class="bar-container">
                    <div
                      class="bar-fill"
                      :style="{
                        height: `${Math.min((dayData.total_calories / maxDailyCalories) * 100, 100)}%`,
                        background: getBarColor(dayData.total_calories)
                      }"
                    ></div>
                  </div>
                  <div class="bar-label">
                    <div class="bar-date">{{ formatShortDate(date) }}</div>
                    <div class="bar-value">{{ dayData.total_calories }}kcal</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 餐次分布可视化 -->
          <div class="visual-section" v-if="mealTypeDistribution.length > 0">
            <h3>餐次分布统计</h3>
            <div class="meal-distribution">
              <div
                v-for="meal in mealTypeDistribution"
                :key="meal.name"
                class="meal-stat-item"
              >
                <div class="meal-stat-header">
                  <span class="meal-name">{{ meal.name }}</span>
                  <span class="meal-count">{{ meal.value }} 次</span>
                </div>
                <div class="meal-progress">
                  <div
                    class="meal-progress-bar"
                    :style="{
                      width: `${(meal.value / maxMealCount) * 100}%`,
                      background: getMealColor(meal.name)
                    }"
                  ></div>
                </div>
                <div class="meal-percentage">
                  {{ Math.round((meal.value / totalMealCount) * 100) }}%
                </div>
              </div>
            </div>
          </div>

          <!-- 周统计洞察 -->
          <div class="insights-section" v-if="weeklyInsights.length > 0">
            <h3>数据洞察</h3>
            <div class="insights-grid">
              <div
                v-for="(insight, index) in weeklyInsights"
                :key="index"
                class="insight-card"
                :class="insight.type"
              >
                <div class="insight-icon">
                  <el-icon><component :is="insight.icon" /></el-icon>
                </div>
                <div class="insight-content">
                  <div class="insight-title">{{ insight.title }}</div>
                  <div class="insight-description">{{ insight.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 每日数据表格 -->
          <div class="daily-breakdown" v-if="Object.keys(weeklyStats.daily_stats || {}).length > 0">
            <h3>每日详细数据</h3>
            <el-card class="table-card" shadow="never">
              <el-table
                :data="dailyStatsArray"
                style="width: 100%"
                :row-style="{ height: '50px' }"
                :header-row-style="{ height: '45px' }"
              >
                <el-table-column prop="date" label="日期" width="120" align="center">
                  <template #default="scope">
                    <span class="date-text">{{ formatDate(scope.row.date) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="total_calories" label="总热量" width="120" align="center">
                  <template #default="scope">
                    <el-tag type="primary" size="large">
                      {{ scope.row.total_calories || 0 }} kcal
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="meal_count" label="用餐次数" width="100" align="center">
                  <template #default="scope">
                    <span class="meal-count">{{ scope.row.meal_count || 0 }} 次</span>
                  </template>
                </el-table-column>
                <el-table-column label="餐次分布" min-width="200">
                  <template #default="scope">
                    <div class="meal-tags">
                      <el-tag
                        v-for="(count, mealType) in scope.row.breakdown_by_meal_type"
                        :key="mealType"
                        :type="getMealTagType(mealType)"
                        size="small"
                        class="meal-tag"
                      >
                        {{ mealType }}: {{ count }}
                      </el-tag>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </div>

        <div v-else class="no-data">
          <el-empty description="暂无周统计数据" />
        </div>
      </div>

      <!-- 热量目标设置 -->
      <div class="section">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><Aim /></el-icon>
            热量目标设置
          </h2>
        </div>

        <el-card class="goal-card" shadow="never">
          <div class="goal-setting">
            <el-form :model="goalForm" label-width="120px" size="large">
              <el-form-item label="每日热量目标">
                <div class="goal-input-group">
                  <el-input-number
                    v-model="goalForm.target_calories"
                    :min="0"
                    :max="10000"
                    placeholder="请输入目标热量"
                    size="large"
                    style="width: 200px"
                  />
                  <span class="unit-text">kcal</span>
                  <el-button type="primary" @click="saveGoal" size="large">
                    <el-icon><Check /></el-icon>
                    保存目标
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { statsAPI } from '@/api/stats'
import { goalsAPI } from '@/api/goals'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Calendar, TrendCharts, Timer, Dish,
  DataLine, Refresh, Check, Sunrise, Sunny, Moon, Coffee,
  ArrowUp, ArrowDown, Minus, Aim
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

const selectedDate = ref(new Date())
const weeklyEndDate = ref(new Date())
const dailyStats = ref(null)
const weeklyStats = ref(null)



const goalForm = reactive({
  target_calories: null
})

const mealCount = computed(() => {
  if (!dailyStats.value?.breakdown_by_meal_type) return 0
  return Object.keys(dailyStats.value.breakdown_by_meal_type).length
})

const remainingCaloriesClass = computed(() => {
  const remaining = dailyStats.value?.remaining_calories || 0
  if (remaining > 0) return 'warning'
  if (remaining < 0) return 'danger'
  return 'success'
})

const progressPercentage = computed(() => {
  if (!dailyStats.value?.target_calories) return 0
  const percentage = (dailyStats.value.total_calories_consumed / dailyStats.value.target_calories) * 100
  return Math.min(percentage, 100)
})

const progressColor = computed(() => {
  const percentage = progressPercentage.value
  if (percentage < 50) return '#f56c6c'
  if (percentage < 80) return '#e6a23c'
  if (percentage <= 100) return '#67c23a'
  return '#f56c6c'
})

const dailyStatsArray = computed(() => {
  if (!weeklyStats.value?.daily_stats) return []
  return Object.entries(weeklyStats.value.daily_stats).map(([date, stats]) => ({
    date,
    ...stats
  })).sort((a, b) => new Date(a.date) - new Date(b.date))
})

// 周趋势分析
const weeklyTrendClass = computed(() => {
  const stats = dailyStatsArray.value
  if (stats.length < 2) return 'info'

  const firstHalf = stats.slice(0, Math.ceil(stats.length / 2))
  const secondHalf = stats.slice(Math.ceil(stats.length / 2))

  const firstAvg = firstHalf.reduce((sum, day) => sum + day.total_calories, 0) / firstHalf.length
  const secondAvg = secondHalf.reduce((sum, day) => sum + day.total_calories, 0) / secondHalf.length

  if (secondAvg > firstAvg * 1.1) return 'warning'
  if (secondAvg < firstAvg * 0.9) return 'success'
  return 'info'
})

const weeklyTrendIcon = computed(() => {
  const trendClass = weeklyTrendClass.value
  if (trendClass === 'warning') return 'ArrowUp'
  if (trendClass === 'success') return 'ArrowDown'
  return 'Minus'
})

const weeklyTrendValue = computed(() => {
  const stats = dailyStatsArray.value
  if (stats.length < 2) return '无数据'

  const firstHalf = stats.slice(0, Math.ceil(stats.length / 2))
  const secondHalf = stats.slice(Math.ceil(stats.length / 2))

  const firstAvg = firstHalf.reduce((sum, day) => sum + day.total_calories, 0) / firstHalf.length
  const secondAvg = secondHalf.reduce((sum, day) => sum + day.total_calories, 0) / secondHalf.length

  const change = ((secondAvg - firstAvg) / firstAvg * 100).toFixed(1)
  return change > 0 ? `+${change}%` : `${change}%`
})

// 餐次分布数据
const mealTypeDistribution = computed(() => {
  if (!weeklyStats.value?.daily_stats) return []

  const distribution = {}
  Object.values(weeklyStats.value.daily_stats).forEach(dayStats => {
    Object.entries(dayStats.breakdown_by_meal_type || {}).forEach(([mealType, count]) => {
      distribution[mealType] = (distribution[mealType] || 0) + count
    })
  })

  return Object.entries(distribution).map(([name, value]) => ({ name, value }))
})

// 简化图表相关计算属性
const maxDailyCalories = computed(() => {
  if (!weeklyStats.value?.daily_stats) return 1
  const calories = Object.values(weeklyStats.value.daily_stats).map(day => day.total_calories || 0)
  return Math.max(...calories, 1)
})

const maxMealCount = computed(() => {
  if (mealTypeDistribution.value.length === 0) return 1
  return Math.max(...mealTypeDistribution.value.map(meal => meal.value))
})

const totalMealCount = computed(() => {
  return mealTypeDistribution.value.reduce((sum, meal) => sum + meal.value, 0)
})

// 周统计洞察
const weeklyInsights = computed(() => {
  if (!weeklyStats.value?.daily_stats) return []

  const insights = []
  const stats = dailyStatsArray.value

  if (stats.length === 0) return insights

  // 分析最活跃的用餐日
  const mostActiveDayData = stats.reduce((max, day) =>
    day.meal_count > max.meal_count ? day : max
  )
  insights.push({
    type: 'success',
    icon: 'TrendCharts',
    title: '最活跃用餐日',
    description: `${new Date(mostActiveDayData.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })} - ${mostActiveDayData.meal_count} 次用餐`
  })

  // 分析热量摄入最高的一天
  const highestCalorieDay = stats.reduce((max, day) =>
    day.total_calories > max.total_calories ? day : max
  )
  insights.push({
    type: 'warning',
    icon: 'Dish',
    title: '热量摄入最高',
    description: `${new Date(highestCalorieDay.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })} - ${highestCalorieDay.total_calories} kcal`
  })

  // 分析用餐规律
  const avgMealsPerDay = weeklyStats.value.total_meals / 7
  if (avgMealsPerDay >= 3) {
    insights.push({
      type: 'success',
      icon: 'Check',
      title: '用餐规律良好',
      description: `平均每日 ${avgMealsPerDay.toFixed(1)} 次用餐，保持规律饮食`
    })
  } else {
    insights.push({
      type: 'info',
      icon: 'Timer',
      title: '建议增加用餐频次',
      description: `平均每日 ${avgMealsPerDay.toFixed(1)} 次用餐，建议保持规律饮食`
    })
  }

  // 分析最喜欢的餐次
  const favoriteMealType = mealTypeDistribution.value.reduce((max, meal) =>
    meal.value > max.value ? meal : max, { name: '', value: 0 }
  )
  if (favoriteMealType.name) {
    insights.push({
      type: 'info',
      icon: 'Coffee',
      title: '最常用餐时间',
      description: `${favoriteMealType.name} - ${favoriteMealType.value} 次记录`
    })
  }

  return insights
})

const fetchDailyStats = async () => {
  try {
    const dateStr = selectedDate.value.toISOString().split('T')[0]
    const response = await statsAPI.getDailyCaloriesStats(dateStr)
    dailyStats.value = response.data
  } catch (error) {
    ElMessage.error('获取每日统计失败')
    console.error('Fetch daily stats error:', error)
  }
}

const fetchWeeklyStats = async () => {
  try {
    const dateStr = weeklyEndDate.value ? weeklyEndDate.value.toISOString().split('T')[0] : null
    const response = await statsAPI.getWeeklyStats(dateStr)
    weeklyStats.value = response.data
  } catch (error) {
    ElMessage.error('获取周统计失败')
    console.error('Fetch weekly stats error:', error)
  }
}

const fetchGoal = async () => {
  try {
    const response = await goalsAPI.getCalorieGoal()
    goalForm.target_calories = response.data.target_calories
  } catch (error) {
    console.error('Fetch goal error:', error)
  }
}

const saveGoal = async () => {
  try {
    if (goalForm.target_calories === null) {
      ElMessage.warning('请输入目标热量')
      return
    }

    await goalsAPI.updateCalorieGoal(goalForm)
    ElMessage.success('目标保存成功！')
    fetchDailyStats() // 刷新每日统计
  } catch (error) {
    ElMessage.error('保存目标失败')
    console.error('Save goal error:', error)
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric'
  })
}

const getMealTypeClass = (mealType) => {
  const classes = {
    '早餐': 'breakfast',
    '中餐': 'lunch',
    '下午茶': 'afternoon',
    '晚餐': 'dinner',
    '夜宵': 'supper'
  }
  return classes[mealType] || 'default'
}

const getMealTypeIcon = (mealType) => {
  const icons = {
    '早餐': 'Sunrise',
    '中餐': 'Sunny',
    '下午茶': 'Coffee',
    '晚餐': 'Moon',
    '夜宵': 'Moon'
  }
  return icons[mealType] || 'Dish'
}

const getMealTagType = (mealType) => {
  const types = {
    '早餐': 'warning',
    '中餐': 'success',
    '下午茶': 'info',
    '晚餐': 'primary',
    '夜宵': 'danger'
  }
  return types[mealType] || 'info'
}

// 简化图表辅助方法
const formatShortDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const getBarColor = (calories) => {
  if (calories < 800) return 'linear-gradient(135deg, #f56c6c 0%, #ff8a80 100%)'
  if (calories < 1500) return 'linear-gradient(135deg, #e6a23c 0%, #ffb74d 100%)'
  if (calories < 2200) return 'linear-gradient(135deg, #67c23a 0%, #81c784 100%)'
  return 'linear-gradient(135deg, #409eff 0%, #64b5f6 100%)'
}

const getMealColor = (mealType) => {
  const colors = {
    '早餐': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    '中餐': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    '下午茶': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    '晚餐': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '夜宵': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  }
  return colors[mealType] || 'linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%)'
}







onMounted(() => {
  fetchDailyStats()
  fetchWeeklyStats()
  fetchGoal()
})
</script>

<style scoped>
.stats-view {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  min-height: 100%;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.stats-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

/* 页面头部 */
.page-header {
  background: white;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.header-content {
  padding: 32px;
}

.title-section {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
}

.page-title .el-icon {
  margin-right: 12px;
  font-size: 32px;
  color: #409eff;
}

.page-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

/* 内容区域 */
.content-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
}

.section-title .el-icon {
  margin-right: 12px;
  font-size: 28px;
  color: #409eff;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
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

.stat-card.primary .stat-icon {
  background: #409eff;
}

.stat-card.success .stat-icon {
  background: #67c23a;
}

.stat-card.warning .stat-icon {
  background: #e6a23c;
}

.stat-card.danger .stat-icon {
  background: #f56c6c;
}

.stat-card.info .stat-icon {
  background: #909399;
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
  margin-top: 32px;
}

.meal-breakdown h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.meal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.meal-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.meal-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.meal-icon {
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

.meal-icon.breakfast {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.meal-icon.lunch {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.meal-icon.afternoon {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.meal-icon.dinner {
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
}

.meal-icon.supper {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.meal-info {
  flex: 1;
}

.meal-calories {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.meal-type {
  font-size: 14px;
  color: #606266;
}

/* 进度条 */
.progress-section {
  margin-top: 32px;
}

.progress-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.progress-container {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.progress-main {
  flex: 1;
}

.progress-bar {
  margin-bottom: 16px;
}

.progress-info {
  text-align: center;
}

.progress-text {
  font-size: 16px;
  color: #606266;
}

.progress-text strong {
  color: #409eff;
  font-weight: 600;
}

/* 目标建议 */
.goal-suggestions {
  flex: 0 0 300px;
}

.suggestion-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e4e7ed;
}

.suggestion-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.suggestion-icon.success {
  background: #67c23a;
}

.suggestion-icon.warning {
  background: #e6a23c;
}

.suggestion-icon.danger {
  background: #f56c6c;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.suggestion-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

/* 表格样式 */
.table-card {
  border-radius: 12px;
  border: none;
  margin-top: 20px;
}

.daily-breakdown h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.date-text {
  font-weight: 500;
  color: #303133;
}

.meal-count {
  font-weight: 500;
  color: #606266;
}

.meal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.meal-tag {
  margin: 0;
}

/* 目标设置 */
.goal-card {
  border-radius: 16px;
  border: none;
}

.goal-setting {
  padding: 20px 0;
}

.goal-input-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.unit-text {
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

/* 无数据状态 */
.no-data {
  padding: 60px 24px;
  text-align: center;
}

/* 图表样式 */
.chart-section {
  margin-top: 32px;
}

.chart-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.chart-container {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.chart {
  width: 100%;
  background: white;
  border-radius: 8px;
}

/* 头部操作区域 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 简化可视化样式 */
.visual-section {
  margin-top: 32px;
}

.visual-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

/* 趋势图样式 */
.trend-chart {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e9ecef;
}

.trend-bars {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  height: 200px;
  padding: 20px 0;
}

.trend-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar-container {
  flex: 1;
  width: 100%;
  max-width: 40px;
  display: flex;
  align-items: end;
  justify-content: center;
  margin-bottom: 12px;
}

.bar-fill {
  width: 100%;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.bar-fill:hover {
  transform: scaleY(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.bar-label {
  text-align: center;
  font-size: 12px;
}

.bar-date {
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.bar-value {
  color: #606266;
  font-size: 11px;
}

/* 餐次分布样式 */
.meal-distribution {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e9ecef;
}

.meal-stat-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.meal-stat-item:last-child {
  margin-bottom: 0;
}

.meal-stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 120px;
  margin-right: 16px;
}

.meal-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.meal-count {
  font-size: 12px;
  color: #606266;
}

.meal-progress {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 12px;
}

.meal-progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.meal-percentage {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  min-width: 40px;
  text-align: right;
}

/* 洞察卡片 */
.insights-section {
  margin-top: 32px;
}

.insights-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.insight-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.insight-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.insight-card.success {
  border-left: 4px solid #67c23a;
}

.insight-card.warning {
  border-left: 4px solid #e6a23c;
}

.insight-card.info {
  border-left: 4px solid #409eff;
}

.insight-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.insight-card.success .insight-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.insight-card.warning .insight-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.insight-card.info .insight-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.insight-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background: #f8f9fa;
}

:deep(.el-table th) {
  background: #f8f9fa;
  color: #303133;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-table__row:hover) {
  background: #f8f9fa;
}

/* PC端专用设计 - 移除响应式断点 */
.stats-view {
  min-width: 1024px;
  padding: 24px;
}

.section-header {
  flex-direction: row;
  align-items: center;
  gap: 24px;
}

.header-content {
  padding: 32px;
}

.section {
  padding: 32px;
}

.page-title {
  font-size: 28px;
}

.page-title .el-icon {
  font-size: 32px;
}

.section-title {
  font-size: 24px;
}

.section-title .el-icon {
  font-size: 28px;
}

.stats-grid {
  grid-template-columns: repeat(4, 1fr); /* PC端固定4列 */
}

.meal-grid {
  grid-template-columns: repeat(4, 1fr); /* PC端固定4列 */
}

.goal-input-group {
  flex-direction: row;
  align-items: center;
  gap: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-container {
    padding: 16px;
  }

  .header-content {
    padding: 24px;
  }

  .page-title {
    font-size: 24px;
  }

  .section {
    padding: 24px;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
    gap: 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .meal-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .goal-input-group {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .progress-container {
    flex-direction: column;
    gap: 20px;
  }

  .goal-suggestions {
    flex: none;
  }

  .chart-container {
    padding: 16px;
  }

  .chart {
    height: 250px !important;
  }
}

@media (min-width: 1200px) {
  .stats-container {
    padding: 32px;
  }

  .section {
    padding: 40px;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }
}
</style>
