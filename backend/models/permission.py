from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class Permission(Base):
    """权限定义模型 - 存储在data_pivot数据库"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    code = Column(String(50), unique=True, nullable=False, comment="权限代码")
    name = Column(String(100), nullable=False, comment="权限名称")
    description = Column(Text, comment="权限描述")
    category = Column(String(50), comment="权限分类: user/case/data/system")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', name='{self.name}')>"


# 预定义权限列表
PREDEFINED_PERMISSIONS = [
    # 用户管理权限
    {"code": "user.create", "name": "创建用户", "description": "创建新用户账号", "category": "user"},
    {"code": "user.read", "name": "查看用户", "description": "查看用户信息", "category": "user"},
    {"code": "user.update", "name": "更新用户", "description": "更新用户信息", "category": "user"},
    {"code": "user.delete", "name": "删除用户", "description": "删除用户账号", "category": "user"},
    {"code": "user.manage_role", "name": "管理用户角色", "description": "修改用户角色", "category": "user"},

    # 案件管理权限
    {"code": "case.create", "name": "创建案件", "description": "创建新案件", "category": "case"},
    {"code": "case.read", "name": "查看案件", "description": "查看案件信息", "category": "case"},
    {"code": "case.update", "name": "更新案件", "description": "更新案件信息", "category": "case"},
    {"code": "case.delete", "name": "删除案件", "description": "删除案件", "category": "case"},
    {"code": "case.archive", "name": "归档案件", "description": "归档案件", "category": "case"},
    {"code": "case.manage_permission", "name": "管理案件权限", "description": "管理案件内用户权限", "category": "case"},

    # 数据管理权限
    {"code": "data.import", "name": "导入数据", "description": "导入数据到案件", "category": "data"},
    {"code": "data.export", "name": "导出数据", "description": "从案件导出数据", "category": "data"},
    {"code": "data.read", "name": "查看数据", "description": "查看案件数据", "category": "data"},
    {"code": "data.update", "name": "更新数据", "description": "更新案件数据", "category": "data"},
    {"code": "data.delete", "name": "删除数据", "description": "删除案件数据", "category": "data"},
    {"code": "data.analyze", "name": "分析数据", "description": "执行数据分析", "category": "data"},

    # 系统管理权限
    {"code": "system.config", "name": "系统配置", "description": "修改系统配置", "category": "system"},
    {"code": "system.log", "name": "查看日志", "description": "查看系统日志", "category": "system"},
    {"code": "system.backup", "name": "备份管理", "description": "管理系统备份", "category": "system"},
]
