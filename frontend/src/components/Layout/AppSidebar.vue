<template>
  <div class="app-sidebar">
    <div class="logo-container">
      <h2>DataPivot</h2>
    </div>

    <el-menu
      :default-active="activeMenu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409eff"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><DataLine /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/system/bank-statements">
        <el-icon><Upload /></el-icon>
        <span>银行流水上传</span>
      </el-menu-item>

      <el-menu-item index="/bank-card-match">
        <el-icon><CreditCard /></el-icon>
        <span>银行卡归属查询</span>
      </el-menu-item>

      <el-sub-menu index="system" v-if="isAdmin">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="/system/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/system/cases">
          <el-icon><FolderOpened /></el-icon>
          <span>案件管理</span>
        </el-menu-item>
        <el-menu-item index="/system/import-rules">
          <el-icon><Setting /></el-icon>
          <span>导入规则管理</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)
const isAdmin = computed(() => authStore.isAdmin)
</script>

<style scoped lang="scss">
.app-sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;

  .logo-container {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    h2 {
      margin: 0;
      font-size: 20px;
      color: #fff;
      font-weight: 600;
    }
  }

  .el-menu {
    border-right: none;
    flex: 1;
  }
}
</style>
