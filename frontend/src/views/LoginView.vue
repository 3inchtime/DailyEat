<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>今天吃什么？</h2>
          <p>个人饮食助手</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="authStore.loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="login-footer">
            <span>还没有账号？</span>
            <el-link type="primary" @click="$router.push('/register')">
              立即注册
            </el-link>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      console.log('开始登录...')
      const success = await authStore.login(loginForm)
      console.log('登录结果:', success)
      console.log('认证状态:', authStore.isAuthenticated)

      if (success) {
        console.log('登录成功，准备跳转到首页')
        // 确保状态已经更新后再跳转
        await nextTick()

        // 使用replace而不是push，避免用户按返回键回到登录页
        try {
          await router.replace('/')
          console.log('跳转到首页成功')
        } catch (routerError) {
          console.error('路由跳转失败:', routerError)
          // 如果路由跳转失败，尝试强制刷新页面
          window.location.href = '/'
        }
      } else {
        console.log('登录失败')
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border-radius: 20px;
  overflow: hidden;
  background: white;
}

.card-header {
  text-align: center;
  padding: 20px 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.card-header h2 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.card-header p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.login-footer {
  text-align: center;
  width: 100%;
  margin-top: 16px;
}

.login-footer span {
  color: #909399;
  font-size: 14px;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  height: 44px;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(30, 41, 59, 0.3);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #334155 0%, #64748b 100%);
  box-shadow: 0 6px 16px rgba(30, 41, 59, 0.4);
}

/* PC端专用设计 - 移除响应式断点 */
.login-container {
  min-width: 1024px;
  padding: 20px;
}

.login-card {
  max-width: 450px; /* 保持合适的登录卡片宽度 */
}

.card-header h2 {
  font-size: 28px;
}

.card-header p {
  font-size: 16px;
}
</style>
