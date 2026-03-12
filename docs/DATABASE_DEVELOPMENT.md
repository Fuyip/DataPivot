# DataPivot 数据库开发规范文档

## 1. 数据库连接配置

### 1.1 数据库架构

DataPivot 采用多数据库架构：

- **`datapivot` 数据库**：存储系统核心配置
  - 用户认证（users 表）
  - 案件管理
  - 系统配置

- **案件专用数据库**：每个案件独立数据库
  - 数据库名称：案件代码（如 `case_20240301`）
  - 表结构参考：`fx_test` 数据库中的表结构
  - 包含案件相关的所有分析数据

### 1.2 配置文件结构

项目使用 `pydantic-settings` 管理配置，配置文件位于项目根目录的 `.env` 文件。

**配置项说明：**

```python
# 数据库配置（系统核心数据库）
MYSQL_HOST=localhost        # MySQL 服务器地址
MYSQL_PORT=3306            # MySQL 端口
MYSQL_USER=root            # 数据库用户名
MYSQL_PASSWORD=password    # 数据库密码
MYSQL_DB=datapivot        # 系统核心数据库名称
```

**案件数据库连接：**

对于案件专用数据库，需要动态切换数据库连接：

```python
from sqlalchemy import create_engine
from config import config, encoded_password

# 创建案件专用数据库连接
case_code = "case_20240301"
case_db_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{case_code}?charset=utf8mb4"
case_engine = create_engine(case_db_url, pool_pre_ping=True)
```

### 1.3 数据库连接实现

项目使用 SQLAlchemy ORM 框架进行数据库操作，核心文件为 `database.py`。

**连接字符串格式：**
```
mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

**关键组件：**

1. **Engine（引擎）**：数据库连接池管理
   ```python
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       pool_pre_ping=True  # 连接前检查，防止连接失效
   )
   ```

2. **SessionLocal（会话工厂）**：创建数据库会话
   ```python
   SessionLocal = sessionmaker(
       autocommit=False,   # 不自动提交
       autoflush=False,    # 不自动刷新
       bind=engine
   )
   ```

3. **Base（基类）**：所有模型的基类
   ```python
   Base = declarative_base()
   ```

4. **get_db（依赖注入）**：FastAPI 路由中使用的数据库会话获取函数
   ```python
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

## 2. 数据库开发规范

### 2.1 模型定义规范

所有数据库模型必须继承 `Base` 类：

```python
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Decimal

class BankStatement(Base):
    __tablename__ = "bank_statements"

    id = Column(Integer, primary_key=True, index=True)
    case_no = Column(String(50), nullable=False, comment="案件编号")
    card_no = Column(String(50), nullable=False, index=True, comment="银行卡号")
    card_name = Column(String(100), comment="持卡人姓名")
    trade_money = Column(Decimal(15, 2), comment="交易金额")
    trade_date = Column(DateTime, comment="交易时间")
```

**命名规范：**
- 表名：使用小写字母和下划线，如 `bank_statements`
- 字段名：使用小写字母和下划线，如 `card_no`
- 类名：使用大驼峰命名，如 `BankStatement`

### 2.2 数据库会话使用规范

**在 FastAPI 路由中使用：**

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

@app.get("/statements/")
def get_statements(db: Session = Depends(get_db)):
    statements = db.query(BankStatement).all()
    return statements
```

**在独立脚本中使用：**

```python
from database import SessionLocal

def process_data():
    db = SessionLocal()
    try:
        # 执行数据库操作
        result = db.query(BankStatement).all()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
```

### 2.3 事务处理规范

**基本原则：**
- 所有写操作必须在事务中执行
- 发生异常时必须回滚
- 操作完成后必须关闭会话

```python
db = SessionLocal()
try:
    # 插入数据
    new_record = BankStatement(
        case_no="6151",
        card_no="6222021234567890"
    )
    db.add(new_record)

    # 更新数据
    record = db.query(BankStatement).filter_by(id=1).first()
    record.card_name = "张三"

    # 提交事务
    db.commit()
except Exception as e:
    # 回滚事务
    db.rollback()
    print(f"错误: {e}")
finally:
    # 关闭会话
    db.close()
```

### 2.4 查询优化规范

**使用索引：**
```python
# 在模型中定义索引
card_no = Column(String(50), index=True)

# 或使用 Index
from sqlalchemy import Index
Index('idx_card_trade_date', 'card_no', 'trade_date')
```

**避免 N+1 查询：**
```python
from sqlalchemy.orm import joinedload

# 使用 joinedload 预加载关联数据
statements = db.query(BankStatement)\
    .options(joinedload(BankStatement.account_info))\
    .all()
```

**分页查询：**
```python
page = 1
page_size = 100
offset = (page - 1) * page_size

statements = db.query(BankStatement)\
    .offset(offset)\
    .limit(page_size)\
    .all()
