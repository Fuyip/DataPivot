from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


# 用户案件权限关联表（多对多）
user_case_permission_association = Table(
    'user_case_permission_details',
    Base.metadata,
    Column('user_case_permission_id', Integer, ForeignKey('user_case_permissions.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    comment="用户案件权限详细关联表"
)


class Case(Base):
    """案件模型 - 存储在datapivot数据库"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, comment="案件ID")
    case_name = Column(String(200), unique=True, nullable=False, comment="案件名称")
    case_code = Column(String(100), unique=True, nullable=False, comment="案件编号")
    database_name = Column(String(100), unique=True, nullable=False, comment="案件数据库名称")
    description = Column(Text, comment="案件描述")
    status = Column(String(20), default="active", comment="状态: active/archived/closed")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_deleted = Column(Boolean, default=False, comment="是否已删除（软删除）")
    deleted_at = Column(DateTime(timezone=True), comment="删除时间")
    deleted_by = Column(Integer, ForeignKey("users.id"), comment="删除人ID")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    permissions = relationship("UserCasePermission", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case(id={self.id}, case_name='{self.case_name}', database_name='{self.database_name}')>"


class UserCasePermission(Base):
    """用户案件权限关联表 - 存储在datapivot数据库"""
    __tablename__ = "user_case_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, comment="案件ID")
    permission_level = Column(String(20), default="read", comment="权限级别: read/write/admin")
    granted_by = Column(Integer, ForeignKey("users.id"), comment="授权人ID")
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), comment="授权时间")

    # 关联关系
    case = relationship("Case", back_populates="permissions")
    # TODO: 细粒度权限控制，暂时不使用
    # permissions = relationship("backend.models.permission.Permission", secondary=user_case_permission_association, lazy="joined")

    def __repr__(self):
        return f"<UserCasePermission(user_id={self.user_id}, case_id={self.case_id}, permission_level='{self.permission_level}')>"
