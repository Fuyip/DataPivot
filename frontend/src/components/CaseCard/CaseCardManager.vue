<template>
  <div class="case-card-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>案件银行卡管理</span>
          <div class="header-actions">
            <el-button type="success" @click="handleDownloadTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="warning" @click="handleImport">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="info" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button @click="showImportTasks">
              <el-icon><List /></el-icon>
              导入任务
            </el-button>
            <el-button @click="handleRematchBanks">
              <el-icon><Refresh /></el-icon>
              一键匹配银行
            </el-button>
            <el-button
              type="danger"
              :disabled="selectedRows.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加银行卡
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="卡号">
          <el-input
            v-model="searchForm.card_no"
            placeholder="请输入卡号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="银行名称">
          <el-input
            v-model="searchForm.bank_name"
            placeholder="请输入银行名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="卡类型">
          <el-select
            v-model="searchForm.card_type"
            placeholder="请选择卡类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="type in cardTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        stripe
        style="margin-top: 20px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="card_no" label="卡号" width="200" show-overflow-tooltip />
        <el-table-column prop="bank_name" label="银行名称" width="150" />
        <el-table-column prop="card_type" label="卡类型" width="100" />
        <el-table-column prop="source" label="卡主姓名" width="120" />
        <el-table-column prop="batch" label="批次" width="80" />
        <el-table-column prop="add_date" label="添加日期" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
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
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="卡号" prop="card_no">
          <el-input
            v-model="formData.card_no"
            placeholder="请输入卡号"
            :disabled="isEdit"
            @blur="handleCardNoBlur"
          />
        </el-form-item>
        <el-form-item label="银行名称" prop="bank_name">
          <el-input v-model="formData.bank_name" placeholder="请输入银行名称" />
        </el-form-item>
        <el-form-item label="卡类型" prop="card_type">
          <el-select v-model="formData.card_type" placeholder="请选择卡类型" style="width: 100%">
            <el-option
              v-for="type in cardTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="卡主姓名" prop="source">
          <el-input v-model="formData.source" placeholder="请输入卡主姓名" />
        </el-form-item>
        <el-form-item label="用户ID" prop="user_id">
          <el-input v-model="formData.user_id" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="批次" prop="batch">
          <el-input-number v-model="formData.batch" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入案件银行卡"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :file-list="importFileList"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只支持 Excel 文件(.xlsx, .xls)
          </div>
        </template>
      </el-upload>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="importing"
          :disabled="importFileList.length === 0"
          @click="handleImportSubmit"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入任务对话框 -->
    <el-dialog
      v-model="taskDialogVisible"
      title="导入任务管理"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-table
        v-loading="taskLoading"
        :data="taskList"
        border
        stripe
      >
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="file_name" label="文件名" width="150" show-overflow-tooltip />
        <el-table-column prop="total_count" label="总数" width="80" />
        <el-table-column prop="success_count" label="成功" width="80" />
        <el-table-column prop="error_count" label="失败" width="80" />
        <el-table-column prop="created_at" label="导入时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="warning"
              :disabled="!row.error_details || row.error_details.length === 0"
              @click="showTaskErrors(row)"
            >
              查看错误
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDeleteTaskCards(row)"
            >
              删除数据
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="taskPagination.page"
        v-model:page-size="taskPagination.page_size"
        :page-sizes="[10, 20, 50]"
        :total="taskPagination.total"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="fetchImportTasks"
        @current-change="fetchImportTasks"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, Plus, UploadFilled, Delete, List, Refresh } from '@element-plus/icons-vue'
import { caseCardApi } from '@/api/caseCard'

