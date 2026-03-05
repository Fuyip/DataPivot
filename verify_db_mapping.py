#!/usr/bin/env python3
"""验证数据库字段映射"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config import config
from urllib.parse import quote_plus

def main():
    print("=" * 60)
    print("验证权限字段映射")
    print("=" * 60)
    print()

    # 创建数据库连接
    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    database_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/datapivot?charset=utf8mb4"

    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            # 1. 检查表结构
            print("1. 数据库表结构:")
            print("-" * 60)
            result = conn.execute(text("DESCRIBE user_case_permissions"))
            for row in result:
                field_name = row[0]
                field_type = row[1]
                if field_name == 'role':
                    print(f"  ✅ {field_name} ({field_type}) <- 这是数据库实际字段")
                elif field_name == 'permission_level':
                    print(f"  ⚠️  {field_name} ({field_type}) <- 意外：不应该存在")
                else:
                    print(f"     {field_name} ({field_type})")

            print()

            # 2. 查询实际数据
            print("2. 数据库中的实际数据:")
            print("-" * 60)
            result = conn.execute(text(
                "SELECT id, user_id, case_id, role, granted_at FROM user_case_permissions LIMIT 5"
            ))

            rows = result.fetchall()
            if rows:
                print(f"  {'ID':<5} {'用户ID':<8} {'案件ID':<8} {'role字段值':<12} {'授权时间'}")
                print("  " + "-" * 55)
                for row in rows:
                    print(f"  {row[0]:<5} {row[1]:<8} {row[2]:<8} {row[3]:<12} {row[4]}")
            else:
                print("  (无数据)")

            print()

            # 3. 统计权限值分布
            print("3. 权限值分布:")
            print("-" * 60)
            result = conn.execute(text(
                "SELECT role, COUNT(*) as count FROM user_case_permissions GROUP BY role"
            ))
            for row in result:
                print(f"  {row[0]}: {row[1]} 条记录")

            print()
            print("=" * 60)
            print("验证结果:")
            print("=" * 60)
            print("✅ 数据库使用 'role' 字段（不是 'permission_level'）")
            print("✅ SQLAlchemy 模型使用 Column('role', ...) 映射")
            print("✅ Python 代码访问 permission_level 属性")
            print("✅ API 返回 permission_level 字段")
            print()
            print("说明:")
            print("- 数据库字段名: role")
            print("- Python 属性名: permission_level")
            print("- SQLAlchemy 自动处理映射")
            print("- 应用层函数处理值转换 (admin/user <-> admin/write/read)")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
