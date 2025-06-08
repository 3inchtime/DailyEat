<template>
  <div class="meal-logs-view">
    <div class="meal-logs-container">
      <!-- 页面头部 -->
      <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon><Document /></el-icon>
            用餐记录
          </h1>
          <p class="page-subtitle">记录和管理您的每日用餐情况，追踪饮食习惯</p>
        </div>
        <el-button type="primary" size="large" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加记录
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 筛选和统计区域 -->
      <el-card class="filter-card" shadow="never">
        <div class="filter-content">
          <el-row :gutter="24" align="middle">
            <el-col :span="6">
              <el-date-picker
                v-model="filterDate"
                type="date"
                placeholder="选择日期"
                @change="handleFilter"
                clearable
                size="large"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="filterMealType"
                placeholder="选择餐次"
                @change="handleFilter"
                clearable
                size="large"
                style="width: 100%"
              >
                <el-option label="早餐" value="早餐" />
                <el-option label="中餐" value="中餐" />
                <el-option label="下午茶" value="下午茶" />
                <el-option label="晚餐" value="晚餐" />
                <el-option label="夜宵" value="夜宵" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button size="large" @click="resetFilter">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-col>
            <el-col :span="8">
              <div class="stats-summary">
                <div class="stat-item">
                  <span class="stat-label">总记录数：</span>
                  <span class="stat-value">{{ mealLogs.length }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">今日热量：</span>
                  <span class="stat-value">{{ todayCalories }} kcal</span>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 用餐记录列表 -->
      <el-card class="table-card" shadow="never">
        <template #header>
          <div class="table-header">
            <h3>用餐记录列表</h3>
            <div class="table-actions">
              <el-button type="text" @click="fetchMealLogs()">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <el-table
          :data="mealLogs"
          :loading="loading"
          style="width: 100%"
          :row-style="{ height: '60px' }"
          :header-row-style="{ height: '50px' }"
          empty-text="暂无用餐记录"
        >
          <el-table-column label="食物信息" width="200">
            <template #default="scope">
              <div class="food-info">
                <div class="food-name">
                  <el-icon class="food-icon"><Food /></el-icon>
                  {{ scope.row.food_detail?.name || '未知食物' }}
                </div>
                <div class="food-desc">{{ scope.row.food_detail?.description || '无描述' }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="meal_type_recorded" label="餐次" width="120" align="center">
            <template #default="scope">
              <el-tag :type="getMealTypeColor(scope.row.meal_type_recorded)" size="large">
                {{ scope.row.meal_type_recorded }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="热量" width="120" align="center">
            <template #default="scope">
              <div class="calories-info">
                <span class="calories-value">{{ scope.row.food_detail?.calories || 0 }}</span>
                <span class="calories-unit">kcal</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="用餐时间" width="180" align="center">
            <template #default="scope">
              <div class="time-info">
                <div class="date">{{ formatDate(scope.row.eaten_at_datetime) }}</div>
                <div class="time">{{ formatTime(scope.row.eaten_at_datetime) }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="notes" label="备注" min-width="200" show-overflow-tooltip>
            <template #default="scope">
              <span class="notes-text">{{ scope.row.notes || '无备注' }}</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" align="center">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="editMealLog(scope.row)"
                plain
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteMealLog(scope.row)"
                plain
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    </div>

    <!-- 添加/编辑用餐记录对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用餐记录' : '添加用餐记录'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="mealLogFormRef"
        :model="mealLogForm"
        :rules="mealLogRules"
        label-width="100px"
      >
        <el-form-item label="选择食物" prop="food_id">
          <el-select
            v-model="mealLogForm.food_id"
            placeholder="请选择食物"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="food in availableFoods"
              :key="food.food_id"
              :label="`${food.name} (${food.calories || 0} kcal)`"
              :value="food.food_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="餐次" prop="meal_type_recorded">
          <el-select
            v-model="mealLogForm.meal_type_recorded"
            placeholder="请选择餐次"
            style="width: 100%"
          >
            <el-option label="早餐" value="早餐" />
            <el-option label="中餐" value="中餐" />
            <el-option label="下午茶" value="下午茶" />
            <el-option label="晚餐" value="晚餐" />
            <el-option label="夜宵" value="夜宵" />
          </el-select>
        </el-form-item>

        <el-form-item label="用餐时间" prop="eaten_at_datetime">
          <el-date-picker
            v-model="mealLogForm.eaten_at_datetime"
            type="datetime"
            placeholder="选择用餐时间"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="mealLogForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveMealLog">
            {{ isEdit ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useFoodsStore } from '@/stores/foods'
import { mealLogsAPI } from '@/api/mealLogs'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Document, Refresh, Food, Edit, Delete
} from '@element-plus/icons-vue'

const foodsStore = useFoodsStore()

const mealLogs = ref([])
const availableFoods = ref([])
const loading = ref(false)
const filterDate = ref('')
const filterMealType = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const mealLogFormRef = ref()

const mealLogForm = reactive({
  food_id: null,
  meal_type_recorded: '',
  eaten_at_datetime: new Date(),
  notes: ''
})

const mealLogRules = {
  food_id: [
    { required: true, message: '请选择食物', trigger: 'change' }
  ],
  meal_type_recorded: [
    { required: true, message: '请选择餐次', trigger: 'change' }
  ],
  eaten_at_datetime: [
    { required: true, message: '请选择用餐时间', trigger: 'change' }
  ]
}

// 计算今日热量
const todayCalories = computed(() => {
  const today = new Date().toDateString()
  return mealLogs.value
    .filter(log => new Date(log.eaten_at_datetime).toDateString() === today)
    .reduce((total, log) => total + (log.food_detail?.calories || 0), 0)
})

const fetchMealLogs = async (params = {}) => {
  loading.value = true
  try {
    const response = await mealLogsAPI.getMealLogs(params)
    mealLogs.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取用餐记录失败')
    console.error('Fetch meal logs error:', error)
  } finally {
    loading.value = false
  }
}

const fetchAvailableFoods = async () => {
  await foodsStore.fetchFoods()
  availableFoods.value = foodsStore.foods
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editMealLog = (log) => {
  isEdit.value = true
  Object.assign(mealLogForm, {
    log_id: log.log_id,
    food_id: log.food_detail?.food_id,
    meal_type_recorded: log.meal_type_recorded,
    eaten_at_datetime: new Date(log.eaten_at_datetime),
    notes: log.notes || ''
  })
  dialogVisible.value = true
}

const deleteMealLog = (log) => {
  ElMessageBox.confirm(
    '确定要删除这条用餐记录吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await mealLogsAPI.deleteMealLog(log.log_id)
      ElMessage.success('删除成功！')
      fetchMealLogs()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const saveMealLog = async () => {
  if (!mealLogFormRef.value) return
  
  await mealLogFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const formData = {
          ...mealLogForm,
          eaten_at_datetime: mealLogForm.eaten_at_datetime.toISOString()
        }
        
        if (isEdit.value) {
          await mealLogsAPI.updateMealLog(mealLogForm.log_id, formData)
          ElMessage.success('更新成功！')
        } else {
          await mealLogsAPI.createMealLog(formData)
          ElMessage.success('添加成功！')
        }
        
        dialogVisible.value = false
        resetForm()
        fetchMealLogs()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
      }
    }
  })
}

const resetForm = () => {
  Object.assign(mealLogForm, {
    food_id: null,
    meal_type_recorded: '',
    eaten_at_datetime: new Date(),
    notes: ''
  })
}

const handleFilter = () => {
  const params = {}
  if (filterDate.value) {
    params.date = filterDate.value.toISOString().split('T')[0]
  }
  if (filterMealType.value) {
    params.meal_type_recorded = filterMealType.value
  }
  fetchMealLogs(params)
}

const resetFilter = () => {
  filterDate.value = ''
  filterMealType.value = ''
  fetchMealLogs()
}

const formatDateTime = (dateTime) => {
  return new Date(dateTime).toLocaleString('zh-CN')
}

const formatDate = (dateTime) => {
  return new Date(dateTime).toLocaleDateString('zh-CN')
}

const formatTime = (dateTime) => {
  return new Date(dateTime).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getMealTypeColor = (mealType) => {
  const colors = {
    '早餐': 'warning',
    '中餐': 'success',
    '下午茶': 'info',
    '晚餐': 'primary',
    '夜宵': 'danger'
  }
  return colors[mealType] || 'info'
}

onMounted(() => {
  fetchMealLogs()
  fetchAvailableFoods()
})
</script>

<style scoped>
.meal-logs-view {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  min-height: 100%;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.meal-logs-container {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  gap: 24px;
}

.filter-card {
  border-radius: 16px;
  border: none;
}

.filter-content {
  padding: 8px 0;
}

.stats-summary {
  display: flex;
  gap: 24px;
  justify-content: flex-end;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  color: #409eff;
  font-weight: 600;
  font-size: 16px;
}

/* 表格卡片 */
.table-card {
  border-radius: 16px;
  border: none;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 8px;
}

/* 表格内容样式 */
.food-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.food-name {
  display: flex;
  align-items: center;
  font-weight: 500;
  color: #303133;
}

.food-icon {
  margin-right: 8px;
  color: #409eff;
  font-size: 16px;
}

.food-desc {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.calories-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.calories-value {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
}

.calories-unit {
  font-size: 12px;
  color: #909399;
}

.time-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.date {
  font-weight: 500;
  color: #303133;
}

.time {
  font-size: 12px;
  color: #909399;
}

.notes-text {
  color: #606266;
  font-size: 14px;
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

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 16px;
}

:deep(.el-dialog__header) {
  background: #f8f9fa;
  border-radius: 16px 16px 0 0;
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .meal-logs-container {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .page-title {
    font-size: 24px;
  }

  .stats-summary {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

@media (min-width: 1200px) {
  .meal-logs-container {
    padding: 32px;
  }

  .header-content {
    padding: 40px;
  }
}

/* 表单样式 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
}

/* PC端专用设计 - 移除响应式断点 */
.meal-logs-view {
  min-width: 1024px;
  padding: 24px;
}

.header-content {
  flex-direction: row;
  align-items: center;
  gap: 24px;
  padding: 32px;
}

.page-title {
  font-size: 28px;
}

.page-title .el-icon {
  font-size: 32px;
}

.page-subtitle {
  font-size: 16px;
}

.stats-summary {
  justify-content: center;
  flex-direction: row;
  gap: 24px;
}

/* 确保表格在PC端正常显示 */
:deep(.el-table__header) {
  display: table-header-group;
}

:deep(.el-table__body) {
  display: table-row-group;
}

:deep(.el-table__row) {
  display: table-row;
  border: none;
  border-radius: 0;
  margin-bottom: 0;
  padding: 0;
}

:deep(.el-table__cell) {
  display: table-cell;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 0;
}
</style>
