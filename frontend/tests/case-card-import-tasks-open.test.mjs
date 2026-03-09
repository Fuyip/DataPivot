import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/CaseCardManagement/index.vue'
)

test('opening the import task dialog triggers task loading', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /@click="handleShowImportTasks"/,
    '导入任务按钮应通过专门处理函数打开弹窗'
  )

  assert.match(
    source,
    /const handleShowImportTasks = \(\) => \{\s*showImportTasks\.value = true\s*loadImportTasks\(\)\s*\}/s,
    '打开导入任务弹窗时应立即加载任务列表'
  )
})

test('import task dialog supports viewing and exporting error reports', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /查看错误/,
    '导入任务列表应提供查看错误入口'
  )

  assert.match(
    source,
    /const showTaskErrors = \(task\) => \{/,
    '页面应定义查看错误详情处理函数'
  )

  assert.match(
    source,
    /const downloadErrorReport = \(errors\) => \{/,
    '页面应定义错误报告导出处理函数'
  )
})
