#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新已存在的案件数据库中的case_no字段数据
将所有值为 '{{CASE_CODE}}' 的记录更新为实际的案件编号
"""
import pymysql
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from database import get_system_db
from backend.models.case import Case


def update_case_data(case_code: str, database_name: str):
    """
    更新单个案件数据库中的case_no字段数据

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

        total_updated = 0

        for table in tables:
            table_name = table[0]

            # 检查是否有case_no字段
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'case_no'")
            case_no_col = cursor.fetchone()

            if case_no_col:
                try:
                    # 更新所有值为 {{CASE_CODE}} 的记录
                    update_sql = f"UPDATE `{table_name}` SET `case_no` = %s WHERE `case_no` = '{{{{CASE_CODE}}}}'"
                    cursor.execute(update_sql, (case_code,))

                    rows_affected = cursor.rowcount
                    if rows_affected > 0:
                        connection.commit()
                        print(f"  ✓ {table_name}: 更新了 {rows_affected} 条记录")
                        total_updated += rows_affected

                except Exception as e:
                    print(f"  ✗ {table_name}: 更新失败 - {str(e)}")

        cursor.close()

        print(f"\n结果: 共更新 {total_updated} 条记录")

    finally:
        connection.close()


def main():
    """主函数：更新所有案件数据库"""
    print("=" * 60)
    print("更新已存在的案件数据库中的case_no字段数据")
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
                update_case_data(case.case_code, case.database_name)
            except Exception as e:
                print(f"\n✗ 处理案件 {case.case_name} ({case.case_code}) 失败: {str(e)}")

        print("\n" + "=" * 60)
        print("✓ 所有案件数据库处理完成")
        print("=" * 60)

    finally:
        db.close()


if __name__ == '__main__':
    main()
