#!/usr/bin/env python3
"""
修复案件数据库缺失表的工具脚本

功能：
1. 扫描所有案件数据库
2. 检测缺失的关键表
3. 重新执行表创建SQL
4. 验证修复结果

使用方法：
    python scripts/fix_missing_case_tables.py
    python scripts/fix_missing_case_tables.py --database c1_AXJCC  # 修复指定数据库
    python scripts/fix_missing_case_tables.py --dry-run  # 仅检查不修复
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config import config
from urllib.parse import quote_plus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_all_case_databases():
    """获取所有案件数据库列表"""
    logger.info("正在获取所有案件数据库...")

    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    db_url = f'mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/datapivot?charset=utf8mb4'

    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT id, case_name, case_code, database_name FROM cases WHERE is_active = 1'))
            cases = result.fetchall()

            databases = []
            for case in cases:
                databases.append({
                    'id': case[0],
                    'case_name': case[1],
                    'case_code': case[2],
                    'database_name': case[3]
                })

            logger.info(f"找到 {len(databases)} 个活跃案件数据库")
            return databases
    finally:
        engine.dispose()


def check_database_tables(database_name):
    """检查数据库中的表"""
    logger.info(f"检查数据库: {database_name}")

    # 定义必需的关键表
    required_tables = [
        'bank_all_statements',
        'bank_all_statements_tmp',
        'bank_all_statements_lastest',
        'bank_all_statements_turn',
        'bank_all_statements_with_info'
    ]

    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    db_url = f'mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{database_name}?charset=utf8mb4'

    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            existing_tables = [row[0] for row in result.fetchall()]

            missing_tables = [table for table in required_tables if table not in existing_tables]

            return {
                'total_tables': len(existing_tables),
                'existing_tables': existing_tables,
                'missing_tables': missing_tables,
                'needs_fix': len(missing_tables) > 0
            }
    except Exception as e:
        logger.error(f"检查数据库 {database_name} 时出错: {str(e)}")
        return None
    finally:
        engine.dispose()


def fix_database(database_name, case_code):
    """修复数据库缺失的表"""
    logger.info(f"开始修复数据库: {database_name}")

    # 读取模板文件
    template_path = project_root / 'sql' / 'schema' / 'case_template.sql'

    if not template_path.exists():
        logger.error(f"模板文件不存在: {template_path}")
        return False

    logger.info(f"读取模板文件: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 替换案件编号占位符
    sql_content = sql_content.replace('{{CASE_CODE}}', case_code)

    # 创建数据库连接
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    db_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{database_name}?charset=utf8mb4"

    engine = create_engine(db_url)

    executed_count = 0
    failed_count = 0

    try:
        with engine.connect() as conn:
            statements = sql_content.split(';')

            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                        executed_count += 1
                    except Exception as e:
                        # 忽略表已存在的错误
                        if 'already exists' in str(e).lower() or 'table' in str(e).lower():
                            continue

                        if 'SET' not in statement.upper():
                            failed_count += 1
                            logger.warning(f"执行失败: {str(e)[:100]}")

            logger.info(f"修复完成: 执行 {executed_count} 条语句, 失败 {failed_count} 条")
            return True

    except Exception as e:
        logger.error(f"修复数据库时出错: {str(e)}")
        return False
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description='修复案件数据库缺失的表')
    parser.add_argument('--database', help='指定要修复的数据库名称')
    parser.add_argument('--dry-run', action='store_true', help='仅检查不修复')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("案件数据库表修复工具")
    logger.info("=" * 80)

    # 获取所有案件数据库
    databases = get_all_case_databases()

    if not databases:
        logger.warning("没有找到任何案件数据库")
        return

    # 如果指定了数据库，只处理该数据库
    if args.database:
        databases = [db for db in databases if db['database_name'] == args.database]
        if not databases:
            logger.error(f"未找到数据库: {args.database}")
            return

    # 检查所有数据库
    problems = []

    for db_info in databases:
        database_name = db_info['database_name']
        case_code = db_info['case_code']

        logger.info(f"\n{'=' * 80}")
        logger.info(f"案件: {db_info['case_name']} ({case_code})")
        logger.info(f"数据库: {database_name}")
        logger.info(f"{'=' * 80}")

        check_result = check_database_tables(database_name)

        if check_result is None:
            continue

        logger.info(f"总表数: {check_result['total_tables']}")

        if check_result['missing_tables']:
            logger.warning(f"❌ 缺失 {len(check_result['missing_tables'])} 个关键表:")
            for table in check_result['missing_tables']:
                logger.warning(f"  - {table}")

            problems.append({
                'database_name': database_name,
                'case_code': case_code,
                'missing_tables': check_result['missing_tables']
            })
        else:
            logger.info("✅ 所有关键表都存在")

    # 如果是dry-run模式，只显示问题不修复
    if args.dry_run:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"检查完成，发现 {len(problems)} 个数据库需要修复")
        logger.info("使用 --dry-run 模式，未执行修复操作")
        return

    # 修复有问题的数据库
    if problems:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"开始修复 {len(problems)} 个数据库")
        logger.info(f"{'=' * 80}")

        for problem in problems:
            database_name = problem['database_name']
            case_code = problem['case_code']

            logger.info(f"\n修复数据库: {database_name}")
            success = fix_database(database_name, case_code)

            if success:
                # 验证修复结果
                check_result = check_database_tables(database_name)
                if check_result and not check_result['missing_tables']:
                    logger.info(f"✅ {database_name} 修复成功")
                else:
                    logger.warning(f"⚠️ {database_name} 修复后仍有缺失表")
            else:
                logger.error(f"❌ {database_name} 修复失败")

        logger.info(f"\n{'=' * 80}")
        logger.info("修复完成")
        logger.info(f"{'=' * 80}")
    else:
        logger.info(f"\n{'=' * 80}")
        logger.info("所有数据库都正常，无需修复")
        logger.info(f"{'=' * 80}")


if __name__ == '__main__':
    main()