```

## 3. 数据库表结构说明

### 3.1 系统核心表（datapivot 数据库）

#### users（用户表）
存储系统用户认证信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键 |
| username | VARCHAR(50) | 用户名 |
| hashed_password | VARCHAR(255) | 加密密码 |
| full_name | VARCHAR(100) | 真实姓名 |
| email | VARCHAR(100) | 邮箱 |
| role | VARCHAR(20) | 角色（admin/user） |
| is_active | TINYINT | 是否激活 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 3.2 案件分析表（案件专用数据库，如 case_20240301）

**注意**：以下表结构参考 `fx_test` 数据库，每个案件数据库都包含这些表。

#### bank_statements（银行流水汇总表）
存储银行卡交易汇总信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键 |
| case_no | VARCHAR(50) | 案件编号 |
| card_no | VARCHAR(50) | 银行卡号 |
| card_name | VARCHAR(100) | 持卡人姓名 |
| dict_trade_tag | VARCHAR(20) | 交易标签（in/out） |
| rival_card_no | VARCHAR(50) | 对手卡号 |
| rival_card_name | VARCHAR(255) | 对手卡户名 |
| merchant_name | VARCHAR(200) | 商户名称 |
| trade_money | DECIMAL(15,2) | 交易金额 |
| trade_count | INT | 交易笔数 |
| min_trade_date | DATETIME | 最早交易时间 |
| max_trade_date | DATETIME | 最晚交易时间 |

#### bank_statements_turn（银行流水正反向表）
在 bank_statements 基础上增加正反向标识。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| situation | VARCHAR(10) | 正/反向标识 |
| 其他字段 | - | 同 bank_statements |

#### bank_all_statements（银行流水明细表）
存储所有银行卡交易明细。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键 |
| card_no | VARCHAR(50) | 银行卡号 |
| trade_date | DATETIME | 交易时间 |
| trade_money | DECIMAL(15,2) | 交易金额 |
| trade_balance | DECIMAL(15,2) | 账户余额 |
| rival_card_no | VARCHAR(50) | 对手卡号 |
| rival_card_name | VARCHAR(255) | 对手卡户名 |
| dict_trade_tag | VARCHAR(20) | 交易方向 |

#### bank_all_statements_lastest（最新流水表）
存储每张卡的最新一笔交易记录。

#### case_card（案件银行卡表）
存储案件涉及的银行卡信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键 |
| card_no | VARCHAR(50) | 银行卡号 |
| bank_name | VARCHAR(100) | 银行名称 |
| card_type | VARCHAR(20) | 卡类型 |
| is_in_bg | TINYINT | 是否从后台获取 |
| is_main | TINYINT | 是否核心收款卡 |
| source | VARCHAR(100) | 来源 |
| user_id | VARCHAR(50) | 用户ID |

#### bank_account_info（银行账户信息表）
存储银行账户详细信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| transactionCardNum | VARCHAR(50) | 交易卡号 |
| tradingAccountNum | VARCHAR(50) | 交易账号 |
| accountOpeningName | VARCHAR(100) | 开户名 |
| idNum | VARCHAR(50) | 身份证号 |
| accountBalance | DECIMAL(15,2) | 账户余额 |
| accountStatus | VARCHAR(50) | 账户状态 |
| source | VARCHAR(100) | 来源 |

### 3.3 辅助信息表（案件专用数据库）

- **bank_people_info**：银行账户人员信息
- **bank_coercive_action_info**：银行强制措施信息
- **freeze_card**：冻结卡信息
- **freeze_back**：冻结反馈信息
- **apply_card_inner**：申调卡信息
- **gz_tz_info**：公证通知信息
- **bank_card_exg**：银行卡交易所信息

### 3.4 视图（案件专用数据库）

- **银行卡涉案情况**：银行卡涉案统计视图
- **3003xpj银行卡整体情况**：特定案件银行卡综合情况视图

## 4. 常见问题

### 4.1 连接池配置

如遇到 "MySQL server has gone away" 错误，已通过 `pool_pre_ping=True` 解决。

如需调整连接池大小：
```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 超出连接池大小的最大连接数
    pool_recycle=3600    # 连接回收时间（秒）
)
```

### 4.2 字符编码

连接字符串已指定 `charset=utf8mb4`，支持完整的 Unicode 字符集（包括 emoji）。

### 4.3 密码特殊字符处理

`config.py` 中使用 `quote_plus` 对密码进行 URL 编码，支持特殊字符。

## 5. 数据库迁移

项目使用 Alembic 进行数据库迁移管理。

**初始化迁移：**
```bash
alembic init alembic
```

**创建迁移脚本：**
```bash
alembic revision --autogenerate -m "描述信息"
```

**执行迁移：**
```bash
alembic upgrade head
```

**回滚迁移：**
```bash
alembic downgrade -1
```

## 6. 最佳实践

1. **始终使用参数化查询**，防止 SQL 注入
2. **合理使用索引**，提升查询性能
3. **避免在循环中执行数据库查询**
4. **使用批量操作**代替逐条插入
5. **定期备份数据库**
6. **监控慢查询**，及时优化
7. **使用连接池**，避免频繁创建连接
8. **正确处理事务**，确保数据一致性

## 7. 安全建议

1. **不要在代码中硬编码数据库密码**
2. **使用环境变量管理敏感信息**
3. **限制数据库用户权限**
4. **定期更新数据库密码**
5. **启用 SSL 连接**（生产环境）
6. **记录数据库操作日志**
7. **定期审计数据库访问**

## 8. 相关文件

- `database.py` - 数据库连接配置
- `config.py` - 配置管理
- `.env` - 环境变量配置
- `requirements.txt` - Python 依赖包
- `generate_db_schema.py` - 数据库结构生成脚本
