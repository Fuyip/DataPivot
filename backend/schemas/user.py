from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserCreate(UserBase):
    """创建用户Schema"""
    password: str = Field(..., min_length=6, description="密码")
    role: Optional[str] = Field("user", pattern="^(super_admin|admin|user)$", description="角色: super_admin/admin/user")


class UserUpdate(BaseModel):
    """更新用户Schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(super_admin|admin|user)$", description="角色: super_admin/admin/user")
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户Schema"""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """返回给前端的用户Schema"""
    pass
