<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="isEdit ? '编辑案件' : '新增案件'"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="案件名称" prop="case_name">
        <el-input
          v-model="form.case_name"
          placeholder="请输入案件名称"
          maxlength="100"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="案件编号" prop="case_code">
        <el-input
          v-model="form.case_code"
          placeholder="系统自动生成"
          maxlength="5"
          disabled
        />
      </el-form-item>

      <el-form-item label="案件描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请输入案件描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="状态" prop="status" v-if="isEdit">
        <el-select v-model="form.status" style="width: 100%">
          <el-option label="进行中" value="active" />
          <el-option label="已归档" value="archived" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        {{ isEdit ? '更新' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { caseApi } from '@/api/case'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  caseData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const formRef = ref(null)
const submitting = ref(false)

const isEdit = computed(() => !!props.caseData?.id)

const form = reactive({
  case_name: '',
  case_code: '',
  description: '',
  status: 'active'
})

const rules = {
  case_name: [
    { required: true, message: '请输入案件名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  case_code: [
    { min: 5, max: 5, message: '案件编号必须为5个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '长度不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 监听对话框打开
watch(() => props.modelValue, (val) => {
  if (val) {
    if (props.caseData) {
      // 编辑模式
      form.case_name = props.caseData.case_name || ''
      form.case_code = props.caseData.case_code || ''
      form.description = props.caseData.description || ''
      form.status = props.caseData.status || 'active'
    } else {
      // 新增模式
      resetForm()
    }
  }
})

// 重置表单
function resetForm() {
  form.case_name = ''
  form.case_code = ''
  form.description = ''
  form.status = 'active'
  formRef.value?.clearValidate()
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value.validate()

    submitting.value = true

    if (isEdit.value) {
      // 更新案件
      await caseApi.updateCase(props.caseData.id, {
        case_name: form.case_name,
        description: form.description,
        status: form.status
      })
      ElMessage.success('案件更新成功')
    } else {
      // 创建案件 - 不传递 case_code，让后端自动生成
      const result = await caseApi.createCase({
        case_name: form.case_name,
        description: form.description
      })

      // 创建成功后，显示生成的案件编号
      if (result && result.case_code) {
        form.case_code = result.case_code
      }

      ElMessage.success('案件创建成功')
    }

    emit('success')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || (isEdit.value ? '案件更新失败' : '案件创建失败'))
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
function handleClose() {
  emit('update:modelValue', false)
}
</script>

<style scoped lang="scss">
</style>
