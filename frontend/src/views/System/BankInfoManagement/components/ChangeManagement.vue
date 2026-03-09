<template>
  <div class="change-management">
    <!-- 待审批列表（仅超级管理员可见） -->
    <div v-if="isSuperAdmin" class="pending-section">
      <h3>待审批申请</h3>
      <el-table :data="pendingData" style="width: 100%; margin-top: 10px" v-loading="pendingLoading">
        <el-table-column prop="id" label="申请ID" width="80" />
        <el-table-column prop="table_type" label="表类型" width="120">
          <template #default="{ row }">
            {{ row.table_type === 'bank_bin' ? 'BIN码库' : '银行映射' }}
          </template>
        </el-table-column>
        <el-table-column prop="change_type" label="变更类型" width="100">
          <template #default="{ row }">
            {{ getChangeTypeLabel(row.change_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="申请人" width="120" />
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column prop="reason" label="变更原因" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" @click="handleApprove(row)">批准</el-button>
            <el-button link type="danger" @click="handleReject(row)">拒绝</el-button>
            <el-button link type="primary" @click="handleViewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pendingPagination.page"
        v-model:page-size="pendingPagination.page_size"
        :total="pendingPagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadPendingData"
        @current-change="loadPendingData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <el-divider v-if="isSuperAdmin" />

    <!-- 变更历史 -->
    <div class="history-section">
      <h3>变更历史</h3>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px">
            <el-option label="待审批" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已执行" value="executed" />
          </el-select>
        </el-form-item>
        <el-form-item label="表类型">
          <el-select v-model="searchForm.table_type" placeholder="请选择" clearable style="width: 120px">
            <el-option label="BIN码库" value="bank_bin" />
            <el-option label="银行映射" value="sy_bank" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更类型">
          <el-select v-model="searchForm.change_type" placeholder="请选择" clearable style="width: 120px">
            <el-option label="新增" value="create" />
            <el-option label="修改" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="historyData" style="width: 100%; margin-top: 10px" v-loading="historyLoading">
        <el-table-column prop="id" label="申请ID" width="80" />
        <el-table-column prop="table_type" label="表类型" width="120">
          <template #default="{ row }">
            {{ row.table_type === 'bank_bin' ? 'BIN码库' : '银行映射' }}
          </template>
        </el-table-column>
        <el-table-column prop="change_type" label="变更类型" width="100">
          <template #default="{ row }">
            {{ getChangeTypeLabel(row.change_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="creator_name" label="申请人" width="120" />
        <el-table-column prop="reviewer_name" label="审批人" width="120" />
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending' && row.created_by === currentUserId"
              link
              type="danger"
              @click="handleCancel(row)"
            >
              撤销
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="historyPagination.page"
        v-model:page-size="historyPagination.page_size"
        :total="historyPagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadHistoryData"
        @current-change="loadHistoryData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="变更详情" width="800px">
      <el-descriptions :column="2" border v-if="currentDetail">
        <el-descriptions-item label="申请ID">{{ currentDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="表类型">
          {{ currentDetail.table_type === 'bank_bin' ? 'BIN码库' : '银行映射' }}
        </el-descriptions-item>
        <el-descriptions-item label="变更类型">
          {{ getChangeTypeLabel(currentDetail.change_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDetail.status)">
            {{ getStatusLabel(currentDetail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentDetail.creator_name }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ currentDetail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="审批人" v-if="currentDetail.reviewer_name">
          {{ currentDetail.reviewer_name }}
        </el-descriptions-item>
        <el-descriptions-item label="审批时间" v-if="currentDetail.reviewed_at">
          {{ currentDetail.reviewed_at }}
        </el-descriptions-item>
        <el-descriptions-item label="变更原因" :span="2">
          {{ currentDetail.reason || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="审批意见" :span="2" v-if="currentDetail.review_comment">
          {{ currentDetail.review_comment }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider>数据对比</el-divider>

      <el-row :gutter="20">
        <el-col :span="12" v-if="currentDetail && currentDetail.old_data">
          <h4>原始数据</h4>
          <pre>{{ formatJson(currentDetail.old_data) }}</pre>
        </el-col>
        <el-col :span="currentDetail && currentDetail.old_data ? 12 : 24">
          <h4>{{ currentDetail && currentDetail.change_type === 'delete' ? '删除数据' : '新数据' }}</h4>
          <pre>{{ formatJson(currentDetail?.new_data) }}</pre>
        </el-col>
      </el-row>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog v-model="reviewVisible" :title="reviewTitle" width="500px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审批意见">
          <el-input
            v-model="reviewForm.review_comment"
            type="textarea"
            :rows="4"
            placeholder="请输入审批意见（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="handleReviewSubmit" :loading="reviewLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, defineExpose } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  getChangeRequests,
  approveChangeRequest,
  rejectChangeRequest,
  deleteChangeRequest
} from '@/api/bankInfo'

const props = defineProps({
  userRole: {
    type: String,
    default: 'user'
  }
})

const authStore = useAuthStore()
const isSuperAdmin = computed(() => props.userRole === 'super_admin')
const currentUserId = computed(() => authStore.user?.id)

// 待审批数据
const pendingData = ref([])
const pendingLoading = ref(false)
const pendingPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 历史数据
const historyData = ref([])
const historyLoading = ref(false)
const historyPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  status: '',
  table_type: '',
  change_type: ''
})

// 详情对话框
const detailVisible = ref(false)
const currentDetail = ref(null)

// 审批对话框
const reviewVisible = ref(false)
const reviewTitle = ref('')
const reviewForm = reactive({
  review_comment: ''
})
const reviewLoading = ref(false)
const currentReviewId = ref(null)
const currentReviewAction = ref('')

// 获取变更类型标签
const getChangeTypeLabel = (type) => {
  const map = {
    create: '新增',
    update: '修改',
    delete: '删除'
  }
  return map[type] || type
}

// 获取状态标签
const getStatusLabel = (status) => {
  const map = {
    pending: '待审批',
    approved: '已批准',
    rejected: '已拒绝',
    executed: '已执行'
  }
  return map[status] || status
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    executed: 'info'
  }
  return map[status] || ''
}

// 格式化 JSON
const formatJson = (jsonStr) => {
  try {
    const obj = JSON.parse(jsonStr)
    return JSON.stringify(obj, null, 2)
  } catch {
    return jsonStr
  }
}

// 加载待审批数据
const loadPendingData = async () => {
  if (!isSuperAdmin.value) return

  pendingLoading.value = true
  try {
    const params = {
      page: pendingPagination.page,
      page_size: pendingPagination.page_size,
      status: 'pending'
    }
    const res = await getChangeRequests(params)
    pendingData.value = res.items || []
    pendingPagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载待审批数据失败')
  } finally {
    pendingLoading.value = false
  }
}

// 加载历史数据
const loadHistoryData = async () => {
  historyLoading.value = true
  try {
    const params = {
      page: historyPagination.page,
      page_size: historyPagination.page_size,
      ...searchForm
    }
    const res = await getChangeRequests(params)
    historyData.value = res.items || []
    historyPagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载历史数据失败')
  } finally {
    historyLoading.value = false
  }
}

// 加载所有数据
const loadData = () => {
  if (isSuperAdmin.value) {
    loadPendingData()
  }
  loadHistoryData()
}

// 搜索
const handleSearch = () => {
  historyPagination.page = 1
  loadHistoryData()
}

// 重置
const handleReset = () => {
  searchForm.status = ''
  searchForm.table_type = ''
  searchForm.change_type = ''
  handleSearch()
}

// 查看详情
const handleViewDetail = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}

// 批准
const handleApprove = (row) => {
  currentReviewId.value = row.id
  currentReviewAction.value = 'approve'
  reviewTitle.value = '批准变更申请'
  reviewForm.review_comment = ''
  reviewVisible.value = true
}

// 拒绝
const handleReject = (row) => {
  currentReviewId.value = row.id
  currentReviewAction.value = 'reject'
  reviewTitle.value = '拒绝变更申请'
  reviewForm.review_comment = ''
  reviewVisible.value = true
}

// 提交审批
const handleReviewSubmit = async () => {
  reviewLoading.value = true
  try {
    const data = {
      review_comment: reviewForm.review_comment
    }

    if (currentReviewAction.value === 'approve') {
      await approveChangeRequest(currentReviewId.value, data)
      ElMessage.success('审批通过，变更已执行')
    } else {
      await rejectChangeRequest(currentReviewId.value, data)
      ElMessage.success('已拒绝变更申请')
    }

    reviewVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    reviewLoading.value = false
  }
}

// 撤销申请
const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要撤销这个变更申请吗?', '提示', {
      type: 'warning'
    })

    await deleteChangeRequest(row.id)
    ElMessage.success('变更申请已撤销')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('撤销失败')
    }
  }
}

// 暴露方法给父组件
defineExpose({
  loadData
})

// 初始加载
loadData()
</script>

<style scoped>
.change-management {
  padding: 20px;
}

.pending-section,
.history-section {
  margin-bottom: 20px;
}

.search-form {
  margin-top: 10px;
  margin-bottom: 10px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
