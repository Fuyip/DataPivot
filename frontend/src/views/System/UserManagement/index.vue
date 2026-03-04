<template>
  <div class="user-management">
    <el-card>
      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable style="width: 150px">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="激活" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 操作按钮 -->
      <div class="toolbar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>

      <!-- 用户表格 -->
      <el-table
        v-loading="loading"
        :data="userList"
        border
        stripe
        style="margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="full_name" label="姓名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.id === currentUser?.id"
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
        @size-change="fetchUserList"
        @current-change="fetchUserList"
      />
    </el-card>

    <!-- 用户编辑对话框 -->
    <UserDialog
      v-model="dialogVisible"
      :user="currentEditUser"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '@/api/user'
import { useAuthStore } from '@/stores/auth'
import UserDialog from './UserDialog.vue'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

const loading = ref(false)
const userList = ref([])
const dialogVisible = ref(false)
const currentEditUser = ref(null)

const searchForm = reactive({
  username: '',
  role: '',
  is_active: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取用户列表
async function fetchUserList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }

    // 添加搜索条件
    if (searchForm.username) {
      params.username = searchForm.username
    }
    if (searchForm.role) {
      params.role = searchForm.role
    }
    if (searchForm.is_active !== '') {
      params.is_active = searchForm.is_active
    }

    const data = await userApi.getUserList(params)
    userList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  fetchUserList()
}

// 重置
function handleReset() {
  searchForm.username = ''
  searchForm.role = ''
  searchForm.is_active = ''
  pagination.page = 1
  fetchUserList()
}

// 新增用户
function handleAdd() {
  currentEditUser.value = null
  dialogVisible.value = true
}

// 编辑用户
function handleEdit(row) {
  currentEditUser.value = { ...row }
  dialogVisible.value = true
}

// 删除用户
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await userApi.deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 重置密码
async function handleResetPassword(row) {
  try {
    const { value } = await ElMessageBox.prompt(
      `请输入用户 "${row.username}" 的新密码`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.{6,}/,
        inputErrorMessage: '密码长度不能少于 6 个字符'
      }
    )

    await userApi.resetPassword(row.id, value)
    ElMessage.success('密码重置成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('密码重置失败')
    }
  }
}

// 对话框成功回调
function handleDialogSuccess() {
  dialogVisible.value = false
  fetchUserList()
}

onMounted(() => {
  fetchUserList()
})
</script>

<style scoped lang="scss">
.user-management {
  padding: 20px;
}

.search-form {
  margin-bottom: 0;
}

.toolbar {
  margin-top: 20px;
}
</style>
