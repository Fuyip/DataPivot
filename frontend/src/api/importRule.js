/**
 * 导入规则管理 API
 */
import request from './request'

export const importRuleApi = {
  // ============ 模板管理 ============

  /**
   * 获取模板列表
   */
  getTemplateList(params) {
    return request.get('/v1/import-rules/templates', { params })
  },

  /**
   * 获取模板详情
   */
  getTemplateDetail(id) {
    return request.get(`/v1/import-rules/templates/${id}`)
  },

  /**
   * 创建模板
   */
  createTemplate(data) {
    return request.post('/v1/import-rules/templates', data)
  },

  /**
   * 更新模板
   */
  updateTemplate(id, data) {
    return request.put(`/v1/import-rules/templates/${id}`, data)
  },

  /**
   * 删除模板
   */
  deleteTemplate(id) {
    return request.delete(`/v1/import-rules/templates/${id}`)
  },

  /**
   * 设为默认模板
   */
  setDefaultTemplate(id) {
    return request.post(`/v1/import-rules/templates/${id}/set-default`)
  },

  /**
   * 复制模板
   */
  duplicateTemplate(id, newName) {
    return request.post(`/v1/import-rules/templates/${id}/duplicate`, null, {
      params: { new_name: newName }
    })
  },

  /**
   * 验证模板
   */
  validateTemplate(id) {
    return request.post(`/v1/import-rules/templates/${id}/validate`)
  },

  // ============ 字段映射管理 ============

  /**
   * 获取字段映射列表
   */
  getFieldMappings(templateId, dataType = null) {
    return request.get(`/v1/import-rules/templates/${templateId}/mappings`, {
      params: { data_type: dataType }
    })
  },

  /**
   * 批量保存字段映射
   */
  saveMappings(templateId, data) {
    return request.post(`/v1/import-rules/templates/${templateId}/mappings`, data)
  },

  /**
   * 更新单个字段映射
   */
  updateMapping(mappingId, data) {
    return request.put(`/v1/import-rules/mappings/${mappingId}`, data)
  },

  /**
   * 删除字段映射
   */
  deleteMapping(mappingId) {
    return request.delete(`/v1/import-rules/mappings/${mappingId}`)
  },

  // ============ 清洗规则管理 ============

  /**
   * 获取清洗规则列表
   */
  getCleaningRules(templateId) {
    return request.get(`/v1/import-rules/templates/${templateId}/cleaning-rules`)
  },

  /**
   * 创建清洗规则
   */
  createCleaningRule(templateId, data) {
    return request.post(`/v1/import-rules/templates/${templateId}/cleaning-rules`, data)
  },

  /**
   * 更新清洗规则
   */
  updateCleaningRule(ruleId, data) {
    return request.put(`/v1/import-rules/cleaning-rules/${ruleId}`, data)
  },

  /**
   * 删除清洗规则
   */
  deleteCleaningRule(ruleId) {
    return request.delete(`/v1/import-rules/cleaning-rules/${ruleId}`)
  },

  // ============ 辅助接口 ============

  /**
   * 获取支持的数据类型
   */
  getDataTypes() {
    return request.get('/v1/import-rules/data-types')
  },

  /**
   * 获取支持的字段类型
   */
  getFieldTypes() {
    return request.get('/v1/import-rules/field-types')
  },

  /**
   * 获取数据库字段定义
   */
  getDatabaseFields() {
    return request.get('/v1/import-rules/database-fields')
  }
}
