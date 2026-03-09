import request from './request'

export const caseCardApi = {
  // 获取案件银行卡列表
  getCaseCardList(caseId, params) {
    return request.get(`/v1/cases/${caseId}/case-cards`, { params })
  },

  // 获取单个案件银行卡
  getCaseCard(caseId, cardId) {
    return request.get(`/v1/cases/${caseId}/case-cards/${cardId}`)
  },

  // 创建案件银行卡
  createCaseCard(caseId, data) {
    return request.post(`/v1/cases/${caseId}/case-cards`, data)
  },

  // 更新案件银行卡
  updateCaseCard(caseId, cardId, data) {
    return request.put(`/v1/cases/${caseId}/case-cards/${cardId}`, data)
  },

  // 删除案件银行卡
  deleteCaseCard(caseId, cardId) {
    return request.delete(`/v1/cases/${caseId}/case-cards/${cardId}`)
  },

  // 导出案件银行卡
  exportCaseCards(caseId) {
    return request.get(`/v1/cases/${caseId}/case-cards/export/excel`, {
      responseType: 'blob'
    })
  },

  // 下载导入模板
  downloadTemplate(caseId) {
    return request.get(`/v1/cases/${caseId}/case-cards/template/download`, {
      responseType: 'blob'
    })
  },

  // 导入案件银行卡
  importCaseCards(caseId, file) {
    const formData = new FormData()
    formData.append('file', file)

    return request.post(`/v1/cases/${caseId}/case-cards/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 根据卡号自动匹配银行名称
  matchBankName(caseId, cardNo) {
    return request.post(`/v1/cases/${caseId}/case-cards/match-bank`, { card_no: cardNo })
  },

  // 获取卡类型字典
  getCardTypes(caseId) {
    return request.get(`/v1/cases/${caseId}/case-cards/card-types`)
  },

  // 批量删除案件银行卡
  batchDeleteCaseCards(caseId, cardIds) {
    return request.post(`/v1/cases/${caseId}/case-cards/batch-delete`, { card_ids: cardIds })
  },

  // 获取导入任务列表
  getImportTasks(caseId, params) {
    return request.get(`/v1/cases/${caseId}/case-cards/import-tasks`, { params })
  },

  // 根据导入任务删除银行卡
  deleteCardsByTask(caseId, taskId) {
    return request.delete(`/v1/cases/${caseId}/case-cards/import-tasks/${taskId}`)
  },

  // 重新匹配未匹配的银行名称
  rematchUnmatchedBanks(caseId) {
    return request.post(`/v1/cases/${caseId}/case-cards/rematch-banks`)
  }
}
