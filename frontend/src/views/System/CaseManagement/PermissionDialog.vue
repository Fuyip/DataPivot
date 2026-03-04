<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="案件权限管理"
    width="800px"
    :close-on-click-modal="false"
  >
    <div class="permission-dialog">
      <!-- 添加权限表单 -->
      <el-card class="add-permission-card" shadow="never">
        <template #header>
          <span>添加权限</span>
        </template>
        <el-form :inline="true" :model="addForm" ref="addFormRef">
          <el-form-item label="用户" prop="user_id">
            <el-select
              v-model="addForm.user_id"
              placeholder="请选择用户"
              filterable
              style="width: 200px"
            >
              <el-option
                v-for="user in availableUsers"
                :key="user.id"
                :label="`${user.username} (${user.full_name})`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="权限级别" prop="permission_level">
            <el-select v-model="addForm.permission_level" placeholder="请选择权限" style="width: 150px">
              <el-option label="管理员" value="admin" />
              <el-option label="读写" value="write" />
              <el-option label="只读" value="read" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleAddPermission">添加</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 权限列表 -->
      <el-card class="permission-list-card" shadow="never" style="margin-top: 20px">
        <template #header>
          <span>已分配权限</span>
        </template>
        <el-table
          v-loading="loading"
          :data="permissionList"
          border
          stripe
          max-height="400"
        >
          <el-table-column prop="user_name" label="用户名" width="120" />
          <el-table-column prop="user_full_name" label="姓名" width="120" />
          <el-table-column prop="permission_level" label="权限级别" width="120">
            <template #default="{ row }">
              <el-tag :type="getPermissionTagType(row.permission_level)">
                {{ getPermissionLabel(row.permission_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="granted_by_name" label="授权人" width="120" />
          <el-table-column prop="granted_at" label="授权时间" width="180" />
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                @click="handleEditPermission(row)"
              >
                修改权限
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="handleDeletePermission(row)"
              >
                撤销
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>

    <!-- 修改权限对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="修改权限级别"
      width="400px"
      append-to-body
    >
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="用户">
          <span>{{ currentEditPermission?.user_name }} ({{ currentEditPermission?.user_full_name }})</span>
        </el-form-item>
        <el-form-item label="权限级别">
          <el-select v-model="editForm.permission_level" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="读写" value="write" />
            <el-option label="只读" value="read" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdatePermission">确定</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { caseApi } from '@/api/case'
import { userApi } from '@/api/user'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  caseId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const loading = ref(false)
const permissionList = ref([])
const allUsers = ref([])
const editDialogVisible = ref(false)
const currentEditPermission = ref(null)

const addForm = reactive({
  user_id: null,
  permission_level: 'read'
})

const editForm = reactive({
  permission_level: ''
})

// 可选用户列表（排除已有权限的用户）
const availableUsers = computed(() => {
  const assignedUserIds = permissionList.value.map(p => p.user_id)
  return allUsers.value.filter(u => !assignedUserIds.includes(u.id))
})

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  if (val && props.caseId) {
    fetchPermissionList()
    fetchAllUsers()
  }
})

// 获取权限列表
async function fetchPermissionList() {
  loading.value = true
  try {
    const data = await caseApi.getCasePermissions(props.caseId)
    permissionList.value = data.items || []
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

// 获取所有用户
async function fetchAllUsers() {
  try {
    const data = await userApi.getUserList({ page: 1, page_size: 1000 })
    allUsers.value = data.items || []
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 添加权限
async function handleAddPermission() {
  if (!addForm.user_id) {
    ElMessage.warning('请选择用户')
    return
  }
  if (!addForm.permission_level) {
    ElMessage.warning('请选择权限级别')
    return
  }

  try {
    await caseApi.createCasePermission(props.caseId, {
      user_id: addForm.user_id,
      permission_level: addForm.permission_level
    })
    ElMessage.success('权限添加成功')
    addForm.user_id = null
    addForm.permission_level = 'read'
    fetchPermissionList()
  } catch (error) {
    ElMessage.error(error.message || '权限添加失败')
  }
}

// 编辑权限
function handleEditPermission(row) {
  currentEditPermission.value = row
  editForm.permission_level = row.permission_level
  editDialogVisible.value = true
}

// 更新权限
async function handleUpdatePermission() {
  try {
    await caseApi.updateCasePermission(
      props.caseId,
      currentEditPermission.value.id,
      { permission_level: editForm.permission_level }
    )
    ElMessage.success('权限更新成功')
    editDialogVisible.value = false
    fetchPermissionList()
  } catch (error) {
    ElMessage.error(error.message || '权限更新失败')
  }
}

// 删除权限
async function handleDeletePermission(row) {
  try {
    await ElMessageBox.confirm(
      `确定要撤销用户 "${row.user_name}" 的权限吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await caseApi.deleteCasePermission(props.caseId, row.id)
    ElMessage.success('权限撤销成功')
    fetchPermissionList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '权限撤销失败')
    }
  }
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
  emit('success')
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
</script>

<style scoped lang="scss">
.permission-dialog {
  .add-permission-card {
    :deep(.el-card__header) {
      padding: 12px 20px;
      background-color: #f5f7fa;
    }
  }

  .permission-list-card {
    :deep(.el-card__header) {
      padding: 12px 20px;
      background-color: #f5f7fa;
    }
  }
}
</style>
