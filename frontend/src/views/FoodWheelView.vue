<template>
  <div class="food-wheel-container">
    <!-- 悬浮结果弹窗 -->
    <div class="result-overlay" v-if="selectedFood" @click="clearSelection">
      <div class="result-modal" @click.stop>
        <div class="result-close-btn">
          <el-button
            type="text"
            @click="clearSelection"
            :icon="Close"
            size="small"
            class="close-button"
          >
          </el-button>
        </div>

        <div class="result-content">
          <div class="result-emoji">{{ selectedFood.emoji }}</div>
          <h2 class="result-title">🎉 今天就吃这个！</h2>
          <h3 class="result-food">{{ selectedFood.name }}</h3>
          <p class="result-description" v-if="selectedFood.description">
            {{ selectedFood.description }}
          </p>

          <!-- 食物详细信息 -->
          <div class="food-details" v-if="selectedFood.calories > 0">
            <div class="detail-item">
              <span class="detail-label">热量:</span>
              <span class="detail-value">{{ selectedFood.calories }} 卡/100g</span>
            </div>
            <div class="detail-item" v-if="selectedFood.category">
              <span class="detail-label">分类:</span>
              <span class="detail-value">{{ selectedFood.category }}</span>
            </div>
          </div>

          <div class="result-actions">
            <el-button type="primary" @click="addToMealLog" :icon="Plus" size="large">
              添加到用餐记录
            </el-button>
            <el-button @click="spinAgain" :icon="Refresh" size="large">
              再转一次
            </el-button>
            <el-button @click="viewFoodDetails" :icon="View" size="large" v-if="selectedFood.id">
              查看详情
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1 class="main-title">🍽️ 今天吃什么？</h1>
    </div>

    <!-- 转盘区域 -->
    <div class="wheel-section">
      <!-- 加载状态 -->
      <div v-if="isLoadingFoods" class="loading-container">
        <div class="loading-spinner">
          <el-icon class="spinning"><Loading /></el-icon>
        </div>
        <p class="loading-text">正在加载美食数据...</p>
      </div>

      <!-- 加载错误状态 -->
      <div v-else-if="loadError" class="error-container">
        <div class="error-icon">⚠️</div>
        <p class="error-text">加载失败，使用默认数据</p>
        <el-button @click="reloadFoods" type="primary" size="small">重新加载</el-button>
      </div>

              <!-- 转盘主体 -->
        <div v-else class="wheel-container" :class="{ spinning: isSpinning }">
          <!-- Canvas 转盘 -->
          <div class="turntable-container">
            <canvas ref="turntableCanvas" width="500" height="500"></canvas>
            <div class="pointer right"></div>
            
            <!-- 中心按钮 -->
            <button class="center-button" @click="spinWheel" :disabled="isSpinning || isLoadingFoods">
              <div class="button-content">
                <el-icon v-if="!isSpinning" class="spin-icon"><Refresh /></el-icon>
                <el-icon v-else class="spin-icon spinning"><Loading /></el-icon>
                <span class="button-text">{{ isSpinning ? '转动中...' : '开始转盘' }}</span>
              </div>
            </button>
          </div>
        </div>
    </div>

    <!-- 当前转盘食物列表 -->
    <div class="foods-display-section" v-if="!isLoadingFoods && wheelFoods.length > 0">
      <div class="foods-display-card">
        <h3 class="foods-title">
          <el-icon><Food /></el-icon>
          转盘食物列表 ({{ filteredFoods.length }} / {{ wheelFoods.length }} 种)
        </h3>

        <!-- 搜索框 -->
        <div class="search-section">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索食物名称..."
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
        </div>

        <div class="foods-grid" v-if="filteredFoods.length > 0">
          <div
            v-for="(food, index) in filteredFoods"
            :key="food.id || index"
            class="food-item"
            :class="{ 'selected': selectedFood && selectedFood.id === food.id }"
            @click="selectFood(food)"
          >
            <div class="food-emoji">{{ food.emoji }}</div>
            <div class="food-name">{{ food.name }}</div>
            <div class="food-calories" v-if="food.calories">{{ food.calories }}卡</div>
          </div>
        </div>

        <!-- 无搜索结果提示 -->
        <div class="no-results" v-else-if="searchKeyword.trim()">
          <div class="no-results-icon">🔍</div>
          <p class="no-results-text">没有找到匹配的食物</p>
          <p class="no-results-tip">试试搜索其他关键词</p>
          <el-button @click="searchKeyword = ''" size="small">清空搜索</el-button>
        </div>
        <div class="foods-actions">
          <el-button @click="$router.push('/foods')" :icon="Setting" size="small">
            管理食物库
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFoodsStore } from '@/stores/foods'
import { useMealLogsStore } from '@/stores/mealLogs'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Loading, Plus, Food, Document, DataAnalysis, View, Setting, Search, Close
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const foodsStore = useFoodsStore()
const mealLogsStore = useMealLogsStore()

