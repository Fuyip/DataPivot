<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑模板' : '新增模板'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="模板名称" prop="template_name">
        <el-input
          v-model="formData.template_name"
          placeholder="请输入模板名称"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="模板描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="4"
          placeholder="请输入模板描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="是否启用" prop="is_active">
        <el-switch v-model="formData.is_active" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { importRuleApi } from '@/api/importRule'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  templateData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref(null)
const submitting = ref(false)

const isEdit = computed(() => !!props.templateData?.id)

const formData = reactive({
  template_name: '',
  description: '',
  is_active: true
})

const rules = {
  template_name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ]
}

// 监听模板数据变化
watch(() => props.templateData, (newVal) => {
  if (newVal) {
    formData.template_name = newVal.template_name
    formData.description = newVal.description || ''
    formData.is_active = newVal.is_active
  } else {
    resetForm()
  }
}, { immediate: true })

// 重置表单
function resetForm() {
  formData.template_name = ''
  formData.description = ''
  formData.is_active = true
  formRef.value?.clearValidate()
}

// 关闭对话框
function handleClose() {
  visible.value = false
  resetForm()
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value.validate()

    submitting.value = true

    const data = {
      template_name: formData.template_name,
      description: formData.description,
      is_active: formData.is_active
    }

    if (isEdit.value) {
      await importRuleApi.updateTemplate(props.templateData.id, data)
    } else {
      await importRuleApi.createTemplate(data)
    }

    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}
</script>
