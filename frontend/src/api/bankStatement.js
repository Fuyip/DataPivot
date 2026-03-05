import request from './request'

export const bankStatementApi = {
  // 上传银行流水文件
  uploadBankStatements(caseId, files, templateId = null) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    if (templateId) {
      formData.append('template_id', templateId)
    }

    return request.post(`/v1/cases/${caseId}/bank-statements/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000 // 5分钟超时
    })
  },

  // 查询任务进度
  getTaskProgress(caseId, taskId) {
    return request.get(`/v1/cases/${caseId}/bank-statements/tasks/${taskId}`)
  },

  // 查询任务列表
  getTaskList(caseId, params) {
    return request.get(`/v1/cases/${caseId}/bank-statements/tasks`, { params })
  },

  // 取消任务
  cancelTask(caseId, taskId) {
    return request.post(`/v1/cases/${caseId}/bank-statements/tasks/${taskId}/cancel`)
  },

  // 删除任务记录
  deleteTask(caseId, taskId) {
    return request.delete(`/v1/cases/${caseId}/bank-statements/tasks/${taskId}`)
  },

  // 获取导入统计
  getStatistics(caseId) {
    return request.get(`/v1/cases/${caseId}/bank-statements/statistics`)
  }
}
