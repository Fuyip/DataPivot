import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/CaseCardManagement/index.vue'
)

test('case card table hides sensitive identity columns', () => {
  const source = fs.readFileSync(componentPath, 'utf8')
  const tableTemplate = source.match(
    /<!-- 银行卡列表 -->[\s\S]*?<\/el-table>\s*<!-- 分页 -->/
  )?.[0]

  assert.ok(tableTemplate, '应能定位案件银行卡列表表格模板')
  assert.doesNotMatch(
    tableTemplate,
    /<el-table-column\s+prop="holder_id"\s+label="身份证号"/,
    '表格中不应显示身份证号列'
  )
  assert.doesNotMatch(
    tableTemplate,
    /<el-table-column\s+prop="phone"\s+label="手机号"/,
    '表格中不应显示手机号列'
  )
  assert.doesNotMatch(
    tableTemplate,
    /<el-table-column\s+prop="remark"\s+label="备注"/,
    '表格中不应显示备注列'
  )
})
