#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复已存在的案件数据库中的case_no字段默认值
将 '{{CASE_CODE}}' 占位符替换为实际的案件编号
"""
import pymysql
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from database import get_system_db
from backend.models.case import Case


def fix_case_database(case_code: str, database_name: str):
    """
    修复单个案件数据库的case_no字段默认值

    Args:
        case_code: 案件编号
        database_name: 数据库名称
    """
    print(f"\n处理数据库: {database_name}")
    print(f"案件编号: {case_code}")

    # 连接到案件数据库
    connection = pymysql.connect(
        host=config.MYSQL_HOST,
        port=int(config.MYSQL_PORT),
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=database_name,
        charset='utf8mb4'
    )

    try:
        cursor = connection.cursor()

        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        fixed_count = 0
        skipped_count = 0

        for table in tables:
            table_name = table[0]

            # 检查是否有case_no字段
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'case_no'")
            case_no_col = cursor.fetchone()

            if case_no_col:
                default_value = case_no_col[4]  # Default列

                # 如果默认值是占位符，则修改
                if default_value == '{{CASE_CODE}}':
                    try:
                        # 修改字段默认值
                        alter_sql = f"ALTER TABLE `{table_name}` MODIFY COLUMN `case_no` varchar(255) DEFAULT '{case_code}' COMMENT '案件编号'"
                        cursor.execute(alter_sql)
                        connection.commit()
                        print(f"  ✓ {table_name}: 已修复")
                        fixed_count += 1
                    except Exception as e:
                        print(f"  ✗ {table_name}: 修复失败 - {str(e)}")
                elif default_value == case_code:
                    skipped_count += 1
                else:
                    print(f"  - {table_name}: 默认值为 '{default_value}'，跳过")
                    skipped_count += 1

        cursor.close()

        print(f"\n结果: 修复 {fixed_count} 个表, 跳过 {skipped_count} 个表")

    finally:
        connection.close()


def main():
    """主函数：修复所有案件数据库"""
    print("=" * 60)
    print("修复已存在的案件数据库中的case_no字段默认值")
    print("=" * 60)

    # 获取所有案件
    db = next(get_system_db())
    try:
        cases = db.query(Case).filter(Case.is_active == True).all()

        if not cases:
            print("\n没有找到活跃的案件")
            return

        print(f"\n找到 {len(cases)} 个活跃案件")

        for case in cases:
            try:
                fix_case_database(case.case_code, case.database_name)
            except Exception as e:
                print(f"\n✗ 处理案件 {case.case_name} ({case.case_code}) 失败: {str(e)}")

        print("\n" + "=" * 60)
        print("✓ 所有案件数据库处理完成")
        print("=" * 60)

    finally:
        db.close()


if __name__ == '__main__':
    main()
