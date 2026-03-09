<template>
  <div class="bank-statement-page">
    <!-- 顶部案件选择 -->
    <el-card class="case-selector-card">
      <el-form :inline="true">
        <el-form-item label="选择案件">
          <el-select
            v-model="selectedCaseId"
            placeholder="请选择案件"
            filterable
            style="width: 400px"
            @change="handleCaseChange"
          >
            <el-option
              v-for="item in caseList"
              :key="item.id"
              :label="`${item.case_name} (${item.case_code})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-tag v-if="selectedCase" type="info">
            权限: {{ getPermissionLabel(selectedCase.user_permission) }}
          </el-tag>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 提示：未选择案件 -->
    <el-empty
      v-if="!selectedCaseId"
      description="请先选择一个案件"
      style="margin-top: 40px"
    />

    <!-- 主内容区域 -->
    <div v-else class="content-area">
      <!-- 银行流水上传卡片 -->
      <el-card class="section-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">
              <el-icon><Upload /></el-icon>
              银行流水上传
            </span>
            <el-button
              type="primary"
              size="small"
              @click="showUploadDialog"
              :disabled="!canUpload"
            >
              <el-icon><Upload /></el-icon>
              上传流水文件
            </el-button>
          </div>
        </template>

        <!-- 筛选条件 -->
        <el-form :inline="true" class="filter-form">
          <el-form-item label="任务状态">
            <el-select
              v-model="searchForm.status"
              placeholder="全部状态"
              clearable
              style="width: 150px"
              @change="fetchTaskList"
            >
              <el-option label="等待中" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button @click="fetchTaskList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 统计信息 -->
        <el-row :gutter="20" v-if="statistics" class="statistics">
          <el-col :span="6">
            <el-statistic title="总任务数" :value="statistics.total_tasks">
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="总文件数" :value="statistics.total_files">
              <template #prefix>
                <el-icon><Folder /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="总记录数" :value="statistics.total_records">
              <template #prefix>
                <el-icon><List /></el-icon>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="成功记录" :value="statistics.success_records">
              <template #prefix>
                <el-icon style="color: #67c23a"><CircleCheck /></el-icon>
              </template>
              <template #suffix>
                <span style="color: #67c23a; font-size: 14px">
                  / {{ statistics.total_records }}
                </span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>

        <!-- 任务列表 -->
        <el-table
          v-loading="loading"
          :data="taskList"
          border
          stripe
          style="margin-top: 20px"
        >
          <el-table-column prop="task_id" label="任务ID" width="280" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="150">
            <template #default="{ row }">
              <el-progress
                :percentage="row.progress || 0"
                :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : ''"
              />
            </template>
          </el-table-column>
          <el-table-column prop="file_count" label="文件数" width="100" />
          <el-table-column prop="total_records" label="总记录数" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleViewDetail(row)">详情</el-button>
              <el-button
                size="small"
                type="warning"
                @click="handleCancelTask(row)"
                v-if="['pending', 'processing'].includes(row.status)"
              >
                取消
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDeleteTask(row)"
                v-if="canDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          style="margin-top: 20px; justify-content: flex-end"
          @size-change="fetchTaskList"
          @current-change="fetchTaskList"
        />
      </el-card>
    </div>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传银行流水文件"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #default>
          <div>当前案件: <strong>{{ selectedCase?.case_name }} ({{ selectedCase?.case_code }})</strong></div>
          <div style="margin-top: 5px; font-size: 12px; color: #909399">
            支持上传 ZIP/RAR/7Z 格式的压缩包，可同时上传多个文件
          </div>
        </template>
      </el-alert>

      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="导入规则" required>
          <el-select
            v-model="uploadForm.templateId"
            placeholder="请选择导入规则模板"
            style="width: 100%"
            @change="handleTemplateChange"
          >
            <el-option
              v-for="template in templateList"
              :key="template.id"
              :label="template.template_name"
              :value="template.id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>{{ template.template_name }}</span>
                <el-tag v-if="template.is_default" type="success" size="small">默认</el-tag>
              </div>
            </el-option>
          </el-select>
          <div v-if="selectedTemplate" style="margin-top: 8px; font-size: 12px; color: #909399">
            {{ selectedTemplate.description }}
          </div>
        </el-form-item>

        <el-form-item label="上传文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :file-list="uploadForm.fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".zip,.rar,.7z"
            multiple
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="uploadForm.fileList.length === 0"
          @click="handleUpload"
        >
          开始上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
    >
      <el-descriptions v-if="currentTask" :column="2" border>
        <el-descriptions-item label="任务ID" :span="2">
          {{ currentTask.task_id }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(currentTask.status)">
            {{ getStatusLabel(currentTask.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">
          {{ currentTask.progress }}%
        </el-descriptions-item>
        <el-descriptions-item label="当前步骤" :span="2">
          {{ currentTask.current_step || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="已处理文件">
          {{ currentTask.processed_files }} / {{ currentTask.total_files }}
        </el-descriptions-item>
        <el-descriptions-item label="总记录数">
          {{ currentTask.total_records || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="成功记录">
          {{ currentTask.success_records || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="失败记录">
          {{ currentTask.error_records || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentTask.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ currentTask.started_at || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="完成时间">
          {{ currentTask.completed_at || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentTask.elapsed_time ? formatTime(currentTask.elapsed_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="currentTask.error_message">
          <el-text type="danger">{{ currentTask.error_message }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="错误文件" :span="2" v-if="currentTask.error_files && currentTask.error_files.length > 0">
          <el-tag
            v-for="file in currentTask.error_files"
            :key="file"
            type="danger"
            style="margin-right: 5px"
          >
            {{ file }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          type="primary"
          @click="refreshTaskDetail"
          v-if="['pending', 'processing'].includes(currentTask?.status)"
        >
          刷新
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  UploadFilled,
  Refresh,
  Document,
  Folder,
  List,
  CircleCheck
} from '@element-plus/icons-vue'
import { caseApi } from '@/api/case'
import { bankStatementApi } from '@/api/bankStatement'
import { importRuleApi } from '@/api/importRule'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)
const isAdmin = computed(() => ['super_admin', 'admin'].includes(currentUser.value?.role))

const loading = ref(false)
const uploading = ref(false)
const caseList = ref([])
const selectedCaseId = ref(null)
const taskList = ref([])
const statistics = ref(null)
const uploadDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentTask = ref(null)
const uploadRef = ref(null)
const templateList = ref([])

let pollingTimer = null

const searchForm = reactive({
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const uploadForm = reactive({
  fileList: [],
  templateId: null
})

// 当前选中的案件
const selectedCase = computed(() => {
  return caseList.value.find(c => c.id === selectedCaseId.value)
})

// 当前选中的模板
const selectedTemplate = computed(() => {
  return templateList.value.find(t => t.id === uploadForm.templateId)
})

// 是否可以上传
const canUpload = computed(() => {
  if (!selectedCase.value) return false
  return isAdmin.value || ['write', 'admin'].includes(selectedCase.value.user_permission)
})

// 获取案件列表
async function fetchCaseList() {
  try {
    const data = await caseApi.getCaseList({ page: 1, page_size: 100 })
    caseList.value = data.items || []

    // 默认选择第一个案件
    if (caseList.value.length > 0 && !selectedCaseId.value) {
      selectedCaseId.value = caseList.value[0].id
      handleCaseChange()
    }
  } catch (error) {
    ElMessage.error('获取案件列表失败')
  }
}

// 案件切换
function handleCaseChange() {
  if (selectedCaseId.value) {
    fetchTaskList()
    fetchStatistics()
  }
}

// 获取任务列表
async function fetchTaskList() {
  if (!selectedCaseId.value) return

  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }

    if (searchForm.status) {
      params.status = searchForm.status
    }

    const data = await bankStatementApi.getTaskList(selectedCaseId.value, params)
    taskList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取统计信息
async function fetchStatistics() {
  if (!selectedCaseId.value) return

  try {
    const data = await bankStatementApi.getStatistics(selectedCaseId.value)
    statistics.value = data
  } catch (error) {
    console.error('获取统计信息失败', error)
  }
}

// 获取模板列表
async function fetchTemplateList() {
  try {
    const data = await importRuleApi.getTemplateList({ page: 1, page_size: 100, is_active: true })
    templateList.value = data.items || []
    // 默认选择默认模板
    const defaultTemplate = templateList.value.find(t => t.is_default)
    if (defaultTemplate) {
      uploadForm.templateId = defaultTemplate.id
    }
  } catch (error) {
    console.error('获取模板列表失败', error)
  }
}

// 显示上传对话框
function showUploadDialog() {
  if (!canUpload.value) {
    ElMessage.warning('没有上传权限，需要写入权限')
    return
  }

  uploadForm.fileList = []
  // 重新加载模板列表
  fetchTemplateList()
  uploadDialogVisible.value = true
}

// 模板变化
function handleTemplateChange() {
  // 可以在这里添加模板变化的处理逻辑
}

// 文件变化
function handleFileChange(file, fileList) {
  uploadForm.fileList = fileList
}

// 文件移除
function handleFileRemove(file, fileList) {
  uploadForm.fileList = fileList
}

// 上传文件
async function handleUpload() {
  if (uploadForm.fileList.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  if (!uploadForm.templateId) {
    ElMessage.warning('请选择导入规则模板')
    return
  }

  uploading.value = true
  try {
    const files = uploadForm.fileList.map(item => item.raw)
    const result = await bankStatementApi.uploadBankStatements(
      selectedCaseId.value,
      files,
      uploadForm.templateId
    )

    ElMessage.success(result.message || '上传成功，开始处理')
    uploadDialogVisible.value = false

    await fetchTaskList()
    await fetchStatistics()

    // 开始轮询任务进度
    startPolling()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 查看任务详情
async function handleViewDetail(row) {
  try {
    const data = await bankStatementApi.getTaskProgress(selectedCaseId.value, row.task_id)
    currentTask.value = data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取任务详情失败')
  }
}

// 刷新任务详情
async function refreshTaskDetail() {
  if (!currentTask.value) return

  try {
    const data = await bankStatementApi.getTaskProgress(selectedCaseId.value, currentTask.value.task_id)
    currentTask.value = data
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 取消任务
async function handleCancelTask(row) {
  try {
    await ElMessageBox.confirm('确定要取消该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await bankStatementApi.cancelTask(selectedCaseId.value, row.task_id)
    ElMessage.success('任务已取消')
    fetchTaskList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消任务失败')
    }
  }
}

// 删除任务
async function handleDeleteTask(row) {
  try {
    await ElMessageBox.confirm('确定要删除该任务记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await bankStatementApi.deleteTask(selectedCaseId.value, row.task_id)
    ElMessage.success('删除成功')
    fetchTaskList()
    fetchStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 判断是否可以删除
function canDelete(row) {
  if (!selectedCase.value) return false
  return isAdmin.value || selectedCase.value.user_permission === 'admin'
}

// 获取权限标签
function getPermissionLabel(permission) {
  const labelMap = {
    read: '只读',
    write: '读写',
    admin: '管理员'
  }
  return labelMap[permission] || permission
}

// 状态标签类型
function getStatusTagType(status) {
  const typeMap = {
    pending: 'info',
    processing: '',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return typeMap[status] || 'info'
}

// 状态标签文本
function getStatusLabel(status) {
  const labelMap = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return labelMap[status] || status
}

// 格式化时间（秒转为可读格式）
function formatTime(seconds) {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}分${secs}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分`
  }
}

// 开始轮询
function startPolling() {
  stopPolling()
  pollingTimer = setInterval(() => {
    // 检查是否有进行中的任务
    const hasProcessing = taskList.value.some(task =>
      ['pending', 'processing'].includes(task.status)
    )

    if (hasProcessing) {
      fetchTaskList()
      fetchStatistics()
    } else {
      stopPolling()
    }
  }, 3000) // 每3秒轮询一次
}

// 停止轮询
function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

onMounted(() => {
  fetchCaseList()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.bank-statement-page {
  padding: 20px;
}

.case-selector-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 15px 20px;
  }
}

.content-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  :deep(.el-card__header) {
    padding: 15px 20px;
    background-color: #f5f7fa;
  }
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
  font-weight: 500;

  .el-icon {
    font-size: 18px;
  }
}

.filter-form {
  margin-bottom: 0;
}

.statistics {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.el-icon--upload {
  font-size: 67px;
  color: #c0c4cc;
  margin: 40px 0 16px;
  line-height: 50px;
}
</style>
