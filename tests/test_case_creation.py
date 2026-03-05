#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试案件创建功能
验证创建案件时是否自动初始化数据库表结构
"""

import re
import pymysql
from config import config
from backend.services.case_service import create_case_database, drop_case_database


def test_case_database_creation():
    """测试案件数据库创建和表结构初始化"""
    print("=" * 60)
    print("测试案件数据库创建功能")
    print("=" * 60)
    print()

    # 测试数据
    test_case_id = 999
    test_case_name = "测试案件"
    test_case_code = "TEST01"

    try:
        # 0. 先删除可能存在的测试数据库
        sanitized_name = re.sub(r'[^\w]', '_', test_case_name)
        sanitized_name = re.sub(r'_+', '_', sanitized_name).strip('_')
        database_name = f"{sanitized_name}_{test_case_code}"

        print("[0/5] 清理旧的测试数据库...")
        try:
            drop_case_database(database_name)
            print(f"✓ 已删除旧数据库: {database_name}")
        except:
            print(f"  (没有旧数据库需要删除)")
        print()

        # 1. 创建案件数据库
        print("[1/5] 创建案件数据库...")
        database_name = create_case_database(test_case_id, test_case_name, test_case_code)
        print(f"✓ 数据库创建成功: {database_name}")
        print()

        # 2. 验证数据库是否存在
        print("[2/5] 验证数据库是否存在...")
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=int(config.MYSQL_PORT),
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=database_name,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        print(f"✓ 成功连接到数据库: {database_name}")
        print()

        # 3. 检查表结构
        print("[3/5] 检查表结构...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_count = len(tables)

        print(f"✓ 找到 {table_count} 个表")
        print()

        if table_count > 0:
            print("前10个表:")
            for i, table in enumerate(tables[:10], 1):
                print(f"  {i}. {table[0]}")
            if table_count > 10:
                print(f"  ... 还有 {table_count - 10} 个表")
        else:
            print("✗ 警告: 没有找到任何表！")

        print()

        # 4. 验证case_no字段默认值和AUTO_INCREMENT
        print("[4/5] 验证case_no字段默认值和AUTO_INCREMENT...")
        success_count = 0
        fail_count = 0

        for table in tables[:5]:  # 只检查前5个表
            table_name = table[0]

            # 检查case_no字段
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'case_no'")
            case_no_col = cursor.fetchone()

            if case_no_col:
                default_value = case_no_col[4]  # Default列
                if default_value == test_case_code:
                    print(f"  ✓ {table_name}: case_no默认值正确 ({default_value})")
                    success_count += 1
                else:
                    print(f"  ✗ {table_name}: case_no默认值错误 (期望: {test_case_code}, 实际: {default_value})")
                    fail_count += 1
            else:
                print(f"  - {table_name}: 没有case_no字段（正常）")

            # 检查AUTO_INCREMENT
            cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
            status = cursor.fetchone()
            if status and status[10] is not None:  # Auto_increment列
                auto_inc = status[10]
                if auto_inc == 1:
                    print(f"    └─ AUTO_INCREMENT: {auto_inc} ✓")
                else:
                    print(f"    └─ AUTO_INCREMENT: {auto_inc} (期望: 1)")

        print(f"\n  测试结果: 成功 {success_count}, 失败 {fail_count}")
        print()

        # 验证关键表是否存在
        print("[5/5] 验证关键表:")
        key_tables = [
            'bank_statements',
            'bank_all_statements',
            'case_card',
            'bank_account_info',
            '人员总体归纳'
        ]

        for table_name in key_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = cursor.fetchone()
            if result:
                print(f"  ✓ {table_name}")
            else:
                print(f"  ✗ {table_name} (缺失)")

        cursor.close()
        connection.close()

        print()
        print("=" * 60)
        print("✓ 测试完成！")
        print("=" * 60)
        print()

        # 自动删除测试数据库
        print(f"\n删除测试数据库: {database_name}")
        drop_case_database(database_name)
        print("✓ 测试数据库已删除")

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_case_database_creation()