const isSpinning = ref(false)
const rotation = ref(0)
const selectedFood = ref(null)
const searchKeyword = ref('')

// Canvas 相关引用
const turntableCanvas = ref(null)
const ctx = ref(null)

// 默认食物数据（如果后端没有数据时使用）
const defaultFoods = [
  { name: '米饭', emoji: '🍚', description: '经典主食，营养丰富', calories_per_100g: 130 },
  { name: '面条', emoji: '🍜', description: '温暖的汤面，暖胃又暖心', calories_per_100g: 150 },
  { name: '饺子', emoji: '🥟', description: '传统美食，馅料丰富', calories_per_100g: 200 },
  { name: '炒菜', emoji: '🥬', description: '新鲜蔬菜，健康营养', calories_per_100g: 80 },
  { name: '鸡肉', emoji: '🍗', description: '高蛋白，低脂肪', calories_per_100g: 165 },
  { name: '鱼肉', emoji: '🐟', description: '富含Omega-3，健康美味', calories_per_100g: 140 },
  { name: '汉堡', emoji: '🍔', description: '快餐经典，满足感十足', calories_per_100g: 250 },
  { name: '披萨', emoji: '🍕', description: '意式美食，多种口味', calories_per_100g: 266 },
  { name: '寿司', emoji: '🍣', description: '日式精致，新鲜美味', calories_per_100g: 150 },
  { name: '沙拉', emoji: '🥗', description: '轻食选择，清爽健康', calories_per_100g: 50 },
  { name: '汤品', emoji: '🍲', description: '营养汤品，温暖身心', calories_per_100g: 60 },
  { name: '水果', emoji: '🍎', description: '天然甜味，维生素丰富', calories_per_100g: 52 }
]

// 转盘食物数据
const wheelFoods = computed(() => {
  // 优先使用后端获取的食物数据，如果没有则使用默认数据
  let availableFoods = []

  if (foodsStore.foods && foodsStore.foods.length > 0) {
    // 使用后端数据
    availableFoods = foodsStore.foods
    console.log('使用后端食物数据:', availableFoods.length, '个食物')
  } else {
    // 使用默认数据
    availableFoods = defaultFoods
    console.log('使用默认食物数据:', availableFoods.length, '个食物')
  }

  // 转盘显示最多12个食物，但列表显示所有食物
  const foods = availableFoods

  return foods.map(food => ({
    id: food.id || food.food_id || Math.random(),
    name: food.name,
    emoji: food.emoji || getRandomEmoji(),
    description: food.description || '',
    calories: food.calories || food.calories_per_100g || 0,
    category: food.category || '其他'
  }))
})

// 过滤后的食物数据（用于搜索）
const filteredFoods = computed(() => {
  if (!searchKeyword.value.trim()) {
    return wheelFoods.value
  }

  const keyword = searchKeyword.value.toLowerCase().trim()
  return wheelFoods.value.filter(food =>
    food.name.toLowerCase().includes(keyword) ||
    (food.description && food.description.toLowerCase().includes(keyword)) ||
    (food.category && food.category.toLowerCase().includes(keyword))
  )
})

// 转盘显示的食物（最多20个）
const wheelDisplayFoods = computed(() => {
  return wheelFoods.value.slice(0, 20)
})

// 获取随机emoji（如果食物没有emoji）
const getRandomEmoji = () => {
  const emojis = ['🍽️', '🥘', '🍱', '🥙', '🌮', '🥪', '🍖', '🥩', '🍳', '🥓']
  return emojis[Math.floor(Math.random() * emojis.length)]
}

