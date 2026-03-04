# 数枢 (DataPivot) API接口设计文档

## 1. 接口规范

### 1.1 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 1.2 统一响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 业务数据
  }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

#### 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 1.3 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

### 1.4 认证方式

使用JWT Bearer Token认证：
```
Authorization: Bearer <token>
```

## 2. 认证模块

### 2.1 用户登录

**接口**: `POST /auth/login`

**请求参数**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### 2.2 刷新Token

**接口**: `POST /auth/refresh`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "new_token",
    "expires_in": 3600
  }
}
```

### 2.3 退出登录

**接口**: `POST /auth/logout`

**请求头**: `Authorization: Bearer <token>`

**响应**:
```json
{
  "code": 200,
  "message": "退出成功",
  "data": null
}
```

## 3. 银行流水模块

### 3.1 上传银行流水文件

**接口**: `POST /bank/upload`

**请求类型**: `multipart/form-data`

**请求参数**:
- `file`: 文件对象（支持zip、rar、csv、xlsx）
- `bank_name`: 银行名称（可选）

**响应**:
```json
{
  "code": 200,
  "message": "文件上传成功",
  "data": {
    "task_id": "task_123456",
    "filename": "bank_data.zip",
    "status": "processing"
  }
}
```

### 3.2 查询处理任务状态

**接口**: `GET /bank/task/{task_id}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_123456",
    "status": "completed",
    "progress": 100,
    "result": {
      "total_records": 10000,
      "success_records": 9950,
      "error_records": 50,
      "error_files": ["file1.csv", "file2.csv"]
    }
  }
}
```

### 3.3 查询交易明细

**接口**: `GET /bank/transactions`

**请求参数**:
- `card_no`: 卡号（可选）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `min_amount`: 最小金额（可选）
- `max_amount`: 最大金额（可选）
- `trade_tag`: 交易方向 in/out（可选）
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "card_no": "6222021234567890",
        "account_name": "张三",
        "trade_date": "2024-03-01 10:30:00",
        "trade_money": 1000.00,
        "trade_balance": 5000.00,
        "dict_trade_tag": "in",
        "rival_card_no": "6228481234567890",
        "rival_card_name": "李四",
        "summary_description": "转账"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 3.4 资金穿透分析

**接口**: `POST /bank/fund-trace`

**请求参数**:
```json
{
  "card_no": "6222021234567890",
  "depth": 3,
  "min_amount": 1000,
  "start_date": "2024-01-01",
  "end_date": "2024-03-01"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": "card_1",
        "card_no": "6222021234567890",
        "name": "张三",
        "level": 0
      }
    ],
    "edges": [
      {
        "source": "card_1",
        "target": "card_2",
        "amount": 10000,
        "count": 5
      }
    ]
  }
}
```

### 3.5 导出交易报告

**接口**: `POST /bank/export`

**请求参数**:
```json
{
  "card_no": "6222021234567890",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01",
  "format": "xlsx"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "download_url": "/downloads/report_20240301.xlsx",
    "expires_at": "2024-03-01 18:00:00"
  }
}
```

## 4. 人员分析模块

### 4.1 导入人员数据

**接口**: `POST /person/import`

**请求类型**: `multipart/form-data`

**请求参数**:
- `file`: Excel文件
- `data_type`: 数据类型（云搜基本信息/云搜综合信息/微信好友等）

**响应**:
```json
{
  "code": 200,
  "message": "导入成功",
  "data": {
    "total": 100,
    "success": 95,
    "failed": 5
  }
}
```

### 4.2 查询人员信息

**接口**: `GET /person/info`

**请求参数**:
- `keyword`: 关键词（姓名/身份证/手机号）
- `page`: 页码
- `page_size`: 每页数量

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "accounts": ["wx_123", "qq_456"],
        "sources": ["云搜", "微信好友"]
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

### 4.3 共同好友分析

**接口**: `POST /person/common-friends`

**请求参数**:
```json
{
  "platform": "微信",
  "min_subjects": 2
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "common_friends": [
      {
        "friend_id": "wx_friend_123",
        "friend_name": "李四",
        "platforms": ["微信", "QQ"],
        "is_cross_platform": true,
        "subject_count": 3,
        "subjects": [
          {
            "account": "wx_123",
            "name": "张三",
            "source": "微信主体"
          }
        ]
      }
    ]
  }
}
```

### 4.4 档案关联分析

**接口**: `POST /person/archive-relation`

**请求参数**:
```json
{
  "relation_type": "同住宿",
  "min_persons": 2
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "relations": [
      {
        "event_key": "酒店_2024-01-01_房间101",
        "relation_type": "同住宿",
        "persons": [
          {
            "name": "张三",
            "id_card": "110101199001011234"
          }
        ],
        "event_info": {
          "hotel": "XX酒店",
          "check_in": "2024-01-01",
          "room": "101"
        }
      }
    ]
  }
}
```

### 4.5 人员关系图谱

**接口**: `GET /person/relation-graph/{person_id}`

**请求参数**:
- `depth`: 关系深度（默认2）
- `relation_types`: 关系类型列表（可选）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {
        "id": "person_1",
        "name": "张三",
        "type": "person",
        "properties": {
          "id_card": "110101199001011234",
          "phone": "13800138000"
        }
      }
    ],
    "edges": [
      {
        "source": "person_1",
        "target": "person_2",
        "relation": "微信好友",
        "properties": {
          "remark": "老同学"
        }
      }
    ]
  }
}
```

