from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class CaseBase(BaseModel):
    """案件基础Schema"""
    case_name: str = Field(..., min_length=1, max_length=200, description="案件名称")
    case_code: str = Field(..., min_length=1, max_length=100, description="案件编号")
    description: Optional[str] = Field(None, description="案件描述")


class CaseCreate(BaseModel):
    """创建案件Schema"""
    case_name: str = Field(..., min_length=1, max_length=200, description="案件名称")
    case_code: Optional[str] = Field(None, description="案件编号（可选，不填则自动生成）")
    description: Optional[str] = Field(None, description="案件描述")

    @model_validator(mode='before')
    @classmethod
    def validate_fields(cls, values):
        # 处理 case_code
        if isinstance(values, dict):
            case_code = values.get('case_code')
            if case_code == '':
                values['case_code'] = None
            elif case_code is not None and len(case_code) != 5:
                raise ValueError('案件编号必须为5个字符')
        return values


class CaseUpdate(BaseModel):
    """更新案件Schema"""
    case_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|closed)$")
    is_active: Optional[bool] = None


class CaseInDB(CaseBase):
    """数据库中的案件Schema"""
    id: int
    database_name: str
    status: str
    is_active: bool
    is_deleted: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class Case(CaseInDB):
    """返回给前端的案件Schema"""
    pass


class UserCasePermissionBase(BaseModel):
    """用户案件权限基础Schema"""
    user_id: int = Field(..., description="用户ID")
    case_id: int = Field(..., description="案件ID")
    permission_level: str = Field(default="read", pattern="^(admin|write|read)$", description="权限级别")


class UserCasePermissionCreate(BaseModel):
    """创建用户案件权限Schema"""
    user_id: int = Field(..., description="用户ID")
    permission_level: str = Field(default="read", pattern="^(admin|write|read)$", description="权限级别")


class UserCasePermissionUpdate(BaseModel):
    """更新用户案件权限Schema"""
    permission_level: str = Field(..., pattern="^(admin|write|read)$", description="权限级别")


class UserCasePermissionInDB(UserCasePermissionBase):
    """数据库中的用户案件权限Schema"""
    id: int
    granted_by: Optional[int] = None
    granted_at: datetime

    class Config:
        from_attributes = True


class UserCasePermission(UserCasePermissionInDB):
    """返回给前端的用户案件权限Schema"""
    pass


class CaseWithPermissions(Case):
    """带权限信息的案件Schema"""
    user_permission: Optional[str] = None  # 当前用户对该案件的权限级别