// 颜色数组 - 20种颜色组合
const segmentColors = [
  '#f0f9ff', // 淡蓝白
  '#f3e8ff', // 淡紫白
  '#dcfce7', // 淡绿白
  '#fef3c7', // 淡黄白
  '#fee2e2', // 淡红白
  '#e2e8f0', // 浅灰白
  '#fed7aa', // 淡橙白
  '#cbd5e1', // 蓝灰白
  '#fef08a', // 淡黄绿白
  '#ddd6fe', // 淡紫蓝白
  '#bbf7d0', // 淡薄荷白
  '#fbcfe8', // 淡粉白
  '#d9e2ec', // 淡蓝灰白
  '#c1e1dc', // 淡青绿白
  '#f8e3dd', // 淡珊瑚白
  '#f2f0d8', // 淡米白
  '#d6eef5', // 淡水蓝白
  '#ebdde7', // 淡紫粉白
  '#e4f5d3', // 淡草绿白
  '#e3e0f3'  // 淡蓝紫白
]

// 获取扇形颜色
const getSegmentColor = (index) => {
  return segmentColors[index % segmentColors.length]
}

// 绘制转盘
const drawWheel = () => {
  if (!ctx.value) {
    console.warn('⚠️ Canvas context 不存在，无法绘制转盘')
    return
  }

  if (!turntableCanvas.value) {
    console.warn('⚠️ Canvas 元素不存在，无法绘制转盘')
    return
  }

  if (wheelDisplayFoods.value.length === 0) {
    console.warn('⚠️ 没有食物数据，无法绘制转盘')
    return
  }

  console.log('🎨 开始绘制转盘，食物数量:', wheelDisplayFoods.value.length)

  const canvas = turntableCanvas.value
  const context = ctx.value
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) * 0.9 // 转盘半径

  // 清除画布
  context.clearRect(0, 0, canvas.width, canvas.height)
  context.save()
  context.translate(centerX, centerY) // 将原点移到中心
  context.rotate(rotation.value * (Math.PI / 180)) // 角度转弧度进行旋转

  const totalSegments = wheelDisplayFoods.value.length
  const anglePerSegment = (2 * Math.PI) / totalSegments

  // 绘制外层彩色扇形
  for (let i = 0; i < totalSegments; i++) {
    const food = wheelDisplayFoods.value[i]
    const startAngle = i * anglePerSegment
    const endAngle = (i + 1) * anglePerSegment

    // 绘制扇形
    context.beginPath()
    context.moveTo(0, 0)
    context.arc(0, 0, radius, startAngle, endAngle)
    context.closePath()
    context.fillStyle = getSegmentColor(i)
    context.fill()
    context.strokeStyle = '#ffffff' // 白色分隔线
    context.lineWidth = 2
    context.stroke()

    // 绘制文字
    context.save()
    context.rotate(startAngle + anglePerSegment / 2) // 旋转文字使其朝外
    context.textAlign = "center"
    context.textBaseline = "middle"
    context.fillStyle = getTextColor(getSegmentColor(i)) // 根据背景色选择文字颜色
    
    const text = food.name
    // 将文字定位在扇形中间位置
    const textRadius = radius * 0.7 // 文字距离圆心的距离
    
    // 调整字体大小以适应扇形区域
    let fontSize = 16
    context.font = `bold ${fontSize}px Arial`
    let textWidth = context.measureText(text).width
    const maxTextWidth = radius * 0.5 // 文字最大宽度

    // 如果文字太长，缩小字体
    while(textWidth > maxTextWidth && fontSize > 10) {
      fontSize--
      context.font = `bold ${fontSize}px Arial`
      textWidth = context.measureText(text).width
    }
    
    // 只绘制食物名称
    context.fillText(text, textRadius, 0)
    
    context.restore()
  }
  
  // 绘制中心白色圆
  context.beginPath()
  context.arc(0, 0, radius * 0.25, 0, 2 * Math.PI)
  context.fillStyle = "#ffffff"
  context.fill()
  context.strokeStyle = "#e2e8f0"
  context.lineWidth = 2
  context.stroke()

  context.restore()

  console.log('✅ 转盘绘制完成，包含', totalSegments, '个扇形')
}

// 根据背景颜色决定文字颜色，确保可读性
const getTextColor = (bgColor) => {
  // 将颜色转换为RGB
  const hexToRgb = (hex) => {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return { r, g, b }
  }
  
  const rgb = hexToRgb(bgColor)
  // 计算亮度
  const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000
  return brightness > 135 ? '#333333' : '#FFFFFF' // 根据背景色亮度选择文字颜色
}

