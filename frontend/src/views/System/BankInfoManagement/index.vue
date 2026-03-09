<template>
  <div class="bank-info-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>银行信息管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- BIN 码管理 -->
        <el-tab-pane label="BIN 码管理" name="bank_bin">
          <BankBinManagement ref="bankBinRef" :user-role="userRole" />
        </el-tab-pane>

        <!-- 银行名称映射 -->
        <el-tab-pane label="银行名称映射" name="sy_bank">
          <SyBankManagement ref="syBankRef" :user-role="userRole" />
        </el-tab-pane>

        <!-- 变更管理 -->
        <el-tab-pane label="变更管理" name="changes">
          <ChangeManagement ref="changeRef" :user-role="userRole" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import BankBinManagement from './components/BankBinManagement.vue'
import SyBankManagement from './components/SyBankManagement.vue'
import ChangeManagement from './components/ChangeManagement.vue'

const authStore = useAuthStore()
const activeTab = ref('bank_bin')

const bankBinRef = ref(null)
const syBankRef = ref(null)
const changeRef = ref(null)

const userRole = computed(() => authStore.user?.role || 'user')

const handleTabChange = (tabName) => {
  // 切换 Tab 时可以刷新数据
  if (tabName === 'bank_bin' && bankBinRef.value) {
    bankBinRef.value.loadData()
  } else if (tabName === 'sy_bank' && syBankRef.value) {
    syBankRef.value.loadData()
  } else if (tabName === 'changes' && changeRef.value) {
    changeRef.value.loadData()
  }
}

onMounted(() => {
  // 初始加载
})
</script>

<style scoped>
.bank-info-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
