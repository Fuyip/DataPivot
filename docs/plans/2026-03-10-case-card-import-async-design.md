# Case Card Async Import Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将“案件银行卡管理”的 Excel 导入从同步请求改为后台任务处理，避免大量数据导入时接口超时。

**Architecture:** 复用现有 Celery 基础设施，为 `import_task` 增加状态/进度字段，并新增案件银行卡导入异步任务。上传接口只负责保存文件、创建任务记录并投递 Celery 任务；前端导入任务弹窗负责展示状态并轮询刷新。

**Tech Stack:** FastAPI, SQLAlchemy, Celery, Redis, Vue 3, Element Plus, Node test, pytest

---

### Task 1: 先写失败测试锁定异步导入行为

**Files:**
- Create: `backend/tests/test_case_card_import_async.py`
- Create: `frontend/tests/case-card-import-async-ui.test.mjs`

**Step 1: Write the failing backend test**

验证上传接口会调用异步入队逻辑，并立即返回任务信息，而不是同步返回成功/失败统计。

**Step 2: Run test to verify it fails**

Run: `./venv/bin/pytest backend/tests/test_case_card_import_async.py -q`

**Step 3: Write the failing frontend test**

验证前端提交导入后提示“后台处理中”，并具备状态列/进度列与轮询逻辑。

**Step 4: Run test to verify it fails**

Run: `node --test frontend/tests/case-card-import-async-ui.test.mjs`

### Task 2: 为 import_task 增加后台任务元数据

**Files:**
- Modify: `backend/models/import_task.py`
- Modify: `backend/services/import_task_service.py`
- Create: `migrations/alter_import_task_async_fields.sql`

**Step 1: Add fields**

增加 `status`, `progress`, `current_step`, `started_at`, `completed_at`, `error_message`, `storage_path`, `task_ref`。

**Step 2: Update task query methods**

任务列表/单任务查询返回状态和进度字段，并在删除前校验不能删除进行中的任务。

### Task 3: 新增案件银行卡异步导入任务

**Files:**
- Create: `backend/tasks/case_card_import_tasks.py`
- Modify: `backend/core/celery_app.py`
- Modify: `backend/services/case_card_service.py`
- Modify: `backend/api/v1/case_cards.py`

**Step 1: Save upload file and create pending task**

上传接口保存 Excel 文件，创建 `import_task` 记录，调用 Celery `delay(...)`。

**Step 2: Move synchronous import logic into background processor**

后台任务负责读取 Excel、更新总数、逐行入库、更新成功/失败统计与错误详情、记录进度。

**Step 3: Keep existing import semantics**

保留现有字段校验、银行卡去重、卡类型校验和错误报告逻辑。

### Task 4: 升级前端导入任务弹窗

**Files:**
- Modify: `frontend/src/views/System/CaseCardManagement/index.vue`

**Step 1: Submit import as async job**

导入提交成功后提示“文件已上传，后台处理中”，自动打开导入任务弹窗。

**Step 2: Show task status**

任务表增加状态、进度、当前步骤列，并禁用进行中任务的删除按钮。

**Step 3: Poll until settled**

当弹窗打开且存在 `pending/processing` 任务时，定时刷新任务列表；全部结束后停止轮询。

### Task 5: 验证

**Files:**
- Test: `backend/tests/test_case_card_import_async.py`
- Test: `frontend/tests/case-card-import-async-ui.test.mjs`

**Step 1: Run backend tests**

Run: `./venv/bin/pytest backend/tests/test_case_card_import_async.py -q`

**Step 2: Run frontend tests**

Run: `node --test frontend/tests/case-card-import-async-ui.test.mjs frontend/tests/case-card-import-tasks-open.test.mjs frontend/tests/case-card-table-columns.test.mjs`

**Step 3: Build frontend**

Run: `npm run build`
