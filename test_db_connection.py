#!/usr/bin/env python3
"""测试数据库连接"""
import pymysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'datapivot'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        print("[成功] 数据库连接成功！")
        print(f"  主机: {os.getenv('MYSQL_HOST')}")
        print(f"  端口: {os.getenv('MYSQL_PORT')}")
        print(f"  用户: {os.getenv('MYSQL_USER')}")
        print(f"  数据库: {os.getenv('MYSQL_DB')}")

        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"  MySQL版本: {version['VERSION()']}")

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"  数据表数量: {len(tables)}")
            if tables:
                print("  现有数据表:")
                for table in tables:
                    print(f"    - {list(table.values())[0]}")

        connection.close()
        return True

    except pymysql.Error as e:
        print(f"[失败] 数据库连接失败！")
        print(f"  错误代码: {e.args[0]}")
        print(f"  错误信息: {e.args[1]}")
        return False
    except Exception as e:
        print(f"[错误] 发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_mysql_connection()
