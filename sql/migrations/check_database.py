"""
检查数据库当前字段名
"""
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def check_database():
    """检查数据库字段"""
    # 数据库配置
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Aa112211"
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306

    # 创建数据库连接
    encoded_password = quote_plus(MYSQL_PASSWORD)
    database_url = f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/datapivot?charset=utf8mb4"

    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            print("检查数据库表结构...\n")

            # 检查字段名
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'datapivot'
                AND TABLE_NAME = 'user_case_permissions'
                AND COLUMN_NAME IN ('role', 'permission_level')
            """))

            print("user_case_permissions 表的权限字段：")
            for row in result:
                print(f"  字段名: {row[0]}")
                print(f"  类型: {row[1]}")
                print(f"  默认值: {row[2]}")
                print(f"  注释: {row[3]}")
                print()

            # 检查现有数据
            result = conn.execute(text("""
                SELECT COUNT(*) as total FROM user_case_permissions
            """))
            total = result.fetchone()[0]
            print(f"权限记录总数: {total}")

            if total > 0:
                # 尝试查询 role 字段
                try:
                    result = conn.execute(text("""
                        SELECT role, COUNT(*) as count
                        FROM user_case_permissions
                        GROUP BY role
                    """))
                    print("\n使用 'role' 字段的权限分布：")
                    for row in result:
                        print(f"  {row[0]}: {row[1]} 条")
                except Exception as e:
                    print(f"\n'role' 字段不存在: {e}")

                # 尝试查询 permission_level 字段
                try:
                    result = conn.execute(text("""
                        SELECT permission_level, COUNT(*) as count
                        FROM user_case_permissions
                        GROUP BY permission_level
                    """))
                    print("\n使用 'permission_level' 字段的权限分布：")
                    for row in result:
                        print(f"  {row[0]}: {row[1]} 条")
                except Exception as e:
                    print(f"\n'permission_level' 字段不存在: {e}")

    except Exception as e:
        print(f"\n❌ 检查失败: {str(e)}")
        print("\n可能的原因：")
        print("1. MySQL 服务未启动")
        print("2. 数据库连接配置错误")
        print("3. datapivot 数据库不存在")
    finally:
        engine.dispose()

if __name__ == "__main__":
    check_database()
