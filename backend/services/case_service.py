"""
案件管理服务层
提供案件数据库动态创建、权限检查等核心功能
"""
import time
import random
import string
import re
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from fastapi import Depends, HTTPException

from config import config
from urllib.parse import quote_plus
from backend.models.case import Case, UserCasePermission
from backend.services.auth_service import get_current_active_user
from database import get_system_db


def generate_case_code(db: Session) -> str:
    """
    生成唯一的案件编号（5位字母数字组合）

    Args:
        db: 数据库会话

    Returns:
        str: 案件编号
    """
    max_attempts = 100
    for _ in range(max_attempts):
        # 生成5位随机字母数字组合
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # 检查是否已存在
        existing = db.query(Case).filter(Case.case_code == code).first()
        if not existing:
            return code

    # 如果100次都没生成唯一编号，抛出异常
    raise Exception("无法生成唯一的案件编号，请稍后重试")


def sanitize_database_name(name: str) -> str:
    """
    清理数据库名称，只保留字母、数字和下划线

    Args:
        name: 原始名称

    Returns:
        str: 清理后的名称
    """
    # 移除所有非字母数字字符，替换为下划线
    sanitized = re.sub(r'[^\w]', '_', name)
    # 移除连续的下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    # 移除首尾的下划线
    sanitized = sanitized.strip('_')
    return sanitized


def create_case_database(case_id: int, case_name: str, case_code: str) -> str:
    """
    为案件创建独立的数据库

    Args:
        case_id: 案件ID
        case_name: 案件名称
        case_code: 案件编号

    Returns:
        str: 数据库名称
    """
    # 清理案件名称，只保留字母数字和下划线
    sanitized_name = sanitize_database_name(case_name)

    # 生成数据库名称：案件名称_案件编号
    database_name = f"{sanitized_name}_{case_code}"

    # 如果名称过长，截断案件名称部分
    if len(database_name) > 64:  # MySQL数据库名称最大长度为64
        max_name_length = 64 - len(case_code) - 1  # 减去编号和下划线的长度
        sanitized_name = sanitized_name[:max_name_length]
        database_name = f"{sanitized_name}_{case_code}"

    # 创建数据库连接（连接到MySQL服务器，不指定数据库）
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    server_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/?charset=utf8mb4"

    engine = create_engine(server_url)

    try:
        with engine.connect() as conn:
            # 创建数据库
            conn.execute(text(f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
    finally:
        engine.dispose()

    return database_name


def drop_case_database(database_name: str):
    """
    删除案件数据库

    Args:
        database_name: 数据库名称
    """
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    server_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/?charset=utf8mb4"

    engine = create_engine(server_url)

    try:
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS `{database_name}`"))
            conn.commit()
    finally:
        engine.dispose()


def get_case_database_url(database_name: str) -> str:
    """
    获取案件数据库连接URL

    Args:
        database_name: 数据库名称

    Returns:
        str: 数据库连接URL
    """
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    return f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{database_name}?charset=utf8mb4"


def check_case_permission(db: Session, user_id: int, case_id: int, required_level: str = "read") -> bool:
    """
    检查用户是否有指定案件的权限

    Args:
        db: 数据库会话
        user_id: 用户ID
        case_id: 案件ID
        required_level: 需要的权限级别 (read/write/admin)

    Returns:
        bool: 是否有权限
    """
    # 权限级别映射
    permission_levels = {"read": 1, "write": 2, "admin": 3}
    required_level_value = permission_levels.get(required_level, 1)

    # 查询用户对该案件的权限
    permission = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id,
        UserCasePermission.case_id == case_id
    ).first()

    if not permission:
        return False

    # 检查权限级别是否满足要求
    user_level_value = permission_levels.get(permission.permission_level, 0)
    return user_level_value >= required_level_value


def get_user_cases(db: Session, user_id: int) -> List[Case]:
    """
    获取用户有权限的所有案件

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        List[Case]: 案件列表
    """
    # 查询用户的所有案件权限
    permissions = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id
    ).all()

    case_ids = [p.case_id for p in permissions]

    # 查询案件信息
    cases = db.query(Case).filter(
        Case.id.in_(case_ids),
        Case.is_active == True
    ).all()

    return cases


def get_case_permission_level(db: Session, user_id: int, case_id: int) -> Optional[str]:
    """
    获取用户对指定案件的权限级别

    Args:
        db: 数据库会话
        user_id: 用户ID
        case_id: 案件ID

    Returns:
        Optional[str]: 权限级别 (read/write/admin) 或 None
    """
    permission = db.query(UserCasePermission).filter(
        UserCasePermission.user_id == user_id,
        UserCasePermission.case_id == case_id
    ).first()

    return permission.permission_level if permission else None


def require_case_permission(required_level: str = "read"):
    """
    案件权限检查依赖注入

    Args:
        required_level: 需要的权限级别

    Returns:
        依赖函数
    """
    def check_permission(
        case_id: int,
        current_user = Depends(get_current_active_user),
        db: Session = Depends(get_system_db)
    ):
        # super_admin 拥有所有权限
        if current_user.role == "super_admin":
            return current_user

        # admin 和 user 都需要检查具体的案件权限
        has_permission = check_case_permission(db, current_user.id, case_id, required_level)
        if not has_permission:
            raise HTTPException(status_code=403, detail="权限不足，无法访问该案件")

        return current_user

    return check_permission
