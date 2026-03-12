import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/BankStatement/index.vue'
)

test('bank statement task detail uses CSV terminology consistently', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /label="已处理CSV"/,
    '任务详情应明确显示已处理 CSV 数'
  )

  assert.match(
    source,
    /label="CSV总数"/,
    '任务详情应明确显示 CSV 总数'
  )

  assert.doesNotMatch(
    source,
    /\{\{\s*currentTask\.processed_files\s*\}\}\s*\/\s*\{\{\s*currentTask\.total_files\s*\}\}/,
    '详情区不应再沿用上传文件数与 CSV 文件数混算的展示方式'
  )
})
