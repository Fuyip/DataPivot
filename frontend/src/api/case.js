import request from './request'

export const caseApi = {
  // 获取案件列表
  getCaseList(params) {
    return request.get('/v1/cases', { params })
  },

  // 获取案件详情
  getCaseDetail(id) {
    return request.get(`/v1/cases/${id}`)
  },

  // 创建案件
  createCase(data) {
    return request.post('/v1/cases', data)
  },

  // 更新案件
  updateCase(id, data) {
    return request.put(`/v1/cases/${id}`, data)
  },

  // 删除案件（软删除）
  deleteCase(id) {
    return request.delete(`/v1/cases/${id}`, {
      params: { confirm: true }
    })
  },

  // 获取已删除案件列表
  getDeletedCases(params) {
    return request.get('/v1/cases/deleted/list', { params })
  },

  // 恢复已删除案件
  restoreCase(id) {
    return request.post(`/v1/cases/${id}/restore`)
  },

  // 永久删除案件
  permanentDeleteCase(id) {
    return request.delete(`/v1/cases/${id}/permanent`, {
      params: { confirm: true }
    })
  },

  // 归档案件
  archiveCase(id) {
    return request.post(`/v1/cases/${id}/archive`)
  },

  // 获取案件权限列表
  getCasePermissions(caseId) {
    return request.get(`/v1/cases/${caseId}/permissions`)
  },

  // 分配案件权限
  createCasePermission(caseId, data) {
    return request.post(`/v1/cases/${caseId}/permissions`, data)
  },

  // 更新案件权限
  updateCasePermission(caseId, permissionId, data) {
    return request.put(`/v1/cases/${caseId}/permissions/${permissionId}`, data)
  },

  // 撤销案件权限
  deleteCasePermission(caseId, permissionId) {
    return request.delete(`/v1/cases/${caseId}/permissions/${permissionId}`)
  },

  // 获取用户的案件列表
  getUserCases(userId) {
    return request.get(`/v1/cases/users/${userId}/cases`)
  }
}
