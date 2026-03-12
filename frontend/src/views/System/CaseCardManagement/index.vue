<template>
  <div class="case-card-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>案件银行卡管理</span>
        </div>
      </template>

      <!-- 案件选择 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="选择案件">
          <el-select
            v-model="selectedCaseId"
            placeholder="请选择案件"
            filterable
            @change="handleCaseChange"
            style="width: 300px"
          >
            <el-option
              v-for="item in caseList"
              :key="item.id"
              :label="`${item.case_code} - ${item.case_name}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 搜索和操作栏 -->
      <div v-if="selectedCaseId" class="toolbar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="卡号">
            <el-input v-model="searchForm.card_no" placeholder="请输入卡号" clearable />
          </el-form-item>
          <el-form-item label="银行名称">
            <el-input v-model="searchForm.bank_name" placeholder="请输入银行名称" clearable />
          </el-form-item>
          <el-form-item label="卡类型">
            <el-select v-model="searchForm.card_type" placeholder="请选择卡类型" clearable>
              <el-option
                v-for="item in cardTypes"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>

        <div class="action-buttons">
          <el-button type="primary" @click="handleAdd">新增银行卡</el-button>
          <el-button type="success" @click="handleImport">导入</el-button>
          <el-button type="info" @click="handleDownloadTemplate">下载模板</el-button>
          <el-button type="warning" @click="handleExport">导出</el-button>
          <el-button type="danger" @click="handleBatchDelete" :disabled="selectedCards.length === 0">
            批量删除
          </el-button>
          <el-button @click="handleRematch">重新匹配银行</el-button>
          <el-button @click="handleShowImportTasks">导入任务</el-button>
        </div>
      </div>

      <!-- 银行卡列表 -->
      <el-table
        v-if="selectedCaseId"
        :data="tableData"
        style="width: 100%; margin-top: 20px"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="card_no" label="卡号" width="200" />
        <el-table-column prop="bank_name" label="银行名称" width="150" />
        <el-table-column prop="card_type" label="卡类型" width="100">
          <template #default="{ row }">
            {{ getCardTypeLabel(row.card_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="持卡人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="selectedCaseId"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="卡号" prop="card_no">
          <el-input v-model="formData.card_no" placeholder="请输入卡号" @blur="handleCardNoBlur" />
        </el-form-item>
        <el-form-item label="银行名称" prop="bank_name">
          <el-input v-model="formData.bank_name" placeholder="请输入银行名称" />
        </el-form-item>
        <el-form-item label="卡类型" prop="card_type">
          <el-select v-model="formData.card_type" placeholder="请选择卡类型">
            <el-option
              v-for="item in cardTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="持卡人" prop="source">
          <el-input v-model="formData.source" placeholder="请输入持卡人姓名" />
        </el-form-item>
        <el-form-item label="身份证号" prop="holder_id">
          <el-input v-model="formData.holder_id" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入银行卡" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
      >
        <template #trigger>
          <el-button type="primary">选择文件</el-button>
        </template>
        <template #tip>
          <div class="el-upload__tip">只能上传 xlsx/xls 文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImportSubmit" :loading="importLoading">
          确定导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入任务对话框 -->
    <el-dialog
      v-model="showImportTasks"
      title="导入任务"
      width="960px"
      @close="handleImportTasksClose"
    >
      <el-table :data="importTasks" v-loading="tasksLoading">
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="file_name" label="文件名" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getImportTaskStatusTagType(row.status)">
              {{ getImportTaskStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.progress || 0)"
              :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : ''"
            />
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前步骤" width="180" show-overflow-tooltip />
        <el-table-column prop="total_count" label="总数" width="80" />
        <el-table-column prop="success_count" label="成功" width="80" />
        <el-table-column prop="error_count" label="失败" width="80" />
        <el-table-column prop="created_at" label="导入时间" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button
              link
              type="warning"
              :disabled="!row.error_details || row.error_details.length === 0"
              @click="showTaskErrors(row)"
            >
              查看错误
            </el-button>
            <el-button
              link
              type="danger"
              :disabled="['pending', 'processing'].includes(row.status)"
              @click="handleDeleteTask(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="taskPagination.page"
        v-model:page-size="taskPagination.page_size"
        :total="taskPagination.total"
        layout="total, prev, pager, next"
        @current-change="loadImportTasks"
        style="margin-top: 20px"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { caseApi } from '@/api/case'
import { caseCardApi } from '@/api/caseCard'

// 案件列表
const caseList = ref([])
const selectedCaseId = ref(null)

// 搜索表单
const searchForm = reactive({
  card_no: '',
  bank_name: '',
  card_type: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)
const selectedCards = ref([])

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 卡类型
const cardTypes = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (formData.id ? '编辑银行卡' : '新增银行卡'))
const formRef = ref(null)
const formData = reactive({
  id: null,
  card_no: '',
  bank_name: '',
  card_type: '',
  source: '',
  holder_id: '',
  phone: '',
  remark: ''
})

const formRules = {
  card_no: [{ required: true, message: '请输入卡号', trigger: 'blur' }],
  bank_name: [{ required: true, message: '请输入银行名称', trigger: 'blur' }],
  card_type: [{ required: true, message: '请选择卡类型', trigger: 'change' }]
}

const submitLoading = ref(false)

// 导入
const importDialogVisible = ref(false)
const uploadRef = ref(null)
const importFile = ref(null)
const importLoading = ref(false)

// 导入任务
const showImportTasks = ref(false)
const importTasks = ref([])
const tasksLoading = ref(false)
let importTaskPollingTimer = null
const taskPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 加载案件列表
const loadCaseList = async () => {
  try {
    const data = await caseApi.getCaseList({ page: 1, page_size: 100 })
    caseList.value = data.items || []
  } catch (error) {
    ElMessage.error('加载案件列表失败')
  }
}

// 加载卡类型
const loadCardTypes = async () => {
  if (!selectedCaseId.value) return
  try {
    const data = await caseCardApi.getCardTypes(selectedCaseId.value)
    cardTypes.value = data || []
  } catch (error) {
    ElMessage.error('加载卡类型失败')
  }
}

// 获取卡类型标签
const getCardTypeLabel = (value) => {
  const type = cardTypes.value.find(item => item.value === value)
  return type ? type.label : value
}

// 案件切换
const handleCaseChange = () => {
  pagination.page = 1
  loadCardTypes()
  loadTableData()
}

// 加载表格数据
const loadTableData = async () => {
  if (!selectedCaseId.value) return

  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const data = await caseCardApi.getCaseCardList(selectedCaseId.value, params)
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadTableData()
}

// 重置
const handleReset = () => {
  searchForm.card_no = ''
  searchForm.bank_name = ''
  searchForm.card_type = ''
  handleSearch()
}

// 分页
const handleSizeChange = () => {
  pagination.page = 1
  loadTableData()
}

const handlePageChange = () => {
  loadTableData()
}

// 选择
const handleSelectionChange = (selection) => {
  selectedCards.value = selection
}

// 新增
const handleAdd = () => {
  Object.assign(formData, {
    id: null,
    card_no: '',
    bank_name: '',
    card_type: '',
    source: '',
    holder_id: '',
    phone: '',
    remark: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(formData, { ...row })
  dialogVisible.value = true
}

// 卡号失焦自动匹配银行
const handleCardNoBlur = async () => {
  if (!formData.card_no || formData.bank_name) return

  try {
    const data = await caseCardApi.matchBankName(selectedCaseId.value, formData.card_no)
    if (data.bank_name) {
      formData.bank_name = data.bank_name
      ElMessage.success('已自动匹配银行名称')
    }
  } catch (error) {
    // 匹配失败不提示错误
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (formData.id) {
        await caseCardApi.updateCaseCard(selectedCaseId.value, formData.id, formData)
        ElMessage.success('更新成功')
      } else {
        await caseCardApi.createCaseCard(selectedCaseId.value, formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadTableData()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗?', '提示', {
      type: 'warning'
    })

    await caseCardApi.deleteCaseCard(selectedCaseId.value, row.id)
    ElMessage.success('删除成功')
    loadTableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedCards.value.length} 条记录吗?`, '提示', {
      type: 'warning'
    })

    const cardIds = selectedCards.value.map(item => item.id)
    await caseCardApi.batchDeleteCaseCards(selectedCaseId.value, cardIds)
    ElMessage.success('批量删除成功')
    loadTableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 导入
const handleImport = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportSubmit = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importLoading.value = true
  try {
    const data = await caseCardApi.importCaseCards(selectedCaseId.value, importFile.value)
    ElMessage.success('文件上传成功，后台处理中')
    importDialogVisible.value = false
    handleShowImportTasks()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    importLoading.value = false
  }
}

// 下载模板
const handleDownloadTemplate = async () => {
  try {
    const res = await caseCardApi.downloadTemplate(selectedCaseId.value)
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'case_card_template.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载模板失败')
  }
}

// 导出
const handleExport = async () => {
  try {
    const res = await caseCardApi.exportCaseCards(selectedCaseId.value)
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    const caseCode = caseList.value.find(c => c.id === selectedCaseId.value)?.case_code || 'export'
    link.setAttribute('download', `case_cards_${caseCode}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 重新匹配银行
const handleRematch = async () => {
  try {
    await ElMessageBox.confirm('确定要重新匹配所有未匹配的银行名称吗?', '提示', {
      type: 'info'
    })

    const data = await caseCardApi.rematchUnmatchedBanks(selectedCaseId.value)
    ElMessage.success(`匹配完成: 成功 ${data.matched_count} 条, 未匹配 ${data.unmatched_count} 条`)
    loadTableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新匹配失败')
    }
  }
}

// 加载导入任务
const loadImportTasks = async () => {
  if (!selectedCaseId.value) return

  tasksLoading.value = true
  try {
    const params = {
      page: taskPagination.page,
      page_size: taskPagination.page_size
    }
    const data = await caseCardApi.getImportTasks(selectedCaseId.value, params)
    importTasks.value = data.items || []
    taskPagination.total = data.total || 0
    if (showImportTasks.value) {
      const hasActiveTasks = importTasks.value.some(task => ['pending', 'processing'].includes(task.status))
      if (hasActiveTasks) {
        startImportTaskPolling()
      } else {
        stopImportTaskPolling()
        loadTableData()
      }
    }
  } catch (error) {
    ElMessage.error('加载导入任务失败')
  } finally {
    tasksLoading.value = false
  }
}

const getImportTaskStatusLabel = (status) => {
  const statusMap = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status || '未知'
}

const getImportTaskStatusTagType = (status) => {
  const tagMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return tagMap[status] || 'info'
}

const startImportTaskPolling = () => {
  if (importTaskPollingTimer || !showImportTasks.value) return

  importTaskPollingTimer = setInterval(() => {
    if (!showImportTasks.value) {
      stopImportTaskPolling()
      return
    }

    const hasActiveTasks = importTasks.value.some(task => ['pending', 'processing'].includes(task.status))
    if (!hasActiveTasks) {
      stopImportTaskPolling()
      return
    }

    loadImportTasks()
  }, 3000)
}

const stopImportTaskPolling = () => {
  if (importTaskPollingTimer) {
    clearInterval(importTaskPollingTimer)
    importTaskPollingTimer = null
  }
}

const downloadErrorReport = (errors) => {
  import('xlsx').then(XLSX => {
    const wsData = [['行号', '卡号', '错误原因']]

    errors.forEach(err => {
      wsData.push([err.row, err.card_no, err.error])
    })

    const ws = XLSX.utils.aoa_to_sheet(wsData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '导入错误报告')
    XLSX.writeFile(wb, `导入错误报告_${Date.now()}.xlsx`)
    ElMessage.success('错误报告已下载')
  }).catch(() => {
    ElMessage.error('下载错误报告失败')
  })
}

const handleShowImportTasks = () => {
  showImportTasks.value = true
  loadImportTasks()
}

const handleImportTasksClose = () => {
  stopImportTaskPolling()
}

const showTaskErrors = (task) => {
  if (!task.error_details || task.error_details.length === 0) {
    ElMessage.info('该任务没有错误记录')
    return
  }

  const errorHtml = task.error_details.map(err =>
    `<div style="margin: 5px 0;">第${err.row}行 - 卡号: ${err.card_no} - ${err.error}</div>`
  ).join('')

  ElMessageBox.confirm(
    `<div style="max-height: 400px; overflow-y: auto;">${errorHtml}</div>`,
    `任务 #${task.id} 错误详情`,
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '下载错误报告',
      cancelButtonText: '关闭',
      distinguishCancelAndClose: true,
      type: 'warning'
    }
  ).then(() => {
    downloadErrorReport(task.error_details)
  }).catch(() => {
    // 用户点击关闭或取消
  })
}

// 删除导入任务
const handleDeleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('删除任务将同时删除该任务导入的所有银行卡,确定要删除吗?', '警告', {
      type: 'warning'
    })

    const data = await caseCardApi.deleteCardsByTask(selectedCaseId.value, taskId)
    ElMessage.success(`删除成功: ${data.deleted_count} 条记录`)
    loadImportTasks()
    loadTableData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadCaseList()
})

onUnmounted(() => {
  stopImportTaskPolling()
})
</script>

<style scoped>
.case-card-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar {
  margin-top: 20px;
}

.search-form {
  margin-bottom: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