// 转动转盘
const spinWheel = () => {
  if (isSpinning.value) return
  
  isSpinning.value = true
  selectedFood.value = null
  
  // 随机转动角度（至少转5圈）
  const spinRevolutions = 5 // 基础旋转圈数
  const randomStopSegment = Math.floor(Math.random() * wheelDisplayFoods.value.length)
  const segmentAngle = 360 / wheelDisplayFoods.value.length
  
  // 计算目标角度：当前角度 + 至少5圈 + 随机扇区
  const currentRotationDeg = rotation.value % 360
  const targetRotation = currentRotationDeg + (spinRevolutions * 360) + 
                        (randomStopSegment * segmentAngle) + (segmentAngle / 2)
  
  // 动画参数
  const spinDuration = 5000 // 旋转持续时间（毫秒）
  const startTime = performance.now()
  const initialRotation = rotation.value
  
  const animateSpin = (currentTime) => {
    const elapsedTime = currentTime - startTime
    const progress = Math.min(elapsedTime / spinDuration, 1)
    
    // 缓动函数：加速然后减速
    const easedProgress = 1 - Math.pow(1 - progress, 4)
    
    // 计算当前角度
    rotation.value = initialRotation + (targetRotation - initialRotation) * easedProgress
    
    // 重绘转盘
    drawWheel()
    
    if (progress < 1) {
      requestAnimationFrame(animateSpin)
    } else {
      // 动画结束
      isSpinning.value = false
      rotation.value = targetRotation % 360
      showResult()
    }
  }
  
  requestAnimationFrame(animateSpin)
}

// 显示结果
const showResult = () => {
  const totalSegments = wheelDisplayFoods.value.length
  const anglePerSegment = 360 / totalSegments
  const normalizedRotation = rotation.value % 360

  // 计算指针指向的扇形（指针在顶部，所以需要调整计算）
  // 注意：转盘是顺时针旋转的，指针固定在顶部
  const pointerAngle = (360 - normalizedRotation) % 360
  const selectedIndex = Math.floor(pointerAngle / anglePerSegment)
  
  // 确保索引在有效范围内
  const validIndex = (selectedIndex + totalSegments) % totalSegments
  selectedFood.value = wheelDisplayFoods.value[validIndex]

  // 显示结果消息
  ElMessage.success(`恭喜！今天吃 ${selectedFood.value.name}！`)
}

// 再转一次
const spinAgain = () => {
  selectedFood.value = null
  spinWheel()
}