const props = defineProps({
  caseId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const taskDialogVisible = ref(false)
const taskLoading = ref(false)
const isEdit = ref(false)
const currentRow = ref(null)
const formRef = ref(null)
const uploadRef = ref(null)
const importFileList = ref([])
const selectedRows = ref([])
const cardTypes = ref([])
const taskList = ref([])

const searchForm = reactive({
  card_no: '',
  bank_name: '',
  card_type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const taskPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const formData = reactive({
  card_no: '',
  bank_name: '',
  card_type: '',
  source: '',
  user_id: '',
  batch: 0,
  is_main: 0,
  is_in_bg: 0
})

const formRules = {
  card_no: [
    { required: true, message: '请输入卡号', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => isEdit.value ? '编辑银行卡' : '添加银行卡')

// 获取数据
async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }

    const data = await caseCardApi.getCaseCardList(props.caseId, params)
    tableData.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 加载卡类型
async function loadCardTypes() {
  try {
    const data = await caseCardApi.getCardTypes(props.caseId)
    cardTypes.value = data || []
  } catch (error) {
    console.error('加载卡类型失败', error)
  }
}

// 选择变化处理
function handleSelectionChange(selection) {
  selectedRows.value = selection
}

// 卡号失焦时自动匹配银行
async function handleCardNoBlur() {
  if (!formData.card_no || formData.card_no.length < 16 || isEdit.value) {
    return
  }

  try {
    const data = await caseCardApi.matchBankName(props.caseId, formData.card_no)
    if (data.matched && data.bank_name) {
      formData.bank_name = data.bank_name
      ElMessage.success(`已自动匹配银行：${data.bank_name}`)
    }
  } catch (error) {
    console.error('银行名称匹配失败', error)
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  fetchData()
}

// 重置
function handleReset() {
  searchForm.card_no = ''
  searchForm.bank_name = ''
  searchForm.card_type = ''
  pagination.page = 1
  fetchData()
}

// 添加
function handleAdd() {
  isEdit.value = false
  currentRow.value = null
  resetForm()
  dialogVisible.value = true
}

// 编辑
function handleEdit(row) {
  isEdit.value = true
  currentRow.value = row
  Object.assign(formData, {
    card_no: row.card_no,
    bank_name: row.bank_name,
    card_type: row.card_type,
    source: row.source,
    user_id: row.user_id,
    batch: row.batch,
    is_main: row.is_main,
    is_in_bg: row.is_in_bg
  })
  dialogVisible.value = true
}

// 删除
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该银行卡吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await caseCardApi.deleteCaseCard(props.caseId, row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        await caseCardApi.updateCaseCard(props.caseId, currentRow.value.id, formData)
        ElMessage.success('更新成功')
      } else {
        await caseCardApi.createCaseCard(props.caseId, formData)
        ElMessage.success('添加成功')
      }

      dialogVisible.value = false
      fetchData()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '添加失败')
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
function resetForm() {
  Object.assign(formData, {
    card_no: '',
    bank_name: '',
    card_type: '',
    source: '',
    user_id: '',
    batch: 0,
    is_main: 0,
    is_in_bg: 0
  })
  formRef.value?.clearValidate()
}

// 批量删除
async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const cardIds = selectedRows.value.map(row => row.id)
    await caseCardApi.batchDeleteCaseCards(props.caseId, cardIds)

    ElMessage.success('批量删除成功')
    selectedRows.value = []
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 导出
async function handleExport() {
  try {
    const blob = await caseCardApi.exportCaseCards(props.caseId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `case_cards_${props.caseId}_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 下载模板
async function handleDownloadTemplate() {
  try {
    const blob = await caseCardApi.downloadTemplate(props.caseId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'case_card_template.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 导入
function handleImport() {
  importFileList.value = []
  importDialogVisible.value = true
}

// 文件变化
function handleFileChange(file, fileList) {
  importFileList.value = fileList
}

// 导入提交
async function handleImportSubmit() {
  if (importFileList.value.length === 0) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  importing.value = true
  try {
    const file = importFileList.value[0].raw
    const result = await caseCardApi.importCaseCards(props.caseId, file)

    ElMessage.success(
      `导入完成：成功 ${result.success_count} 条，失败 ${result.error_count} 条`
    )

    if (result.errors && result.errors.length > 0) {
      // 显示错误详情
      const errorHtml = result.errors.map(err =>
        `<div style="margin: 5px 0;">第${err.row}行 - 卡号: ${err.card_no} - ${err.error}</div>`
      ).join('')

      ElMessageBox.confirm(
        `<div style="max-height: 400px; overflow-y: auto;">${errorHtml}</div>`,
        '导入错误详情',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '下载错误报告',
          cancelButtonText: '关闭',
          distinguishCancelAndClose: true,
          type: 'warning'
        }
      ).then(() => {
        // 下载错误报告
        downloadErrorReport(result.errors)
      }).catch(() => {
        // 用户点击关闭或取消
      })
    }

    importDialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

// 下载错误报告
function downloadErrorReport(errors) {
  // 使用 xlsx 库生成 Excel
  import('xlsx').then(XLSX => {
    const ws_data = [['行号', '卡号', '错误原因']]
    errors.forEach(err => {
      ws_data.push([err.row, err.card_no, err.error])
    })

    const ws = XLSX.utils.aoa_to_sheet(ws_data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '导入错误报告')

    // 下载文件
    XLSX.writeFile(wb, `导入错误报告_${Date.now()}.xlsx`)
    ElMessage.success('错误报告已下载')
  }).catch(() => {
    ElMessage.error('下载错误报告失败')
  })
}

// 显示导入任务列表
function showImportTasks() {
  taskDialogVisible.value = true
  fetchImportTasks()
}

// 获取导入任务列表
async function fetchImportTasks() {
  taskLoading.value = true
  try {
    const params = {
      page: taskPagination.page,
      page_size: taskPagination.page_size
    }
    const data = await caseCardApi.getImportTasks(props.caseId, params)
    taskList.value = data.items || []
    taskPagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取导入任务失败')
  } finally {
    taskLoading.value = false
  }
}

// 显示任务错误详情
function showTaskErrors(task) {
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

// 删除任务相关的所有银行卡
async function handleDeleteTaskCards(task) {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 #${task.id} 导入的所有银行卡吗？这将删除 ${task.success_count} 条记录。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await caseCardApi.deleteCardsByTask(props.caseId, task.id)
    ElMessage.success('删除成功')
    fetchImportTasks()
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 一键重新匹配银行
async function handleRematchBanks() {
  try {
    await ElMessageBox.confirm(
      '确定要重新匹配所有未匹配的银行名称吗？',
      '重新匹配',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const result = await caseCardApi.rematchUnmatchedBanks(props.caseId)
    ElMessage.success(
      `匹配完成：成功匹配 ${result.matched_count} 条，仍有 ${result.unmatched_count} 条未匹配`
    )
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新匹配失败')
    }
  }
}

onMounted(() => {
  fetchData()
  loadCardTypes()
})
</script>

<style scoped lang="scss">
.case-card-manager {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .search-form {
    margin-bottom: 0;
  }

  .el-icon--upload {
    font-size: 67px;
    color: #c0c4cc;
    margin: 40px 0 16px;
    line-height: 50px;
  }
}
</style>
