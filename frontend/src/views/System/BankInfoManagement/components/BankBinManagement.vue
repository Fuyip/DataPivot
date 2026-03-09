<template>
  <div class="bank-bin-management">
    <!-- 搜索筛选区 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="BIN码">
        <el-input v-model="searchForm.bin" placeholder="请输入BIN码" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="银行名称">
        <el-input v-model="searchForm.bank_name" placeholder="请输入银行名称" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="BIN长度">
        <el-select v-model="searchForm.bin_len" placeholder="请选择" clearable style="width: 120px">
          <el-option label="6位" :value="6" />
          <el-option label="8位" :value="8" />
        </el-select>
      </el-form-item>
      <el-form-item label="卡长度">
        <el-select v-model="searchForm.card_len" placeholder="请选择" clearable style="width: 120px">
          <el-option label="16位" :value="16" />
          <el-option label="17位" :value="17" />
          <el-option label="18位" :value="18" />
          <el-option label="19位" :value="19" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 操作按钮区 -->
    <div class="action-buttons">
      <el-button type="primary" @click="handleAdd">新增</el-button>
      <el-button type="success" @click="handleExport">导出</el-button>
      <el-button type="info" @click="handleDownloadTemplate">下载模板</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%; margin-top: 20px" v-loading="loading">
      <el-table-column prop="bin" label="BIN码" width="150" />
      <el-table-column prop="bin_len" label="BIN长度" width="100" />
      <el-table-column prop="card_len" label="卡长度" width="100" />
      <el-table-column prop="bank_name" label="银行名称" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="pagination.total"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      style="margin-top: 20px; justify-content: flex-end"
    />

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="BIN码" prop="bin">
          <el-input v-model="formData.bin" placeholder="请输入BIN码" @input="handleBinInput" />
        </el-form-item>
        <el-form-item label="BIN长度" prop="bin_len">
          <el-input-number v-model="formData.bin_len" :min="1" :max="20" disabled />
        </el-form-item>
        <el-form-item label="卡长度" prop="card_len">
          <el-select v-model="formData.card_len" placeholder="请选择卡长度">
            <el-option label="16位" :value="16" />
            <el-option label="17位" :value="17" />
            <el-option label="18位" :value="18" />
            <el-option label="19位" :value="19" />
          </el-select>
        </el-form-item>
        <el-form-item label="银行名称" prop="bank_name">
          <el-input v-model="formData.bank_name" placeholder="请输入银行名称" />
        </el-form-item>
        <el-form-item label="变更原因" prop="reason" v-if="!isSuperAdmin || showReasonField">
          <el-input
            v-model="formData.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入变更原因"
          />
        </el-form-item>
        <el-form-item v-if="isSuperAdmin">
          <el-checkbox v-model="formData.direct_execute">直接执行（跳过审批）</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ isSuperAdmin && formData.direct_execute ? '确定' : '提交申请' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, defineExpose } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getBankBinList,
  createBankBin,
  updateBankBin,
  deleteBankBin,
  exportBankBin,
  downloadBankBinTemplate
} from '@/api/bankInfo'

const props = defineProps({
  userRole: {
    type: String,
    default: 'user'
  }
})

const isSuperAdmin = computed(() => props.userRole === 'super_admin')
const showReasonField = ref(true)

// 搜索表单
const searchForm = reactive({
  bin: '',
  bank_name: '',
  bin_len: null,
  card_len: null
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => (formData.isEdit ? '编辑 BIN 码' : '新增 BIN 码'))
const formRef = ref(null)
const formData = reactive({
  isEdit: false,
  oldBin: '',
  bin: '',
  bin_len: 0,
  card_len: 16,
  bank_name: '',
  reason: '',
  direct_execute: false
})

const formRules = {
  bin: [
    { required: true, message: '请输入BIN码', trigger: 'blur' },
    { pattern: /^\d+$/, message: 'BIN码必须是数字', trigger: 'blur' }
  ],
  bin_len: [{ required: true, message: '请输入BIN长度', trigger: 'blur' }],
  card_len: [{ required: true, message: '请选择卡长度', trigger: 'change' }],
  bank_name: [{ required: true, message: '请输入银行名称', trigger: 'blur' }]
}

const submitLoading = ref(false)

// BIN码输入时自动计算长度
const handleBinInput = () => {
  formData.bin_len = formData.bin.length
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const res = await getBankBinList(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.bin = ''
  searchForm.bank_name = ''
  searchForm.bin_len = null
  searchForm.card_len = null
  handleSearch()
}

// 分页
const handleSizeChange = () => {
  pagination.page = 1
  loadData()
}

const handlePageChange = () => {
  loadData()
}

// 新增
const handleAdd = () => {
  Object.assign(formData, {
    isEdit: false,
    oldBin: '',
    bin: '',
    bin_len: 0,
    card_len: 16,
    bank_name: '',
    reason: '',
    direct_execute: false
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  Object.assign(formData, {
    isEdit: true,
    oldBin: row.bin,
    bin: row.bin,
    bin_len: row.bin_len,
    card_len: row.card_len,
    bank_name: row.bank_name,
    reason: '',
    direct_execute: false
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      const requestData = {
        data: {
          bin: formData.bin,
          bin_len: formData.bin_len,
          card_len: formData.card_len,
          bank_name: formData.bank_name
        },
        reason: formData.reason,
        direct_execute: formData.direct_execute
      }

      if (formData.isEdit) {
        await updateBankBin(formData.oldBin, requestData)
      } else {
        await createBankBin(requestData)
      }

      const message = formData.direct_execute ? '操作成功' : '申请已提交，等待审批'
      ElMessage.success(message)
      dialogVisible.value = false
      loadData()
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

    let reason = ''
    let directExecute = false

    if (isSuperAdmin.value) {
      const { value, action } = await ElMessageBox.prompt('请输入删除原因（可选）', '删除确认', {
        confirmButtonText: '直接删除',
        cancelButtonText: '提交申请',
        distinguishCancelAndClose: true,
        inputPlaceholder: '删除原因'
      }).catch(() => ({ action: 'cancel' }))

      if (action === 'confirm') {
        directExecute = true
        reason = value || ''
      } else if (action === 'cancel') {
        directExecute = false
        reason = value || ''
      } else {
        return
      }
    } else {
      const { value } = await ElMessageBox.prompt('请输入删除原因', '提交删除申请', {
        confirmButtonText: '提交申请',
        inputPlaceholder: '删除原因',
        inputValidator: (val) => !!val,
        inputErrorMessage: '请输入删除原因'
      })
      reason = value
    }

    await deleteBankBin(row.bin, { reason, direct_execute: directExecute })
    const message = directExecute ? '删除成功' : '删除申请已提交，等待审批'
    ElMessage.success(message)
    loadData()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('删除失败')
    }
  }
}

// 导出
const handleExport = async () => {
  try {
    const res = await exportBankBin(searchForm)
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'bank_bin.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 下载模板
const handleDownloadTemplate = async () => {
  try {
    const res = await downloadBankBinTemplate()
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'bank_bin_template.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载模板失败')
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
.bank-bin-management {
  padding: 20px;
}

.search-form {
  margin-bottom: 10px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
