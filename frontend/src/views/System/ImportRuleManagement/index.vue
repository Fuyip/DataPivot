<template>
  <div class="import-rule-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入规则管理</span>
          <el-button type="primary" @click="handleCreate">新增模板</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="模板名称或描述"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 模板列表 -->
      <el-table :data="templateList" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="template_name" label="模板名称" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small" style="margin-right: 8px">
              默认
            </el-tag>
            {{ row.template_name }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="统计" width="200">
          <template #default="{ row }">
            <div style="font-size: 12px; color: #666">
              字段: {{ row.field_mapping_count }} |
              规则: {{ row.cleaning_rule_count }} |
              使用: {{ row.usage_count }}次
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handleConfigMapping(row)">字段映射</el-button>
            <el-button size="small" @click="handleConfigCleaning(row)">清洗规则</el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="setDefault" :disabled="row.is_default">
                    设为默认
                  </el-dropdown-item>
                  <el-dropdown-item command="duplicate">复制</el-dropdown-item>
                  <el-dropdown-item command="validate">验证</el-dropdown-item>
                  <el-dropdown-item command="delete" :disabled="row.is_default">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 模板编辑对话框 -->
    <template-dialog
      v-model="dialogVisible"
      :template-data="currentTemplate"
      @success="handleSearch"
    />

    <!-- 字段映射配置对话框 -->
    <field-mapping-dialog
      v-model="mappingDialogVisible"
      :template-id="currentTemplateId"
      :template-name="currentTemplateName"
    />

    <!-- 清洗规则配置对话框 -->
    <cleaning-rule-dialog
      v-model="cleaningDialogVisible"
      :template-id="currentTemplateId"
      :template-name="currentTemplateName"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import { importRuleApi } from '@/api/importRule'
import TemplateDialog from './TemplateDialog.vue'
import FieldMappingDialog from './FieldMappingDialog.vue'
import CleaningRuleDialog from './CleaningRuleDialog.vue'

const loading = ref(false)
const templateList = ref([])
const dialogVisible = ref(false)
const mappingDialogVisible = ref(false)
const cleaningDialogVisible = ref(false)
const currentTemplate = ref(null)
const currentTemplateId = ref(null)
const currentTemplateName = ref('')

const searchForm = reactive({
  search: '',
  is_active: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 加载模板列表
async function loadTemplates() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      search: searchForm.search || undefined,
      is_active: searchForm.is_active
    }
    const data = await importRuleApi.getTemplateList(params)
    templateList.value = data.items || []
    pagination.total = data.total || 0
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  loadTemplates()
}

// 重置
function handleReset() {
  searchForm.search = ''
  searchForm.is_active = null
  handleSearch()
}

// 新增模板
function handleCreate() {
  currentTemplate.value = null
  dialogVisible.value = true
}

// 编辑模板
function handleEdit(row) {
  currentTemplate.value = { ...row }
  dialogVisible.value = true
}

// 配置字段映射
function handleConfigMapping(row) {
  currentTemplateId.value = row.id
  currentTemplateName.value = row.template_name
  mappingDialogVisible.value = true
}

// 配置清洗规则
function handleConfigCleaning(row) {
  currentTemplateId.value = row.id
  currentTemplateName.value = row.template_name
  cleaningDialogVisible.value = true
}

// 下拉菜单命令
async function handleCommand(command, row) {
  switch (command) {
    case 'setDefault':
      await handleSetDefault(row)
      break
    case 'duplicate':
      await handleDuplicate(row)
      break
    case 'validate':
      await handleValidate(row)
      break
    case 'delete':
      await handleDelete(row)
      break
  }
}

// 设为默认
async function handleSetDefault(row) {
  try {
    await importRuleApi.setDefaultTemplate(row.id)
    ElMessage.success('已设为默认模板')
    loadTemplates()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 复制模板
async function handleDuplicate(row) {
  const { value: newName } = await ElMessageBox.prompt('请输入新模板名称', '复制模板', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.+/,
    inputErrorMessage: '模板名称不能为空'
  })

  if (newName) {
    try {
      await importRuleApi.duplicateTemplate(row.id, newName)
      ElMessage.success('模板复制成功')
      loadTemplates()
    } catch (error) {
      ElMessage.error('复制失败')
    }
  }
}

// 验证模板
async function handleValidate(row) {
  try {
    const result = await importRuleApi.validateTemplate(row.id)
    if (result.valid) {
      ElMessage.success('模板验证通过')
    } else {
      let message = '模板验证失败:\n'
      if (result.errors.length > 0) {
        message += '\n错误:\n' + result.errors.join('\n')
      }
      if (result.warnings.length > 0) {
        message += '\n\n警告:\n' + result.warnings.join('\n')
      }
      ElMessageBox.alert(message, '验证结果', { type: 'warning' })
    }
  } catch (error) {
    ElMessage.error('验证失败')
  }
}

// 删除模板
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板"${row.template_name}"吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning' }
    )

    await importRuleApi.deleteTemplate(row.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.import-rule-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
