from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """权限基础Schema"""
    code: str = Field(..., max_length=50, description="权限代码")
    name: str = Field(..., max_length=100, description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")
    category: Optional[str] = Field(None, max_length=50, description="权限分类")


class PermissionCreate(PermissionBase):
    """创建权限Schema"""
    pass


class Permission(PermissionBase):
    """权限Schema"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCasePermissionBase(BaseModel):
    """用户案件权限基础Schema"""
    user_id: int = Field(..., description="用户ID")
    case_id: int = Field(..., description="案件ID")
    role: str = Field("user", pattern="^(admin|user)$", description="案件内角色: admin/user")


class UserCasePermissionCreate(UserCasePermissionBase):
    """创建用户案件权限Schema"""
    permission_codes: List[str] = Field(default=[], description="权限代码列表")


class UserCasePermissionUpdate(BaseModel):
    """更新用户案件权限Schema"""
    role: Optional[str] = Field(None, pattern="^(admin|user)$", description="案件内角色")
    permission_codes: Optional[List[str]] = Field(None, description="权限代码列表")


class UserCasePermission(UserCasePermissionBase):
    """用户案件权限Schema"""
    id: int
    granted_by: Optional[int] = None
    granted_at: datetime
    permissions: List[Permission] = []

    class Config:
        from_attributes = True
