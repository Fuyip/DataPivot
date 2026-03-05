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
            <el-option label="借记卡" value="借记卡" />
            <el-option label="信用卡" value="信用卡" />
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
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="card_no" label="卡号" width="200" show-overflow-tooltip />
        <el-table-column prop="bank_name" label="银行名称" width="150" />
        <el-table-column prop="card_type" label="卡类型" width="100" />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="batch" label="批次" width="80" />
        <el-table-column prop="is_main" label="是否主卡" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_main === 1 ? 'success' : 'info'">
              {{ row.is_main === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
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
          />
        </el-form-item>
        <el-form-item label="银行名称" prop="bank_name">
          <el-input v-model="formData.bank_name" placeholder="请输入银行名称" />
        </el-form-item>
        <el-form-item label="卡类型" prop="card_type">
          <el-select v-model="formData.card_type" placeholder="请选择卡类型" style="width: 100%">
            <el-option label="借记卡" value="借记卡" />
            <el-option label="信用卡" value="信用卡" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="formData.source" placeholder="请输入来源" />
        </el-form-item>
        <el-form-item label="用户ID" prop="user_id">
          <el-input v-model="formData.user_id" placeholder="请输入用户ID" />
        </el-form-item>
        <el-form-item label="批次" prop="batch">
          <el-input-number v-model="formData.batch" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="是否主卡" prop="is_main">
          <el-radio-group v-model="formData.is_main">
            <el-radio :label="1">是</el-radio>
            <el-radio :label="0">否</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="是否在后台" prop="is_in_bg">
          <el-radio-group v-model="formData.is_in_bg">
            <el-radio :label="1">是</el-radio>
            <el-radio :label="0">否</el-radio>
          </el-radio-group>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload, Plus, UploadFilled } from '@element-plus/icons-vue'
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
const isEdit = ref(false)
const currentRow = ref(null)
const formRef = ref(null)
const uploadRef = ref(null)
const importFileList = ref([])

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

const formData = reactive({
  card_no: '',
  bank_name: '',
  card_type: '',
  source: '',
  user_id: '',
  batch: 1,
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
    batch: 1,
    is_main: 0,
    is_in_bg: 0
  })
  formRef.value?.clearValidate()
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
      console.warn('导入错误:', result.errors)
    }

    importDialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchData()
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
