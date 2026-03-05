<template>
  <el-dialog
    v-model="visible"
    :title="`清洗规则配置 - ${templateName}`"
    width="800px"
    @close="handleClose"
  >
    <div v-loading="loading">
      <!-- 规则列表 -->
      <el-table :data="rules" border>
        <el-table-column prop="rule_name" label="规则名称" width="150" />
        <el-table-column label="规则类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.rule_type === 'general' ? 'primary' : 'success'" size="small">
              {{ row.rule_type === 'general' ? '通用清洗' : '日期时间' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="regex_pattern" label="正则表达式" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row, $index }">
            <el-button size="small" @click="handleEdit(row, $index)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加规则按钮 -->
      <el-button type="primary" style="margin-top: 15px" @click="handleAdd">
        添加规则
      </el-button>

      <!-- 正则测试工具 -->
      <el-divider>正则表达式测试工具</el-divider>
      <el-form :model="testForm" label-width="100px">
        <el-form-item label="正则表达式">
          <el-input v-model="testForm.pattern" placeholder="输入正则表达式" />
        </el-form-item>
        <el-form-item label="测试数据">
          <el-input
            v-model="testForm.testData"
            type="textarea"
            :rows="3"
            placeholder="输入测试数据"
          />
        </el-form-item>
        <el-form-item label="清洗结果">
          <el-input
            :value="testResult"
            type="textarea"
            :rows="3"
            readonly
            placeholder="点击测试按钮查看结果"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleTest">测试</el-button>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>

    <!-- 编辑规则对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEdit ? '编辑规则' : '添加规则'"
      width="600px"
      append-to-body
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="规则名称" prop="rule_name">
          <el-input v-model="formData.rule_name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="formData.rule_type" placeholder="请选择规则类型">
            <el-option label="通用清洗" value="general">
              <div>
                <div>通用清洗</div>
                <div style="font-size: 12px; color: #999">
                  用于清洗字段中的特殊字符、空格等
                </div>
              </div>
            </el-option>
            <el-option label="日期时间清洗" value="datetime">
              <div>
                <div>日期时间清洗</div>
                <div style="font-size: 12px; color: #999">
                  用于清洗日期时间字段中的非数字字符
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="正则表达式" prop="regex_pattern">
          <el-input
            v-model="formData.regex_pattern"
            type="textarea"
            :rows="3"
            placeholder="请输入正则表达式"
          />
          <div style="font-size: 12px; color: #999; margin-top: 5px">
            示例 - 通用: \t| |"|\\\\|(nan)|\\|,<br>
            示例 - 日期: \D|\b0\b
          </div>
        </el-form-item>
        <el-form-item label="规则说明" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入规则说明"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { importRuleApi } from '@/api/importRule'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  templateId: {
    type: Number,
    default: null
  },
  templateName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const submitting = ref(false)
const rules = ref([])
const editDialogVisible = ref(false)
const isEdit = ref(false)
const currentIndex = ref(-1)
const formRef = ref(null)

const formData = reactive({
  rule_name: '',
  rule_type: 'general',
  regex_pattern: '',
  description: ''
})

const formRules = {
  rule_name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  rule_type: [
    { required: true, message: '请选择规则类型', trigger: 'change' }
  ],
  regex_pattern: [
    { required: true, message: '请输入正则表达式', trigger: 'blur' }
  ]
}

const testForm = reactive({
  pattern: '',
  testData: ''
})

const testResult = ref('')

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.templateId) {
    loadRules()
  }
})

// 加载清洗规则
async function loadRules() {
  loading.value = true
  try {
    const data = await importRuleApi.getCleaningRules(props.templateId)
    rules.value = data
  } catch (error) {
    ElMessage.error('加载清洗规则失败')
  } finally {
    loading.value = false
  }
}

// 添加规则
function handleAdd() {
  isEdit.value = false
  currentIndex.value = -1
  formData.rule_name = ''
  formData.rule_type = 'general'
  formData.regex_pattern = ''
  formData.description = ''
  editDialogVisible.value = true
}

// 编辑规则
function handleEdit(row, index) {
  isEdit.value = true
  currentIndex.value = index
  formData.rule_name = row.rule_name
  formData.rule_type = row.rule_type
  formData.regex_pattern = row.regex_pattern
  formData.description = row.description || ''
  editDialogVisible.value = true
}

// 删除规则
async function handleDelete(index) {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '删除确认', {
      type: 'warning'
    })

    const rule = rules.value[index]
    if (rule.id) {
      await importRuleApi.deleteCleaningRule(rule.id)
      ElMessage.success('删除成功')
      loadRules()
    } else {
      rules.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交规则
async function handleSubmit() {
  try {
    await formRef.value.validate()

    submitting.value = true

    const data = {
      rule_name: formData.rule_name,
      rule_type: formData.rule_type,
      regex_pattern: formData.regex_pattern,
      description: formData.description
    }

    if (isEdit.value && rules.value[currentIndex.value]?.id) {
      await importRuleApi.updateCleaningRule(
        rules.value[currentIndex.value].id,
        data
      )
    } else {
      await importRuleApi.createCleaningRule(props.templateId, data)
    }

    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    editDialogVisible.value = false
    loadRules()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

// 测试正则表达式
function handleTest() {
  if (!testForm.pattern) {
    ElMessage.warning('请输入正则表达式')
    return
  }
  if (!testForm.testData) {
    ElMessage.warning('请输入测试数据')
    return
  }

  try {
    const regex = new RegExp(testForm.pattern, 'g')
    testResult.value = testForm.testData.replace(regex, '')
  } catch (error) {
    ElMessage.error('正则表达式格式错误')
    testResult.value = '错误: ' + error.message
  }
}

// 关闭对话框
function handleClose() {
  visible.value = false
}
</script>
