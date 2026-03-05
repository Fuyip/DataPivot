<template>
  <el-dialog
    v-model="visible"
    :title="`字段映射配置 - ${templateName}`"
    width="90%"
    top="5vh"
    @close="handleClose"
  >
    <el-tabs v-model="activeDataType" v-loading="loading">
      <el-tab-pane
        v-for="dataType in dataTypes"
        :key="dataType.name"
        :label="`${dataType.name} (${getMappingCount(dataType.name)})`"
        :name="dataType.name"
      >
        <div style="margin-bottom: 10px; color: #666; font-size: 13px">
          {{ dataType.description }}
        </div>

        <!-- 字段映射表格 -->
        <el-table :data="getMappings(dataType.name)" border max-height="500">
          <el-table-column label="排序" width="60" align="center">
            <template #default>
              <el-icon class="drag-handle" style="cursor: move">
                <Rank />
              </el-icon>
            </template>
          </el-table-column>

          <el-table-column label="数据库字段" width="200">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 8px">
                <span style="color: #606266">{{ getFieldLabel(row.db_field_name, activeDataType) }}</span>
                <span style="color: #999; font-size: 12px">({{ row.db_field_name }})</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="CSV列名" width="200">
            <template #default="{ row }">
              <el-input v-model="row.csv_column_name" size="small" />
            </template>
          </el-table-column>

          <el-table-column label="字段类型" width="150">
            <template #default="{ row }">
              <el-select v-model="row.field_type" size="small">
                <el-option
                  v-for="type in fieldTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                >
                  <span>{{ type.label }}</span>
                  <span style="color: #999; font-size: 12px; margin-left: 8px">
                    {{ type.description }}
                  </span>
                </el-option>
              </el-select>
            </template>
          </el-table-column>

          <el-table-column label="必填" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox v-model="row.is_required" />
            </template>
          </el-table-column>

          <el-table-column label="默认值" width="150">
            <template #default="{ row }">
              <el-input v-model="row.default_value" size="small" placeholder="可选" />
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ $index }">
              <el-button
                size="small"
                type="danger"
                link
                @click="handleDeleteMapping(dataType.name, $index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 添加字段按钮 -->
        <el-button
          type="primary"
          size="small"
          style="margin-top: 10px"
          @click="handleAddMapping(dataType.name)"
        >
          添加字段
        </el-button>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div style="display: flex; justify-content: space-between; align-items: center">
        <div>
          <el-button size="small" @click="handleImport">导入配置</el-button>
          <el-button size="small" @click="handleExport">导出配置</el-button>
        </div>
        <div>
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存配置
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
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
const saving = ref(false)
const activeDataType = ref('人员信息')
const mappings = reactive({})
const dataTypes = ref([])
const fieldTypes = ref([])
const databaseFields = ref({})

// 获取指定数据类型的映射
const getMappings = (dataType) => {
  return mappings[dataType] || []
}

// 获取映射数量
const getMappingCount = (dataType) => {
  return getMappings(dataType).length
}

// 获取指定数据类型的数据库字段选项
const getDatabaseFieldOptions = (dataType) => {
  return databaseFields.value[dataType] || []
}

// 获取字段的显示标签
const getFieldLabel = (fieldName, dataType) => {
  const fields = getDatabaseFieldOptions(dataType)
  const field = fields.find(f => f.field === fieldName)
  return field ? field.label : fieldName
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.templateId) {
    loadDataTypes()
    loadFieldTypes()
    loadDatabaseFields()
    loadMappings()
  }
})

// 加载数据类型列表
async function loadDataTypes() {
  try {
    const data = await importRuleApi.getDataTypes()
    dataTypes.value = data
  } catch (error) {
    ElMessage.error('加载数据类型失败')
  }
}

// 加载字段类型列表
async function loadFieldTypes() {
  try {
    const data = await importRuleApi.getFieldTypes()
    fieldTypes.value = data
  } catch (error) {
    ElMessage.error('加载字段类型失败')
  }
}

