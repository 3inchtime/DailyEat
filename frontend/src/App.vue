<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: #f0f2f5;
  color: #1e293b;
  transition: background-color 0.3s ease, color 0.3s ease;
}

#app {
  height: 100vh;
}

/* 暗黑模式全局样式 */
.dark body {
  background-color: #0f172a;
  color: #f1f5f9;
}

/* Element Plus 暗黑模式覆盖 */
.dark .el-button--primary {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.dark .el-button--primary:hover {
  background-color: #2563eb;
  border-color: #2563eb;
}

.dark .el-button--warning {
  background-color: #f59e0b;
  border-color: #f59e0b;
}

.dark .el-button--warning:hover {
  background-color: #d97706;
  border-color: #d97706;
}

.dark .el-card {
  background-color: #1e293b;
  border-color: #334155;
}

.dark .el-dialog {
  background-color: #1e293b;
}

.dark .el-dialog__title {
  color: #f1f5f9;
}

.dark .el-message-box {
  background-color: #1e293b;
}

.dark .el-message-box__title {
  color: #f1f5f9;
}

.dark .el-message-box__message {
  color: #94a3b8;
}

.dark .el-dropdown-menu {
  background-color: #1e293b;
  border-color: #334155;
}

.dark .el-dropdown-menu__item {
  color: #f1f5f9;
}

.dark .el-dropdown-menu__item:hover {
  background-color: #334155;
}
</style>
