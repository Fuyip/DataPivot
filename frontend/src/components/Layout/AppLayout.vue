<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside width="200px">
      <AppSidebar />
    </el-aside>

    <!-- 主区域 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header height="60px">
        <AppHeader />
      </el-header>

      <!-- 内容区 -->
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.el-main {
  background-color: #f0f2f5;
  padding: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
