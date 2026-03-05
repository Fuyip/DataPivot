# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URL, get_datapivot_database_url

# 1. 创建业务数据库引擎（原有数据库）
# pool_pre_ping=True 可以在每次连接前检查连接是否存活，防止 MySQL server has gone away 错误
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# 2. 创建业务数据库 SessionLocal 类
# 这是一个工厂类，每次调用都会产生一个新的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建系统数据库引擎（datapivot 数据库，用于认证等系统功能）
system_engine = create_engine(
    get_datapivot_database_url(),
    pool_pre_ping=True
)

# 4. 创建系统数据库 SessionLocal 类
SystemSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=system_engine)

# 5. 创建 Base 类
# 以后所有的模型（Model）都要继承这个类
Base = declarative_base()

# 6. 业务数据库依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db  # 请求开始时，提供一个 db session
    finally:
        db.close() # 请求结束时，自动关闭 session，归还连接池

# 7. 系统数据库依赖注入函数（用于认证等系统功能）
def get_system_db():
    db = SystemSessionLocal()
    try:
        yield db
    finally:
        db.close()