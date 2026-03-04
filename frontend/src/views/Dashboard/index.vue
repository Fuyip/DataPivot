<template>
  <div class="dashboard">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>欢迎使用 DataPivot 数据情报分析系统</span>
        </div>
      </template>
      <div class="welcome-content">
        <h2>您好，{{ user?.full_name || user?.username }}！</h2>
        <p>当前角色：{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="系统用户" :value="0">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="数据记录" :value="0">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="分析报告" :value="0">
            <template #prefix>
              <el-icon><DataLine /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)
</script>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-content {
  padding: 20px 0;

  h2 {
    margin: 0 0 10px 0;
    font-size: 24px;
    color: #333;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: #666;
  }
}
</style>
