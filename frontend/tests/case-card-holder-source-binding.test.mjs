import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const componentPath = path.resolve(
  process.cwd(),
  'frontend/src/views/System/CaseCardManagement/index.vue'
)

test('case card holder column binds to source field', () => {
  const source = fs.readFileSync(componentPath, 'utf8')

  assert.match(
    source,
    /<el-table-column prop="source" label="持卡人" width="120" \/>/,
    '持卡人列表列应绑定后端返回的 source 字段'
  )

  assert.match(
    source,
    /<el-form-item label="持卡人" prop="source">/,
    '持卡人表单项应绑定 source 字段'
  )

  assert.match(
    source,
    /v-model="formData\.source"/,
    '持卡人输入框应写入 formData.source'
  )
})
