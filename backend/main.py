"""
DataPivot FastAPI 应用入口
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 将项目根目录和tools目录添加到 Python 路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "tools"))

from backend.core.config import config
from backend.api.v1 import auth, users, cases, case_permissions, permissions, bank_statements, case_cards, import_rules

# 创建 FastAPI 应用实例
app = FastAPI(
    title="DataPivot API",
    description="数据情报分析系统 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS 中间件
origins = config.CORS_ORIGINS.split(",") if hasattr(config, "CORS_ORIGINS") else [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查接口
@app.get("/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "DataPivot API is running"
    }


# 根路径
@app.get("/", tags=["系统"])
def root():
    """根路径"""
    return {
        "message": "Welcome to DataPivot API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# 注册 API 路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(case_permissions.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")
app.include_router(bank_statements.router, prefix="/api/v1")
app.include_router(case_cards.router, prefix="/api/v1/cases", tags=["案件银行卡"])
app.include_router(import_rules.router, prefix="/api/v1/import-rules")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
