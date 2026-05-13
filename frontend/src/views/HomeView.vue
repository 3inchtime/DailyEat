<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon class="logo-icon"><Food /></el-icon>
          <span class="logo-text">今天吃什么？</span>
          <span class="subtitle">个人饮食助手</span>
        </div>

        <!-- 主导航菜单 -->
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          router
          class="main-nav"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/foods">
            <el-icon><Food /></el-icon>
            <span>食物库</span>
          </el-menu-item>
          <el-menu-item index="/meal-logs">
            <el-icon><Document /></el-icon>
            <span>用餐记录</span>
          </el-menu-item>
          <el-menu-item index="/stats">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据统计</span>
          </el-menu-item>
        </el-menu>

        <!-- 主题切换按钮 -->
        <div class="theme-toggle">
          <el-button 
            :icon="themeStore.isDark ? Sun : Moon" 
            @click="themeStore.toggleTheme"
            circle
            :type="themeStore.isDark ? 'warning' : 'primary'"
          />
        </div>

        <!-- 用户菜单 -->
        <div class="user-menu">
          <el-dropdown @command="handleCommand" trigger="hover">
            <span class="user-info">
              <el-avatar :size="32" class="user-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.userName }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人资料
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主内容区域 -->
    <el-main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { ElMessageBox } from 'element-plus'
import {
  User, ArrowDown, House, Food, Document, DataAnalysis, SwitchButton,
  Sun, Moon
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      authStore.logout()
      router.push('/login')
    })
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
}

.header {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 2px 20px 0 rgba(0, 0, 0, 0.06);
  height: 70px;
  padding: 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  color: #1e293b;
}

.logo-icon {
  font-size: 32px;
  margin-right: 12px;
  color: #3b82f6;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  margin-right: 12px;
  background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.main-nav {
  flex: 1;
  margin: 0 40px;
  background: transparent;
  border: none;
}

.main-nav .el-menu-item {
  color: #64748b;
  border-bottom: 2px solid transparent;
  font-size: 16px;
  font-weight: 500;
  height: 70px;
  line-height: 70px;
  margin: 0 8px;
  transition: all 0.3s ease;
}

.main-nav .el-menu-item:hover {
  color: #1e293b;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
}

.main-nav .el-menu-item.is-active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
  font-weight: 600;
}

.main-nav .el-menu-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.theme-toggle {
  margin-right: 16px;
}

.user-menu {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #1e293b;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid rgba(226, 232, 240, 0.6);
}

.user-info:hover {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.user-avatar {
  margin-right: 8px;
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  color: #475569;
}

.username {
  margin-right: 8px;
  font-weight: 500;
}

.dropdown-icon {
  font-size: 14px;
  transition: transform 0.3s;
}

.main-content {
  padding: 0;
  min-height: calc(100vh - 70px);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.content-wrapper {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 24px;
  box-sizing: border-box;
}

/* PC端专用设计 - 移除响应式断点 */
.header-content {
  width: 100%;
  padding: 0 24px;
}

.main-nav {
  margin: 0 24px;
}

.logo-text {
  font-size: 20px;
}

.subtitle {
  display: inline;
}

.main-nav .el-menu-item {
  font-size: 16px;
  margin: 0 8px;
}

.username {
  display: inline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 16px;
  }

  .header-content {
    padding: 0 16px;
  }

  .main-nav {
    margin: 0 16px;
  }

  .logo-text {
    font-size: 18px;
  }
}

@media (min-width: 1200px) {
  .content-wrapper {
    padding: 32px;
  }

  .header-content {
    padding: 0 32px;
  }

  .main-nav {
    margin: 0 32px;
  }
}

/* 暗黑模式样式 */
:global(.dark) .layout-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
}

:global(.dark) .header {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-bottom: 1px solid rgba(71, 85, 105, 0.6);
}

:global(.dark) .logo {
  color: #f1f5f9;
}

:global(.dark) .logo-text {
  background: linear-gradient(135deg, #f1f5f9 0%, #cbd5e1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:global(.dark) .subtitle {
  color: #94a3b8;
}

:global(.dark) .main-nav .el-menu-item {
  color: #94a3b8;
}

:global(.dark) .main-nav .el-menu-item:hover {
  color: #f1f5f9;
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
}

:global(.dark) .main-nav .el-menu-item.is-active {
  color: #60a5fa;
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
}

:global(.dark) .user-info {
  color: #f1f5f9;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border: 1px solid rgba(71, 85, 105, 0.6);
}

:global(.dark) .user-info:hover {
  background: linear-gradient(135deg, #334155 0%, #475569 100%);
}

:global(.dark) .user-avatar {
  background: linear-gradient(135deg, #475569 0%, #64748b 100%);
  color: #f1f5f9;
}
</style>
