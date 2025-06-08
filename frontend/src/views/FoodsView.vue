<template>
  <div class="foods-view">
    <div class="foods-container">
      <!-- 页面头部 -->
      <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon><Food /></el-icon>
            食物库管理
          </h1>
          <p class="page-subtitle">管理您的个人食物库，添加、编辑和组织您的食物</p>
        </div>
        <el-button type="primary" size="large" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加食物
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-section">
      <!-- 搜索和筛选区域 -->
      <el-card class="filter-card" shadow="never">
        <div class="filter-content">

          <el-row :gutter="24" align="middle">
            <el-col :span="8">
              <el-input
                v-model="searchText"
                placeholder="搜索食物名称、描述或标签..."
                :prefix-icon="Search"
                @input="handleSearch"
                clearable
                size="large"
              />
            </el-col>
            <el-col :span="6">
              <el-select
                v-model="selectedMealType"
                placeholder="选择餐次"
                @change="handleSearch"
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
              <el-button size="large" @click="resetSearch">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-col>
            <el-col :span="6">
              <div class="stats-info">
                <span class="stats-text">共 {{ foodsStore.totalFoods }} 个食物</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 食物列表 -->
      <el-card class="table-card" shadow="never">
        <el-table
          :data="foodsStore.foods"
          :loading="foodsStore.loading"
          style="width: 100%"
          :row-style="{ height: '60px' }"
          :header-row-style="{ height: '50px' }"
        >
          <el-table-column prop="name" label="食物名称" width="180" show-overflow-tooltip>
            <template #default="scope">
              <div class="food-name">
                <el-icon class="food-icon"><Food /></el-icon>
                <span>{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="calories" label="热量" width="120" align="center">
            <template #default="scope">
              <el-tag type="info" size="large">
                {{ scope.row.calories || 0 }} kcal
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="适用餐次" width="240">
            <template #default="scope">
              <div class="meal-tags">
                <el-tag
                  v-for="mealType in scope.row.meal_types"
                  :key="mealType"
                  :type="getMealTypeColor(mealType)"
                  size="small"
                  class="meal-tag"
                >
                  {{ mealType }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="tags" label="标签" width="180" show-overflow-tooltip>
            <template #default="scope">
              <span class="tags-text">{{ scope.row.tags || '无标签' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center">
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click="editFood(scope.row)"
                plain
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteFood(scope.row)"
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

    <!-- 添加/编辑食物对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑食物' : '添加食物'"
      width="600px"
    >
      <el-form
        ref="foodFormRef"
        :model="foodForm"
        :rules="foodRules"
        label-width="100px"
      >
        <el-form-item label="食物名称" prop="name">
          <el-input v-model="foodForm.name" placeholder="请输入食物名称" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="foodForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入食物描述、做法等"
          />
        </el-form-item>

        <el-form-item label="热量" prop="calories">
          <el-input-number
            v-model="foodForm.calories"
            :min="0"
            :max="10000"
            placeholder="请输入热量(kcal)"
          />
        </el-form-item>

        <el-form-item label="适用餐次">
          <el-checkbox-group v-model="selectedMealTypes">
            <el-checkbox label="is_for_breakfast">早餐</el-checkbox>
            <el-checkbox label="is_for_lunch">中餐</el-checkbox>
            <el-checkbox label="is_for_afternoon_tea">下午茶</el-checkbox>
            <el-checkbox label="is_for_dinner">晚餐</el-checkbox>
            <el-checkbox label="is_for_supper">夜宵</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="标签" prop="tags">
          <el-input
            v-model="foodForm.tags"
            placeholder="请输入标签，用逗号分隔"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveFood">
            {{ isEdit ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useFoodsStore } from '@/stores/foods'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Food, Refresh, Edit, Delete } from '@element-plus/icons-vue'

const foodsStore = useFoodsStore()

const searchText = ref('')
const selectedMealType = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const foodFormRef = ref()

const foodForm = reactive({
  name: '',
  description: '',
  calories: null,
  tags: ''
})

const selectedMealTypes = ref([])

const foodRules = {
  name: [
    { required: true, message: '请输入食物名称', trigger: 'blur' }
  ]
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editFood = (food) => {
  isEdit.value = true
  Object.assign(foodForm, {
    food_id: food.food_id,
    name: food.name,
    description: food.description || '',
    calories: food.calories,
    tags: food.tags || ''
  })
  
  // 设置餐次选择
  selectedMealTypes.value = []
  if (food.is_for_breakfast) selectedMealTypes.value.push('is_for_breakfast')
  if (food.is_for_lunch) selectedMealTypes.value.push('is_for_lunch')
  if (food.is_for_afternoon_tea) selectedMealTypes.value.push('is_for_afternoon_tea')
  if (food.is_for_dinner) selectedMealTypes.value.push('is_for_dinner')
  if (food.is_for_supper) selectedMealTypes.value.push('is_for_supper')
  
  dialogVisible.value = true
}

const deleteFood = (food) => {
  ElMessageBox.confirm(
    `确定要删除食物"${food.name}"吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    await foodsStore.deleteFood(food.food_id)
  })
}

const saveFood = async () => {
  if (!foodFormRef.value) return
  
  await foodFormRef.value.validate(async (valid) => {
    if (valid) {
      const formData = {
        ...foodForm,
        is_for_breakfast: selectedMealTypes.value.includes('is_for_breakfast'),
        is_for_lunch: selectedMealTypes.value.includes('is_for_lunch'),
        is_for_afternoon_tea: selectedMealTypes.value.includes('is_for_afternoon_tea'),
        is_for_dinner: selectedMealTypes.value.includes('is_for_dinner'),
        is_for_supper: selectedMealTypes.value.includes('is_for_supper')
      }
      
      let success = false
      if (isEdit.value) {
        success = await foodsStore.updateFood(foodForm.food_id, formData)
      } else {
        success = await foodsStore.createFood(formData)
      }
      
      if (success) {
        dialogVisible.value = false
        resetForm()
      }
    }
  })
}

const resetForm = () => {
  Object.assign(foodForm, {
    name: '',
    description: '',
    calories: null,
    tags: ''
  })
  selectedMealTypes.value = []
}

const handleSearch = () => {
  const params = {}
  if (searchText.value) {
    params.search = searchText.value
  }
  if (selectedMealType.value) {
    params.meal_type = selectedMealType.value
  }
  foodsStore.fetchFoods(params)
}

const resetSearch = () => {
  searchText.value = ''
  selectedMealType.value = ''
  foodsStore.fetchFoods()
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
  foodsStore.fetchFoods()
})
</script>

<style scoped>
.foods-view {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  min-height: 100%;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.foods-container {
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

.stats-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.stats-text {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

/* 表格卡片 */
.table-card {
  border-radius: 16px;
  border: none;
}

/* 表格内容样式 */
.food-name {
  display: flex;
  align-items: center;
}

.food-icon {
  margin-right: 8px;
  color: #409eff;
  font-size: 16px;
}

.meal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.meal-tag {
  margin: 0;
}

.tags-text {
  color: #909399;
  font-size: 13px;
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
  .foods-container {
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

  .page-title .el-icon {
    font-size: 28px;
  }
}

@media (min-width: 1200px) {
  .foods-container {
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
.foods-view {
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