// 添加到用餐记录
const addToMealLog = async () => {
  ElMessageBox.confirm(
    `确定要将 "${selectedFood.value.name}" 添加到今天的用餐记录吗？`,
    '添加用餐记录',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    try {
      // 准备用餐记录数据
      const mealLogData = {
        food_id: selectedFood.value.id,
        meal_type_recorded: getMealTypeByTime(), // 根据当前时间自动判断餐次
        eaten_at_datetime: new Date().toISOString(),
        notes: `从转盘选择的食物: ${selectedFood.value.name}`
      }
      
      // 调用store的方法添加用餐记录
      const result = await mealLogsStore.createMealLog(mealLogData)
      
      if (result) {
        ElMessage.success(`已成功添加 ${selectedFood.value.name} 到用餐记录！`)
        router.push('/meal-logs')
      }
    } catch (error) {
      console.error('添加用餐记录失败:', error)
      ElMessage.error('添加用餐记录失败，请稍后重试')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 根据当前时间自动判断餐次
const getMealTypeByTime = () => {
  const hour = new Date().getHours()
  
  if (hour >= 5 && hour < 10) {
    return '早餐'
  } else if (hour >= 10 && hour < 14) {
    return '中餐'
  } else if (hour >= 14 && hour < 17) {
    return '下午茶'
  } else if (hour >= 17 && hour < 21) {
    return '晚餐'
  } else {
    return '夜宵'
  }
}

// 查看食物详情
const viewFoodDetails = () => {
  if (selectedFood.value && selectedFood.value.id) {
    router.push(`/foods/${selectedFood.value.id}`)
  } else {
    ElMessage.info('该食物暂无详细信息')
  }
}

// 直接选择食物
const selectFood = (food) => {
  selectedFood.value = food
  ElMessage.success(`已选择：${food.name}！`)
}

// 清除选择
const clearSelection = () => {
  selectedFood.value = null
}

// 加载状态
const isLoadingFoods = ref(true)
const loadError = ref(null)

// 加载食物数据
const loadFoodsData = async () => {
  isLoadingFoods.value = true
  loadError.value = null

  try {
    console.log('开始从后端加载食物数据...')
    await foodsStore.fetchFoods()

    if (foodsStore.foods && foodsStore.foods.length > 0) {
      console.log('✅ 后端食物数据加载成功:', foodsStore.foods.length, '个食物')
      ElMessage.success(`成功加载 ${foodsStore.foods.length} 个食物`)
    } else {
      console.log('⚠️ 后端没有食物数据，使用默认数据')
      ElMessage.info('使用默认食物数据')
    }

    // 数据加载完成后，等待下一个tick再重绘转盘
    await nextTick()
    if (ctx.value) {
      console.log('🎨 数据加载完成，重新绘制转盘')
      drawWheel()
    }
  } catch (error) {
    console.error('❌ 加载食物数据失败:', error)
    loadError.value = error.message

    // 如果是认证错误，不显示错误消息（让路由守卫处理）
    if (error.response?.status !== 401) {
      ElMessage.warning('无法加载食物数据，使用默认数据')
    }

    // 即使出错也要重绘转盘（使用默认数据）
    await nextTick()
    if (ctx.value) {
      console.log('🎨 使用默认数据重新绘制转盘')
      drawWheel()
    }
  } finally {
    isLoadingFoods.value = false
  }
}

// 重新加载食物数据
const reloadFoods = async () => {
  console.log('🔄 开始重新加载食物数据...')
  await loadFoodsData()

  // 确保数据加载完成后重新绘制转盘
  nextTick(() => {
    if (ctx.value && wheelDisplayFoods.value.length > 0) {
      console.log('🎨 重新绘制转盘，食物数量:', wheelDisplayFoods.value.length)
      drawWheel()
    } else {
      console.warn('⚠️ 无法重新绘制转盘: ctx.value=', !!ctx.value, 'wheelDisplayFoods.length=', wheelDisplayFoods.value.length)
    }
  })
}

// 初始化和更新Canvas
const initCanvas = () => {
  if (!turntableCanvas.value) {
    console.warn('⚠️ Canvas 元素不存在，无法初始化')
    return
  }

  console.log('🎨 初始化 Canvas')
  ctx.value = turntableCanvas.value.getContext('2d')

  if (ctx.value) {
    console.log('✅ Canvas context 创建成功')
    // 等待下一个tick确保数据已经准备好
    nextTick(() => {
      if (wheelDisplayFoods.value.length > 0) {
        drawWheel()
      } else {
        console.log('⏳ 等待食物数据加载完成...')
      }
    })
  } else {
    console.error('❌ 无法创建 Canvas context')
  }
}

// 监听窗口大小变化，重绘转盘
const handleResize = () => {
  nextTick(() => {
    if (turntableCanvas.value) {
      drawWheel()
    }
  })
}

// 监听食物数据变化，重绘转盘
watch(wheelDisplayFoods, (newFoods, oldFoods) => {
  console.log('🔄 食物数据发生变化:', {
    oldCount: oldFoods?.length || 0,
    newCount: newFoods?.length || 0
  })

  nextTick(() => {
    if (ctx.value && newFoods.length > 0) {
      console.log('🎨 因数据变化重新绘制转盘')
      drawWheel()
    } else {
      console.warn('⚠️ 无法重绘转盘: ctx存在=', !!ctx.value, '食物数量=', newFoods.length)
    }
  })
}, { deep: true })

// 组件挂载
onMounted(async () => {
  console.log('🎡 FoodWheelView 组件已挂载')
  console.log('认证状态:', authStore.isAuthenticated)
  console.log('用户信息:', authStore.user)

  // 加载食物数据
  await loadFoodsData()
  
  // 初始化Canvas
  initCanvas()
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize)
})

// 在组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.food-wheel-container {
  min-height: 100vh;
  background:
    radial-gradient(circle at 10% 90%, rgba(59, 130, 246, 0.07) 0%, transparent 55%),
    radial-gradient(circle at 90% 10%, rgba(147, 51, 234, 0.05) 0%, transparent 55%),
    radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.03) 0%, transparent 45%),
    linear-gradient(135deg, #f9fafb 0%, #f3f4f6 50%, #e5e7eb 100%);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
  width: 100%;
  max-width: 100vw;
  box-sizing: border-box;
}

