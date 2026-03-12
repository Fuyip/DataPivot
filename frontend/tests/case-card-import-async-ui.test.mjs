import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/CaseCardManagement/index.vue'
)

test('case card import submit acknowledges background processing', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /ElMessage\.success\(['"`]文件上传成功，后台处理中['"`]\)/,
    '导入成功后应提示任务已转后台处理'
  )

  assert.match(
    source,
    /handleShowImportTasks\(\)|showImportTasks\.value = true/,
    '导入成功后应引导用户查看导入任务'
  )
})

test('case card import task dialog shows task status and progress', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /<el-table-column prop="status" label="状态"/,
    '导入任务列表应显示任务状态'
  )

  assert.match(
    source,
    /<el-table-column prop="progress" label="进度"/,
    '导入任务列表应显示任务进度'
  )

  assert.match(
    source,
    /getImportTaskStatusLabel|getImportTaskStatusTagType/,
    '页面应定义导入任务状态展示辅助函数'
  )
})

test('case card import tasks poll while jobs are running', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /setInterval\(/,
    '页面应在导入任务执行期间轮询刷新'
  )

  assert.match(
    source,
    /\['pending', 'processing'\]/,
    '轮询逻辑应关注等待中和处理中任务'
  )
})