// 加载数据库字段定义
async function loadDatabaseFields() {
  try {
    const data = await importRuleApi.getDatabaseFields()
    databaseFields.value = data
  } catch (error) {
    ElMessage.error('加载数据库字段失败')
  }
}

// 加载字段映射
async function loadMappings() {
  loading.value = true
  try {
    const data = await importRuleApi.getFieldMappings(props.templateId)
    Object.assign(mappings, data)
    // 初始化拖拽排序
    await nextTick()
    initSortable()
  } catch (error) {
    ElMessage.error('加载字段映射失败')
  } finally {
    loading.value = false
  }
}

// 初始化拖拽排序
function initSortable() {
  const tables = document.querySelectorAll('.el-table__body-wrapper tbody')
  tables.forEach((tbody) => {
    Sortable.create(tbody, {
      handle: '.drag-handle',
      animation: 150,
      onEnd: ({ oldIndex, newIndex }) => {
        const currentMappings = getMappings(activeDataType.value)
        const movedItem = currentMappings.splice(oldIndex, 1)[0]
        currentMappings.splice(newIndex, 0, movedItem)
        // 更新排序顺序
        currentMappings.forEach((item, index) => {
          item.sort_order = index
        })
      }
    })
  })
}

// 添加字段映射
function handleAddMapping(dataType) {
  if (!mappings[dataType]) {
    mappings[dataType] = []
  }

  // 获取该数据类型的预定义字段列表
  const availableFields = getDatabaseFieldOptions(dataType)

  // 找出已使用的字段
  const usedFields = new Set(mappings[dataType].map(m => m.db_field_name))

  // 找到第一个未使用的字段
  const nextField = availableFields.find(f => !usedFields.has(f.field))

  if (!nextField) {
    ElMessage.warning('该数据类型的所有预定义字段已添加完毕')
    return
  }

  mappings[dataType].push({
    data_type: dataType,
    db_field_name: nextField.field,
    csv_column_name: '',
    field_type: 'str',
    sort_order: mappings[dataType].length,
    is_required: false,
    default_value: ''
  })
}

// 删除字段映射
function handleDeleteMapping(dataType, index) {
  mappings[dataType].splice(index, 1)
  // 更新排序顺序
  mappings[dataType].forEach((item, idx) => {
    item.sort_order = idx
  })
}

// 保存配置
async function handleSave() {
  // 验证必填字段
  for (const dataType of dataTypes.value) {
    const items = getMappings(dataType.name)
    for (const item of items) {
      if (!item.db_field_name || !item.csv_column_name) {
        ElMessage.warning(`${dataType.name}中存在未填写的字段`)
        activeDataType.value = dataType.name
        return
      }
    }
  }

  saving.value = true
  try {
    // 批量保存所有数据类型的映射
    for (const dataType of dataTypes.value) {
      const items = getMappings(dataType.name)
      if (items.length > 0) {
        await importRuleApi.saveMappings(props.templateId, {
          data_type: dataType.name,
          mappings: items
        })
      }
    }
    ElMessage.success('配置保存成功')
    handleClose()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 导入配置
async function handleImport() {
  try {
    const { value: jsonStr } = await ElMessageBox.prompt(
      '请粘贴JSON配置',
      '导入配置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea'
      }
    )

    if (jsonStr) {
      const importedData = JSON.parse(jsonStr)
      Object.assign(mappings, importedData)
      ElMessage.success('导入成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导入失败，请检查JSON格式')
    }
  }
}

// 导出配置
function handleExport() {
  const jsonStr = JSON.stringify(mappings, null, 2)
  navigator.clipboard.writeText(jsonStr).then(() => {
    ElMessage.success('配置已复制到剪贴板')
  }).catch(() => {
    ElMessageBox.alert(jsonStr, '导出配置', {
      confirmButtonText: '关闭'
    })
  })
}

// 关闭对话框
function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.drag-handle {
  font-size: 18px;
  color: #999;
}

.drag-handle:hover {
  color: #409eff;
}
</style>