.food-wheel-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background:
    radial-gradient(circle, rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    radial-gradient(circle, rgba(147, 51, 234, 0.04) 1px, transparent 1px),
    radial-gradient(circle, rgba(16, 185, 129, 0.04) 1px, transparent 1px);
  background-size: 80px 80px, 120px 120px, 100px 100px;
  background-position: 0 0, 40px 40px, 20px 60px;
  animation: sparkle 50s linear infinite;
  pointer-events: none;
}

@keyframes sparkle {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(-80px, -80px) rotate(360deg); }
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  color: #1e293b;
  margin-bottom: 40px;
  max-width: 100%;
  width: 100%;
  padding: 0 20px;
  box-sizing: border-box;
  animation: fadeSlideDown 0.8s ease-out;
}

@keyframes fadeSlideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 20px 0;
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.subtitle {
  font-size: 20px;
  margin: 0 0 24px 0;
  color: #64748b;
  font-weight: 400;
  line-height: 1.6;
}

/* 转盘区域 */
.wheel-section {
  margin-bottom: 40px;
  perspective: 1000px;
  width: 100%;
  display: flex;
  justify-content: center;
  animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 450px;
  width: 450px;
  color: #64748b;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  box-shadow: 
    0 10px 30px rgba(15, 23, 42, 0.08),
    0 5px 15px rgba(15, 23, 42, 0.05);
  border: 1px solid rgba(226, 232, 240, 0.6);
  backdrop-filter: blur(10px);
}

.loading-spinner {
  font-size: 48px;
  margin-bottom: 20px;
  color: #3b82f6;
}

.loading-text {
  font-size: 18px;
  margin: 0;
  font-weight: 500;
}

/* 错误状态 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 450px;
  width: 450px;
  color: #64748b;
  text-align: center;
  background: rgba(254, 242, 242, 0.9);
  border-radius: 24px;
  box-shadow: 
    0 10px 30px rgba(239, 68, 68, 0.1),
    0 5px 15px rgba(239, 68, 68, 0.05);
  border: 1px solid rgba(254, 202, 202, 0.6);
  backdrop-filter: blur(10px);
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-text {
  font-size: 16px;
  margin: 0 0 20px 0;
  font-weight: 500;
}

/* 转盘容器 */
.wheel-container {
  position: relative;
  width: 500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  filter: drop-shadow(0 20px 40px rgba(0,0,0,0.15));
  transform-style: preserve-3d;
  transition: transform 0.5s ease;
}

.wheel-container:hover {
  transform: perspective(1000px) rotateX(5deg);
}

/* Canvas 转盘容器 */
.turntable-container {
  position: relative;
  width: 500px;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

/* Canvas 样式 */
canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-shadow: 
    0 10px 35px rgba(0, 0, 0, 0.15),
    0 20px 50px rgba(0, 0, 0, 0.1),
    inset 0 -5px 15px rgba(0, 0, 0, 0.1);
  border: 5px solid rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

/* 转盘指针 */
.pointer.right {
  right: -25px;
  top: 50%;
  transform: translateY(-50%);
  border-top: 15px solid transparent;
  border-bottom: 15px solid transparent;
  border-right: 40px solid #dc2626;
  position: absolute;
  z-index: 30;
}

/* 中心按钮 */
.center-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 
    0 5px 15px rgba(37, 99, 235, 0.3),
    0 2px 5px rgba(37, 99, 235, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  width: 100px; 
  height: 100px;
  z-index: 40;
}

.center-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.center-button:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translate(-50%, -50%) scale(1.05);
  box-shadow: 
    0 8px 20px rgba(37, 99, 235, 0.4),
    0 4px 10px rgba(37, 99, 235, 0.25);
}

.center-button:hover::before {
  left: 100%;
}

.center-button:active {
  transform: translate(-50%, -50%) scale(0.98);
  box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);
  transition: all 0.1s ease;
}

.center-button[disabled] {
  background: #94a3b8;
  cursor: not-allowed;
  transform: translate(-50%, -50%);
  box-shadow: none;
  opacity: 0.8;
}

.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  z-index: 1;
}

