from urllib.parse import quote_plus

from anyio.functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG_MODE: bool
    HAIJING_API_KEY : str
    HAIJING_BASE_URL :str
    MYSQL_HOST : str
    MYSQL_PORT : str
    MYSQL_USER : str
    MYSQL_PASSWORD : str
    MYSQL_DB : str

    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ('.env','.env.prod')

@lru_cache()
def get_settings() -> Settings:
    return Settings()

config = get_settings()

encoded_password = quote_plus(config.MYSQL_PASSWORD)
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB}?charset=utf8mb4"

def get_datapivot_database_url() -> str:
    """获取 datapivot 系统数据库连接 URL（用于认证等系统功能）"""
    return f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/datapivot?charset=utf8mb4"
