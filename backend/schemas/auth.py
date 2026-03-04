from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """Token响应Schema"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


class TokenData(BaseModel):
    """Token数据Schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None
