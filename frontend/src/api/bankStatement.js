import request from './request'

export const bankStatementApi = {
  // 上传银行流水文件
  uploadBankStatements(caseId, files, templateId = null) {
    const formData = new FormData()
    const relativePaths = []

    files.forEach(item => {
      const rawFile = item.raw || item
      const relativePath = item.relativePath || rawFile.webkitRelativePath || ''

      formData.append('files', rawFile)

      if (relativePath) {
        relativePaths.push(relativePath)
      } else {
        relativePaths.push(null)
      }
    })

    if (templateId) {
      formData.append('template_id', templateId)
    }

    if (relativePaths.some(path => path)) {
      formData.append('relative_paths_json', JSON.stringify(relativePaths))
    }

    return request.post(`/v1/cases/${caseId}/bank-statements/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 600000, // 10分钟超时
      maxContentLength: 20 * 1024 * 1024 * 1024, // 20GB
      maxBodyLength: 20 * 1024 * 1024 * 1024 // 20GB
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