## 5. 设备分析模块

### 5.1 导入设备档案

**接口**: `POST /device/import`

**请求类型**: `multipart/form-data`

**请求参数**:
- `file`: Excel文件
- `device_type`: 设备类型（路由设备/出口路由等）

**响应**:
```json
{
  "code": 200,
  "message": "导入成功",
  "data": {
    "total": 50,
    "success": 48,
    "failed": 2
  }
}
```

### 5.2 查询设备信息

**接口**: `GET /device/info`

**请求参数**:
- `device_id`: 设备ID（可选）
- `query_id`: 查询ID（可选）
- `start_date`: 开始时间（可选）
- `end_date`: 结束时间（可选）

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "query_id": "Q123456",
        "device": "设备001",
        "start_time": "2024-01-01 00:00:00",
        "end_time": "2024-01-31 23:59:59"
      }
    ]
  }
}
```

## 6. 报告生成模块

### 6.1 生成综合报告

**接口**: `POST /report/generate`

**请求参数**:
```json
{
  "report_type": "综合分析报告",
  "person_ids": [1, 2, 3],
  "card_nos": ["6222021234567890"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-03-01"
  },
  "modules": ["银行流水", "人员关系", "设备档案"]
}
```

**响应**:
```json
{
  "code": 200,
  "message": "报告生成中",
  "data": {
    "task_id": "report_task_123",
    "status": "processing"
  }
}
```

### 6.2 查询报告状态

**接口**: `GET /report/status/{task_id}`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "report_task_123",
    "status": "completed",
    "download_url": "/downloads/report_20240301.pdf"
  }
}
```

### 6.3 下载报告

**接口**: `GET /report/download/{filename}`

**响应**: 文件流

## 7. 系统管理模块

### 7.1 获取系统统计

**接口**: `GET /system/stats`

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "bank_records": 1000000,
    "person_records": 50000,
    "device_records": 5000,
    "storage_used": "10.5GB",
    "last_import": "2024-03-01 10:00:00"
  }
}
```

### 7.2 获取处理日志

**接口**: `GET /system/logs`

**请求参数**:
- `level`: 日志级别（INFO/WARNING/ERROR）
- `start_date`: 开始日期
- `end_date`: 结束日期
- `page`: 页码
- `page_size`: 每页数量

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "level": "INFO",
        "message": "银行流水导入成功",
        "timestamp": "2024-03-01 10:00:00"
      }
    ],
    "total": 100
  }
}
```

## 8. WebSocket接口

### 8.1 实时任务进度推送

**连接**: `ws://localhost:8000/ws/task/{task_id}`

**消息格式**:
```json
{
  "type": "progress",
  "data": {
    "task_id": "task_123",
    "progress": 50,
    "message": "正在处理第5000条记录"
  }
}
```

## 9. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1002 | 文件格式不支持 |
| 1003 | 文件大小超限 |
| 2001 | 数据库操作失败 |
| 2002 | 数据不存在 |
| 3001 | 认证失败 |
| 3002 | Token过期 |
| 3003 | 权限不足 |
| 5001 | 服务器内部错误 |

## 10. 接口调用示例

### Python示例
```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "password123"}
)
token = response.json()["data"]["access_token"]

# 查询交易明细
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/bank/transactions",
    headers=headers,
    params={"card_no": "6222021234567890", "page": 1}
)
print(response.json())
```

### JavaScript示例
```javascript
// 登录
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password123' })
});
const { data } = await loginResponse.json();
const token = data.access_token;

// 查询交易明细
const response = await fetch('http://localhost:8000/api/v1/bank/transactions?card_no=6222021234567890', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const result = await response.json();
console.log(result);
```
