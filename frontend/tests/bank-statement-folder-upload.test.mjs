import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/BankStatement/index.vue'
)

const apiPath = path.resolve(
  process.cwd(),
  'frontend/src/api/bankStatement.js'
)

test('bank statement upload dialog supports selecting a folder directly', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /选择文件夹/,
    '上传弹窗应提供直接选择文件夹的入口'
  )

  assert.match(
    source,
    /webkitdirectory/,
    '目录选择输入框应启用 webkitdirectory 属性'
  )
})

test('bank statement upload keeps relative paths for folder uploads', () => {
  const apiSource = fs.readFileSync(apiPath, 'utf8')

  assert.match(
    apiSource,
    /formData\.append\('relative_paths_json'/,
    '目录上传时应通过单一 JSON 字段提交相对路径映射，避免 multipart 空字段触发 400'
  )

  assert.doesNotMatch(
    apiSource,
    /formData\.append\('relative_paths'/,
    '普通文件上传不应再逐项追加空的 relative_paths 字段'
  )
})
