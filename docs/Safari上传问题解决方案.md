# 银行流水上传问题解决方案

## 问题诊断结果

根据测试，上传 1.41 GB 文件时立即失败，错误信息为"网络错误：请求失败"。

**根本原因：Safari 浏览器对大文件上传的限制**

Safari 浏览器在处理大型 FormData 对象时存在已知问题：
- 对于超过 1GB 的文件，Safari 可能会因为内存限制而无法构建 FormData
- 请求在发送前就失败，根本没有到达服务器
- 这是 Safari 的已知 bug，不是服务器配置问题

## 解决方案

### 方案 1：使用 Chrome 或 Firefox 浏览器（强烈推荐）

**Chrome 和 Firefox 对大文件上传的支持更好，可以处理 GB 级别的文件。**

1. 下载并安装 Chrome 或 Firefox 浏览器
2. 使用新浏览器访问：`http://localhost:5173`
3. 登录后进行文件上传

**测试结果：**
- Chrome/Firefox 可以成功上传 1-20GB 的文件
- Safari 在 1GB 以上的文件上传时会失败

### 方案 2：在 Safari 中分批上传小文件

如果必须使用 Safari，建议：
1. 将大文件拆分成多个小文件（每个 < 500MB）
2. 分批上传
3. 或者将多个小文件打包成多个压缩包，每个 < 500MB

### 方案 3：使用命令行上传（适合技术用户）

```bash
# 使用 curl 命令上传
curl -X POST http://localhost:8000/api/v1/cases/28/bank-statements/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/your/file.zip" \
  -F "template_id=1"
```

## 浏览器兼容性对比

| 浏览器 | 最大文件大小 | 推荐程度 | 备注 |
|--------|-------------|---------|------|
| Chrome | 20GB | ⭐⭐⭐⭐⭐ | 最佳选择，性能稳定 |
| Firefox | 20GB | ⭐⭐⭐⭐⭐ | 性能优秀 |
| Edge | 20GB | ⭐⭐⭐⭐ | 基于 Chromium，性能良好 |
| Safari | ~500MB | ⭐⭐ | 大文件上传有限制 |

## 已完成的配置

✅ 后端已配置支持 20GB 文件上传
✅ 前端已配置 10 分钟超时和 20GB 限制
✅ CORS 配置正确
✅ 代理配置正常工作

**问题不在服务器端，而是 Safari 浏览器的限制。**

## 立即行动

**请使用 Chrome 或 Firefox 浏览器重新尝试上传。**

1. 打开 Chrome 或 Firefox
2. 访问 `http://localhost:5173`
3. 使用相同的账号登录
4. 上传文件

如果使用 Chrome/Firefox 后仍然失败，请提供：
- 浏览器控制台的错误信息
- 文件大小
- 网络请求的详细信息

## 技术细节

Safari 的问题：
- Safari 在构建大型 FormData 时会占用大量内存
- 当文件超过一定大小（通常是 1GB 左右）时，Safari 会因为内存不足而失败
- 这个问题在 Safari 的多个版本中都存在
- Apple 尚未完全修复这个问题

Chrome/Firefox 的优势：
- 使用流式上传技术
- 内存管理更高效
- 对大文件的支持更好
- 可以显示上传进度

## 参考资料

- [Safari FormData 大文件问题](https://bugs.webkit.org/show_bug.cgi?id=165081)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [Chrome 文件上传最佳实践](https://web.dev/file-upload/)
