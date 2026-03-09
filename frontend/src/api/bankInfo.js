import request from './request'

/**
 * 银行信息管理 API
 */

// ==================== BankBin 相关接口 ====================

/**
 * 获取 BankBin 列表
 */
export function getBankBinList(params) {
  return request({
    url: '/v1/bank-info/bank-bin',
    method: 'get',
    params
  })
}

/**
 * 创建 BankBin
 */
export function createBankBin(data) {
  return request({
    url: '/v1/bank-info/bank-bin',
    method: 'post',
    data
  })
}

/**
 * 更新 BankBin
 */
export function updateBankBin(binCode, data) {
  return request({
    url: `/v1/bank-info/bank-bin/${binCode}`,
    method: 'put',
    data
  })
}

/**
 * 删除 BankBin
 */
export function deleteBankBin(binCode, params) {
  return request({
    url: `/v1/bank-info/bank-bin/${binCode}`,
    method: 'delete',
    params
  })
}

/**
 * 导出 BankBin
 */
export function exportBankBin(params) {
  return request({
    url: '/v1/bank-info/bank-bin/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 下载 BankBin 模板
 */
export function downloadBankBinTemplate() {
  return request({
    url: '/v1/bank-info/bank-bin/template',
    method: 'get',
    responseType: 'blob'
  })
}

// ==================== SyBank 相关接口 ====================

/**
 * 获取 SyBank 列表
 */
export function getSyBankList(params) {
  return request({
    url: '/v1/bank-info/sy-bank',
    method: 'get',
    params
  })
}

/**
 * 创建 SyBank
 */
export function createSyBank(data) {
  return request({
    url: '/v1/bank-info/sy-bank',
    method: 'post',
    data
  })
}

/**
 * 更新 SyBank
 */
export function updateSyBank(fromBank, sys, data) {
  return request({
    url: `/v1/bank-info/sy-bank/${encodeURIComponent(fromBank)}/${sys}`,
    method: 'put',
    data
  })
}

/**
 * 删除 SyBank
 */
export function deleteSyBank(fromBank, sys, params) {
  return request({
    url: `/v1/bank-info/sy-bank/${encodeURIComponent(fromBank)}/${sys}`,
    method: 'delete',
    params
  })
}

/**
 * 导出 SyBank
 */
export function exportSyBank(params) {
  return request({
    url: '/v1/bank-info/sy-bank/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * 下载 SyBank 模板
 */
export function downloadSyBankTemplate() {
  return request({
    url: '/v1/bank-info/sy-bank/template',
    method: 'get',
    responseType: 'blob'
  })
}

// ==================== 变更申请相关接口 ====================

/**
 * 获取变更申请列表
 */
export function getChangeRequests(params) {
  return request({
    url: '/v1/bank-info/change-requests',
    method: 'get',
    params
  })
}

/**
 * 批准变更申请
 */
export function approveChangeRequest(requestId, data) {
  return request({
    url: `/v1/bank-info/change-requests/${requestId}/approve`,
    method: 'post',
    data
  })
}

/**
 * 拒绝变更申请
 */
export function rejectChangeRequest(requestId, data) {
  return request({
    url: `/v1/bank-info/change-requests/${requestId}/reject`,
    method: 'post',
    data
  })
}

/**
 * 撤销变更申请
 */
export function deleteChangeRequest(requestId) {
  return request({
    url: `/v1/bank-info/change-requests/${requestId}`,
    method: 'delete'
  })
}

export default {
  getBankBinList,
  createBankBin,
  updateBankBin,
  deleteBankBin,
  exportBankBin,
  downloadBankBinTemplate,
  getSyBankList,
  createSyBank,
  updateSyBank,
  deleteSyBank,
  exportSyBank,
  downloadSyBankTemplate,
  getChangeRequests,
  approveChangeRequest,
  rejectChangeRequest,
  deleteChangeRequest
}