.spin-icon {
  font-size: 20px;
  color: #ffffff;
}

.button-text {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.spin-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 食物列表显示区域 */
.foods-display-section {
  margin-bottom: 40px;
  width: 100%;
  max-width: 1400px;
  padding: 0 20px;
  box-sizing: border-box;
  animation: fadeSlideUp 0.8s ease-out;
}

@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.foods-display-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 24px;
  padding: 32px;
  box-shadow:
    0 15px 40px rgba(0, 0, 0, 0.08),
    0 5px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.6);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.foods-display-card:hover {
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.1),
    0 10px 30px rgba(0, 0, 0, 0.05);
}

.foods-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1e293b;
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 24px 0;
  text-align: center;
  justify-content: center;
}

.foods-title .el-icon {
  color: #3b82f6;
  font-size: 24px;
}

.search-section {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.search-input {
  max-width: 400px;
  width: 100%;
}

.foods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  width: 100%;
}

.food-item {
  background: rgba(248, 250, 252, 0.9);
  border-radius: 16px;
  padding: 16px 12px;
  text-align: center;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  position: relative;
  overflow: hidden;
}

.food-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transform: translateX(-100%);
  transition: all 0.6s ease;
  z-index: 1;
}

.food-item:hover {
  background: rgba(241, 245, 249, 0.9);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border-color: rgba(226, 232, 240, 0.8);
}

.food-item:hover::before {
  transform: translateX(100%);
}

.food-item.selected {
  border-color: #3b82f6;
  background: rgba(219, 234, 254, 0.9);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
}

.food-item .food-emoji {
  font-size: 28px;
  margin-bottom: 10px;
  display: block;
  filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.1));
  transition: all 0.3s ease;
  transform-origin: center;
}

.food-item:hover .food-emoji {
  transform: scale(1.15);
}

.food-item .food-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 6px;
  line-height: 1.2;
  position: relative;
  z-index: 2;
}

.food-item .food-calories {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
  background: rgba(241, 245, 249, 0.7);
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  position: relative;
  z-index: 2;
}

.foods-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 16px;
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
}

.no-results-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-results-text {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #374151;
}

.no-results-tip {
  font-size: 14px;
  margin: 0 0 20px 0;
}

/* 悬浮弹窗遮罩层 */
.result-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.4s ease-out;
}

/* 悬浮弹窗主体 */
.result-modal {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  animation: modalSlideIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow:
    0 25px 80px rgba(0, 0, 0, 0.3),
    0 10px 40px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 弹窗内容区域 */
.result-content {
  padding: 48px;
  text-align: center;
  position: relative;
}

/* 弹窗装饰效果 */
.result-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
  border-radius: 24px 24px 0 0;
}

/* 弹窗动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 关闭按钮样式 */
.result-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 20;
}

.close-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  color: #6b7280;
  border: 1px solid rgba(229, 231, 235, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.close-button:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.3);
  transform: rotate(90deg) scale(1.1);
}

.result-emoji {
  font-size: 90px;
  margin-bottom: 24px;
  filter: drop-shadow(0 5px 15px rgba(0, 0, 0, 0.15));
  animation: bounceIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
  }
}

