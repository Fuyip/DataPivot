import request from './request'

/**
 * 批量匹配银行卡归属
 */
export function batchMatchBanks(cardNumbers) {
  return request({
    url: '/v1/bank-cards/batch-match',
    method: 'post',
    data: {
      card_numbers: cardNumbers
    },
    timeout: 120000 // 2分钟超时
  })
}

/**
 * 导出匹配结果
 */
export function exportMatchResult(cardNumbers) {
  return request({
    url: '/v1/bank-cards/batch-match/export',
    method: 'post',
    data: {
      card_numbers: cardNumbers
    },
    responseType: 'blob',
    timeout: 120000 // 2分钟超时
  })
}
