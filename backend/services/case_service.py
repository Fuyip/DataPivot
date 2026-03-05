"""
案件管理服务层
提供案件数据库动态创建、权限检查等核心功能
"""
import time
import random
import string
import re
import os
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from fastapi import Depends, HTTPException

from config import config
from urllib.parse import quote_plus
from backend.models.case import Case, UserCasePermission
from backend.services.auth_service import get_current_active_user
from database import get_system_db

# 配置日志
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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


def initialize_case_database_schema(database_name: str, case_code: str):
    """
    初始化案件数据库表结构（从 fx_test 模板导入）

    Args:
        database_name: 数据库名称
        case_code: 案件编号

    Raises:
        Exception: 当模板文件不存在或SQL执行失败时
    """
    logger.info(f"开始初始化案件数据库: {database_name}, 案件编号: {case_code}")

    # 获取案件数据库模板文件路径
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                  'sql', 'schema', 'case_template.sql')

    if not os.path.exists(template_path):
        error_msg = f"案件数据库模板文件不存在: {template_path}"
        logger.error(error_msg)
        raise Exception(error_msg)

    logger.info(f"读取模板文件: {template_path}")

    # 读取模板 SQL 文件
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        logger.info(f"模板文件读取成功，大小: {len(sql_content)} 字节")
    except Exception as e:
        error_msg = f"读取模板文件失败: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

    # 替换案件编号占位符
    sql_content = sql_content.replace('{{CASE_CODE}}', case_code)
    logger.info(f"已替换案件编号占位符: {{{{CASE_CODE}}}} -> {case_code}")

    # 创建数据库连接
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    db_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{database_name}?charset=utf8mb4"

    engine = create_engine(db_url)

    executed_count = 0
    failed_count = 0
    failed_statements = []

    try:
        with engine.connect() as conn:
            # 分割 SQL 语句（按分号分割）
            statements = sql_content.split(';')
            total_statements = len([s for s in statements if s.strip() and not s.strip().startswith('--')])

            logger.info(f"开始执行 SQL 语句，共 {total_statements} 条")

            for idx, statement in enumerate(statements):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                        executed_count += 1

                        # 每执行10条语句记录一次进度
                        if executed_count % 10 == 0:
                            logger.info(f"进度: {executed_count}/{total_statements} 条语句已执行")

                    except Exception as e:
                        # 忽略某些无关紧要的错误（如 SET 语句）
                        if 'SET' not in statement.upper():
                            failed_count += 1
                            error_info = {
                                'index': idx,
                                'error': str(e)[:200],
                                'statement': statement[:200]
                            }
                            failed_statements.append(error_info)
                            logger.error(f"执行 SQL 语句失败 (第 {idx} 条): {str(e)[:100]}")
                            logger.error(f"失败的语句: {statement[:200]}")

                            # 如果是创建表的语句失败，这是严重错误
                            if 'CREATE TABLE' in statement.upper():
                                logger.error(f"创建表失败，这是严重错误！")
                                # 继续执行，但记录错误

            logger.info(f"SQL 执行完成: 成功 {executed_count} 条, 失败 {failed_count} 条")

            if failed_count > 0:
                logger.warning(f"有 {failed_count} 条语句执行失败，详情:")
                for fail in failed_statements[:5]:  # 只记录前5个失败
                    logger.warning(f"  - 第 {fail['index']} 条: {fail['error']}")

    except Exception as e:
        error_msg = f"初始化数据库时发生严重错误: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    finally:
        engine.dispose()

    logger.info(f"案件数据库 {database_name} 初始化完成")

    # 验证关键表是否创建成功
    try:
        verify_result = verify_case_database_tables(database_name)
        if verify_result['missing_tables']:
            logger.warning(f"警告: 以下关键表缺失: {', '.join(verify_result['missing_tables'])}")
        else:
            logger.info("所有关键表验证通过")
    except Exception as e:
        logger.warning(f"表验证失败: {str(e)}")


def verify_case_database_tables(database_name: str) -> dict:
    """
    验证案件数据库关键表是否存在

    Args:
        database_name: 数据库名称

    Returns:
        dict: 包含验证结果的字典
            {
                'total_tables': int,  # 总表数
                'required_tables': list,  # 必需的表列表
                'existing_tables': list,  # 已存在的表列表
                'missing_tables': list,  # 缺失的表列表
                'all_present': bool  # 是否所有必需表都存在
            }
    """
    logger.info(f"开始验证数据库 {database_name} 的表结构")

    # 定义必需的关键表
    required_tables = [
        'bank_all_statements',
        'bank_all_statements_tmp',
        'bank_all_statements_lastest',
        'bank_all_statements_turn',
        'bank_all_statements_with_info',
        'bank_account_info',
        'bank_people_info',
        'case_card'
    ]

    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    db_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{database_name}?charset=utf8mb4"

    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            # 获取所有表
            result = conn.execute(text("SHOW TABLES"))
            all_tables = [row[0] for row in result.fetchall()]

            # 检查必需表
            existing_tables = []
            missing_tables = []

            for table in required_tables:
                if table in all_tables:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)

            result = {
                'total_tables': len(all_tables),
                'required_tables': required_tables,
                'existing_tables': existing_tables,
                'missing_tables': missing_tables,
                'all_present': len(missing_tables) == 0
            }

            logger.info(f"验证完成: 总表数 {len(all_tables)}, 必需表 {len(required_tables)}, "
                       f"已存在 {len(existing_tables)}, 缺失 {len(missing_tables)}")

            if missing_tables:
                logger.warning(f"缺失的表: {', '.join(missing_tables)}")

            return result

    except Exception as e:
        logger.error(f"验证数据库表时出错: {str(e)}")
        raise
    finally:
        engine.dispose()


def create_case_database(case_id: int, case_name: str, case_code: str) -> str:
    """
    为案件创建独立的数据库（仅创建空数据库，不初始化表结构）

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

    except Exception as e:
        raise e
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