.result-title {
  font-size: 28px;
  color: #1e293b;
  margin: 0 0 20px 0;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.result-food {
  font-size: 36px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 20px 0;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.result-description {
  color: #64748b;
  margin: 0 0 24px 0;
  line-height: 1.7;
  font-size: 16px;
}

.food-details {
  background: rgba(248, 250, 252, 0.7);
  border-radius: 16px;
  padding: 24px;
  margin: 0 0 32px 0;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(5px);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(203, 213, 225, 0.5);
  margin-bottom: 0;
}

.detail-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #334155;
  font-size: 14px;
}

.detail-value {
  color: #0f172a;
  font-weight: 600;
  font-size: 14px;
  padding: 4px 12px;
  background: rgba(241, 245, 249, 0.7);
  border-radius: 20px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

/* PC端适配 */
@media (min-width: 1024px) {
  .food-wheel-container {
    padding: 40px;
  }

  .welcome-section {
    margin-bottom: 60px;
    padding: 0 40px;
  }

  .main-title {
    font-size: 68px;
    margin-bottom: 24px;
  }

  .subtitle {
    font-size: 24px;
    margin-bottom: 32px;
  }

  .turntable-container {
    width: 600px;
    height: 600px;
  }

  /* PC端特定的转盘设计调整 */
  canvas {
    border-width: 8px;
  }

  /* 指针在PC上调整 */
  .pointer.right {
    right: -30px;
    border-top: 18px solid transparent;
    border-bottom: 18px solid transparent;
    border-right: 50px solid #dc2626;
  }

  .pointer.right:before {
    width: 20px;
    height: 20px;
    top: -10px;
    left: 36px;
  }

  /* 按钮在大屏幕上调整 */
  .center-button {
    width: 120px;
    height: 120px;
    border-radius: 75px;
  }

  .spin-icon {
    font-size: 24px;
  }

  .button-text {
    font-size: 18px;
  }

  .result-modal {
    max-width: 700px;
  }

  .result-content {
    padding: 60px;
  }

  .result-emoji {
    font-size: 100px;
    margin-bottom: 32px;
  }

  .result-title {
    font-size: 32px;
    margin-bottom: 24px;
  }

  .result-food {
    font-size: 48px;
    margin-bottom: 24px;
  }

  .result-description {
    font-size: 18px;
    margin-bottom: 32px;
  }

  .food-details {
    padding: 28px;
    margin-bottom: 40px;
  }

  .foods-display-section {
    max-width: 1600px;
    padding: 0 40px;
  }

  .foods-display-card {
    padding: 40px;
  }

  .foods-title {
    font-size: 24px;
    margin-bottom: 32px;
  }

  .foods-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
  }

  .food-item {
    padding: 20px 16px;
    border-radius: 18px;
  }

  .food-item .food-emoji {
    font-size: 32px;
    margin-bottom: 12px;
  }

  .food-item .food-name {
    font-size: 16px;
    margin-bottom: 8px;
  }

  .food-item .food-calories {
    font-size: 14px;
    padding: 3px 10px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .food-wheel-container {
    padding: 16px;
  }

  .welcome-section {
    padding: 0 16px;
    margin-bottom: 32px;
  }

  .main-title {
    font-size: 32px;
  }

  .subtitle {
    font-size: 16px;
  }

  .wheel-section {
    margin-bottom: 32px;
  }

  .turntable-container {
    width: 320px;
    height: 320px;
  }

  /* 指针在移动端调整 */
  .pointer.right {
    right: -20px;
    border-top: 12px solid transparent;
    border-bottom: 12px solid transparent;
    border-right: 30px solid #dc2626;
  }
  
  .pointer.right:before {
    width: 12px;
    height: 12px;
    top: -6px;
    left: 22px;
  }

  .foods-display-section {
    padding: 0 16px;
  }

  .foods-display-card {
    padding: 24px;
    border-radius: 20px;
  }

  .foods-title {
    font-size: 18px;
    margin-bottom: 20px;
  }

  .foods-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .food-item {
    padding: 16px 12px;
    border-radius: 14px;
  }

  .food-item .food-emoji {
    font-size: 24px;
    margin-bottom: 8px;
  }

  .food-item .food-name {
    font-size: 13px;
    margin-bottom: 4px;
  }

  .food-item .food-calories {
    font-size: 11px;
    padding: 2px 6px;
  }

  .search-input {
    max-width: 100%;
  }

  .result-overlay {
    padding: 16px;
  }

  .result-modal {
    max-width: 100%;
    border-radius: 20px;
  }

  .result-content {
    padding: 32px 24px;
  }

  .result-close-btn {
    top: 12px;
    right: 12px;
  }

  .close-button {
    width: 32px;
    height: 32px;
  }

  .result-emoji {
    font-size: 64px;
    margin-bottom: 20px;
  }

  .result-title {
    font-size: 24px;
    margin-bottom: 16px;
  }

  .result-food {
    font-size: 28px;
    margin-bottom: 16px;
  }

  .result-actions {
    flex-direction: column;
    gap: 12px;
  }

  .result-actions .el-button {
    width: 100%;
  }

  .food-details {
    padding: 16px;
    margin-bottom: 24px;
  }

  .detail-item {
    padding: 8px 0;
  }

  .detail-label, .detail-value {
    font-size: 13px;
  }

  .center-button {
    width: 90px;
    height: 90px;
    border-radius: 45px;
    padding: 5px;
  }
  
  .button-text {
    font-size: 12px;
  }
}
</style>
