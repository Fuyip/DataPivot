<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑用户' : '新增用户'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          placeholder="请输入用户名"
          :disabled="isEdit"
        />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="formData.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>

      <el-form-item label="姓名" prop="full_name">
        <el-input
          v-model="formData.full_name"
          placeholder="请输入姓名"
        />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="formData.email"
          placeholder="请输入邮箱"
        />
      </el-form-item>

      <el-form-item label="角色" prop="role">
        <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
      </el-form-item>

      <el-form-item label="状态" prop="is_active">
        <el-switch
          v-model="formData.is_active"
          active-text="激活"
          inactive-text="禁用"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api/user'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const loading = ref(false)

const isEdit = computed(() => !!props.user)

const formData = reactive({
  username: '',
  password: '',
  full_name: '',
  email: '',
  role: 'user',
  is_active: true
})

// 邮箱验证规则
const validateEmail = (rule, value, callback) => {
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入正确的邮箱格式'))
  } else {
    callback()
  }
}

const formRules = computed(() => ({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' }
  ],
  password: isEdit.value
    ? [{ min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }]
    : [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
      ],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}))

// 监听用户数据变化
watch(
  () => props.user,
  (newUser) => {
    if (newUser) {
      formData.username = newUser.username || ''
      formData.password = ''
      formData.full_name = newUser.full_name || ''
      formData.email = newUser.email || ''
      formData.role = newUser.role || 'user'
      formData.is_active = newUser.is_active !== false
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

// 重置表单
function resetForm() {
  formData.username = ''
  formData.password = ''
  formData.full_name = ''
  formData.email = ''
  formData.role = 'user'
  formData.is_active = true
  formRef.value?.clearValidate()
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
  resetForm()
}

// 提交表单
async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      const data = {
        username: formData.username,
        full_name: formData.full_name || null,
        email: formData.email || null,
        role: formData.role,
        is_active: formData.is_active
      }

      // 新增时必须包含密码，编辑时如果填写了密码则更新
      if (!isEdit.value) {
        data.password = formData.password
      } else if (formData.password) {
        data.password = formData.password
      }

      if (isEdit.value) {
        await userApi.updateUser(props.user.id, data)
        ElMessage.success('更新成功')
      } else {
        await userApi.createUser(data)
        ElMessage.success('创建成功')
      }

      emit('success')
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      loading.value = false
    }
  })
}
</script>
