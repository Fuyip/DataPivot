# 银行流水上传失败诊断方案

## 问题现象
- 前端上传银行流水文件时，请求发送到 `http://localhost:5173/api/v1/cases/28/bank-statements/upload`
- 浏览器显示网络错误，没有响应标头
- curl 测试后端接口和代理都正常工作

## 可能的原因

### 1. 前端服务器代理未生效
**症状**: 请求被发送但没有正确代理到后端

**解决方案**:
```bash
# 停止前端服务 (Ctrl+C)
# 重新启动前端服务
cd /Users/yipf/DataPivot项目/DataPivot/frontend
npm run dev
```

### 2. 浏览器 CORS 问题
**症状**: 浏览器控制台显示 CORS 错误

**检查方法**:
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签页
- 查找红色的 CORS 相关错误信息

### 3. 文件太大导致超时
**症状**: 上传大文件时请求中断

**检查方法**:
- 尝试上传一个小文件（< 1MB）测试
- 如果小文件可以上传，说明是文件大小问题

**解决方案**: 需要调整 FastAPI 的文件大小限制

### 4. 请求格式问题
**症状**: FormData 格式不正确

**检查方法**:
- 在浏览器开发者工具的 Network 标签页
- 查看请求的 Payload 部分
- 确认 files 字段是否正确

## 立即尝试的步骤

### 步骤 1: 重启前端服务
```bash
# 在终端中找到运行前端的窗口，按 Ctrl+C 停止
# 然后重新运行
cd /Users/yipf/DataPivot项目/DataPivot/frontend
npm run dev
```

### 步骤 2: 清除浏览器缓存
- 在浏览器中按 Cmd+Shift+R (Mac) 强制刷新页面
- 或者清除浏览器缓存后重新访问

### 步骤 3: 检查浏览器控制台
1. 打开浏览器开发者工具 (F12 或 Cmd+Option+I)
2. 切换到 Console 标签页
3. 尝试上传文件
4. 查看是否有错误信息

### 步骤 4: 检查网络请求详情
1. 在开发者工具中切换到 Network 标签页
2. 尝试上传文件
3. 点击失败的请求
4. 查看以下信息：
   - Headers 标签：请求头和响应头
   - Payload 标签：请求体内容
   - Response 标签：响应内容（如果有）
   - Console 标签：是否有错误信息

## 临时测试方案

如果重启前端服务后仍然失败，可以尝试直接使用 curl 上传文件来验证后端：

```bash
# 替换 YOUR_TOKEN 为你的实际 token
# 替换 /path/to/your/file.zip 为实际文件路径
curl -X POST http://localhost:8000/api/v1/cases/28/bank-statements/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/your/file.zip" \
  -F "template_id=1"
```

如果 curl 可以成功上传，说明问题确实在前端。

## 需要提供的信息

请提供以下信息以便进一步诊断：

1. 浏览器控制台的完整错误信息（截图或文字）
2. Network 标签页中失败请求的详细信息
3. 上传的文件大小
4. 重启前端服务后是否仍然失败
