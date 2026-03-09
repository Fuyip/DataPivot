<template>
  <div class="bank-card-match-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><CreditCard /></el-icon>
            银行卡归属批量查询
          </span>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：输入区域 -->
        <el-col :span="10">
          <div class="input-section">
            <div class="section-title">输入银行卡号（每行一个）</div>
            <el-input
              v-model="cardNumbersText"
              type="textarea"
              :rows="15"
              placeholder="请输入银行卡号，每行一个&#10;例如：&#10;6222021234567890123&#10;6228481234567890123"
            />
            <div class="action-buttons">
              <el-button type="primary" @click="handleMatch" :loading="loading">
                <el-icon><Search /></el-icon>
                开始匹配
              </el-button>
              <el-button @click="handleClear">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>
          </div>
        </el-col>

        <!-- 右侧：结果展示 -->
        <el-col :span="14">
          <div class="result-section">
            <div class="section-title">
              匹配结果
              <el-button
                v-if="matchResults.length > 0"
                type="success"
                size="small"
                @click="handleExport"
                :loading="exporting"
              >
                <el-icon><Download /></el-icon>
                导出Excel
              </el-button>
            </div>

            <el-table
              v-loading="loading"
              :data="matchResults"
              border
              stripe
              max-height="500"
            >
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="card_no" label="银行卡号" width="200" />
              <el-table-column prop="bank_name" label="银行名称" min-width="150">
                <template #default="{ row }">
                  <span v-if="row.matched">{{ row.bank_name }}</span>
                  <el-tag v-else type="warning" size="small">未匹配</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="matched" label="匹配状态" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.matched" type="success" size="small">已匹配</el-tag>
                  <el-tag v-else type="info" size="small">未匹配</el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="matchResults.length > 0" class="result-summary">
              <el-statistic title="总数" :value="matchResults.length" />
              <el-statistic title="已匹配" :value="matchedCount" />
              <el-statistic title="未匹配" :value="unmatchedCount" />
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { CreditCard, Search, Delete, Download } from '@element-plus/icons-vue'
import { batchMatchBanks, exportMatchResult } from '@/api/bankCard'

const cardNumbersText = ref('')
const matchResults = ref([])
const loading = ref(false)
const exporting = ref(false)

const matchedCount = computed(() => {
  return matchResults.value.filter(r => r.matched).length
})

const unmatchedCount = computed(() => {
  return matchResults.value.filter(r => !r.matched).length
})

const handleMatch = async () => {
  const lines = cardNumbersText.value.split('\n')
  const cardNumbers = lines
    .map(line => line.trim())
    .filter(line => line.length > 0)

  if (cardNumbers.length === 0) {
    ElMessage.warning('请输入至少一个银行卡号')
    return
  }

  if (cardNumbers.length > 100) {
    ElMessage.warning('单次最多只能查询100个银行卡号')
    return
  }

  loading.value = true
  try {
    const data = await batchMatchBanks(cardNumbers)
    console.log('API返回数据:', data)
    console.log('数据类型:', typeof data)
    console.log('是否为数组:', Array.isArray(data))
    matchResults.value = data
    ElMessage.success(`匹配完成！已匹配 ${matchedCount.value} 个，未匹配 ${unmatchedCount.value} 个`)
  } catch (error) {
    console.error('匹配错误:', error)
    ElMessage.error('匹配失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  const lines = cardNumbersText.value.split('\n')
  const cardNumbers = lines
    .map(line => line.trim())
    .filter(line => line.length > 0)

  exporting.value = true
  try {
    const blob = await exportMatchResult(cardNumbers)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `银行卡匹配结果_${new Date().getTime()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败：' + (error.message || '未知错误'))
  } finally {
    exporting.value = false
  }
}

const handleClear = () => {
  cardNumbersText.value = ''
  matchResults.value = []
}
</script>

<style scoped>
.bank-card-match-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  font-size: 14px;
  color: #606266;
}

.input-section {
  height: 100%;
}

.action-buttons {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

.result-section {
  height: 100%;
}

.result-summary {
  margin-top: 20px;
  display: flex;
  gap: 40px;
  justify-content: center;
}
</style>
