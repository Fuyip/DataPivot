<template>
  <div class="case-management">
    <el-card>
      <!-- 选项卡 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部案件" name="all"></el-tab-pane>
        <el-tab-pane label="已删除" name="deleted" v-if="isAdmin"></el-tab-pane>
      </el-tabs>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form" v-if="activeTab === 'all'">
        <el-form-item label="案件名称">
          <el-input
            v-model="searchForm.search"
            placeholder="请输入案件名称/编号"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="进行中" value="active" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="toolbar" v-if="activeTab === 'all'">
        <el-button type="primary" @click="handleAdd" v-if="isAdmin">
          <el-icon><Plus /></el-icon>
          新增案件
        </el-button>
      </div>

      <!-- 案件表格 -->
      <el-table
        v-if="activeTab === 'all'"
        v-loading="loading"
        :data="caseList"
        border
        stripe
        style="margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="case_name" label="案件名称" width="200" />
        <el-table-column prop="case_code" label="案件编号" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '进行中' : '已归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_permission" label="我的权限" width="100">
          <template #default="{ row }">
            <el-tag :type="getPermissionTagType(row.user_permission)">
              {{ getPermissionLabel(row.user_permission) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button
              size="small"
              @click="handleEdit(row)"
              v-if="canEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="handleManagePermissions(row)"
              v-if="canManagePermissions(row)"
            >
              权限管理
            </el-button>
            <el-button
              size="small"
              type="warning"
              @click="handleArchive(row)"
              v-if="canArchive(row)"
            >
              归档
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              v-if="isAdmin"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="activeTab === 'all'"
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="fetchCaseList"
        @current-change="fetchCaseList"
      />

      <!-- 已删除案件表格 -->
      <el-table
        v-if="activeTab === 'deleted'"
        v-loading="loading"
        :data="deletedCaseList"
        border
        stripe
        style="margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="case_name" label="案件名称" width="200" />
        <el-table-column prop="case_code" label="案件编号" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="deleted_at" label="删除时间" width="180" />
        <el-table-column prop="deleted_by" label="删除人" width="120">
          <template #default="{ row }">
            {{ row.deleted_by_username || row.deleted_by }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="success" @click="handleRestore(row)">
              恢复
            </el-button>
            <el-button size="small" type="danger" @click="handlePermanentDelete(row)">
              彻底删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 已删除案件分页 -->
      <el-pagination
        v-if="activeTab === 'deleted'"
        v-model:current-page="deletedPagination.page"
        v-model:page-size="deletedPagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="deletedPagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="fetchDeletedCaseList"
        @current-change="fetchDeletedCaseList"
      />
    </el-card>

    <!-- 案件编辑对话框 -->
    <CaseDialog
      v-model="dialogVisible"
      :case-data="currentEditCase"
      @success="handleDialogSuccess"
    />

    <!-- 权限管理对话框 -->
    <PermissionDialog
      v-model="permissionDialogVisible"
      :case-id="currentCaseId"
      @success="handlePermissionDialogSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { caseApi } from '@/api/case'
import { useAuthStore } from '@/stores/auth'
import CaseDialog from './CaseDialog.vue'
import PermissionDialog from './PermissionDialog.vue'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)
const isAdmin = computed(() => currentUser.value?.role === 'admin')

const activeTab = ref('all')
const loading = ref(false)
const caseList = ref([])
const deletedCaseList = ref([])
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const currentEditCase = ref(null)
const currentCaseId = ref(null)

const searchForm = reactive({
  search: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const deletedPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取案件列表
async function fetchCaseList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }

    if (searchForm.search) {
      params.search = searchForm.search
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }

    const data = await caseApi.getCaseList(params)
    caseList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取案件列表失败')
  } finally {
    loading.value = false
  }
}

// 获取已删除案件列表
async function fetchDeletedCaseList() {
  loading.value = true
  try {
    const params = {
      page: deletedPagination.page,
      page_size: deletedPagination.page_size
    }

    const data = await caseApi.getDeletedCases(params)
    deletedCaseList.value = data.items || []
    deletedPagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取已删除案件列表失败')
  } finally {
    loading.value = false
  }
}

// 选项卡切换
function handleTabChange(tab) {
  if (tab === 'all') {
    fetchCaseList()
  } else if (tab === 'deleted') {
    fetchDeletedCaseList()
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  fetchCaseList()
}

// 重置
function handleReset() {
  searchForm.search = ''
  searchForm.status = ''
  pagination.page = 1
  fetchCaseList()
}

// 新增案件
function handleAdd() {
  currentEditCase.value = null
  dialogVisible.value = true
}

// 查看案件
function handleView(row) {
  ElMessage.info('查看案件详情功能待实现')
}

// 编辑案件
function handleEdit(row) {
  currentEditCase.value = { ...row }
  dialogVisible.value = true
}

// 权限管理
function handleManagePermissions(row) {
  currentCaseId.value = row.id
  permissionDialogVisible.value = true
}

// 归档案件
async function handleArchive(row) {
  try {
    await ElMessageBox.confirm(
      `确定要归档案件 "${row.case_name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await caseApi.archiveCase(row.id)
    ElMessage.success('归档成功')
    fetchCaseList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('归档失败')
    }
  }
}

// 删除案件（软删除，无需确认）
async function handleDelete(row) {
  try {
    await caseApi.deleteCase(row.id)
    ElMessage.success('删除成功')
    fetchCaseList()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 恢复案件
async function handleRestore(row) {
  try {
    await caseApi.restoreCase(row.id)
    ElMessage.success('恢复成功')
    fetchDeletedCaseList()
  } catch (error) {
    ElMessage.error('恢复失败')
  }
}

// 永久删除案件
async function handlePermanentDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要永久删除案件 "${row.case_name}" 吗？此操作将永久删除案件及其所有数据，不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )

    await caseApi.permanentDeleteCase(row.id)
    ElMessage.success('永久删除成功')
    fetchDeletedCaseList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('永久删除失败')
    }
  }
}

// 对话框成功回调
function handleDialogSuccess() {
  dialogVisible.value = false
  fetchCaseList()
}

// 权限对话框成功回调
function handlePermissionDialogSuccess() {
  permissionDialogVisible.value = false
}

// 权限判断
function canEdit(row) {
  return isAdmin.value || row.user_permission === 'admin'
}

function canManagePermissions(row) {
  return isAdmin.value || row.user_permission === 'admin'
}

function canArchive(row) {
  return (isAdmin.value || row.user_permission === 'admin') && row.status === 'active'
}

// 权限标签类型
function getPermissionTagType(permission) {
  const typeMap = {
    admin: 'danger',
    write: 'warning',
    read: 'info'
  }
  return typeMap[permission] || 'info'
}

// 权限标签文本
function getPermissionLabel(permission) {
  const labelMap = {
    admin: '管理员',
    write: '读写',
    read: '只读'
  }
  return labelMap[permission] || '未知'
}

onMounted(() => {
  fetchCaseList()
})
</script>

<style scoped lang="scss">
.case-management {
  padding: 20px;
}

.search-form {
  margin-bottom: 0;
}

.toolbar {
  margin-top: 20px;
}
</style>
