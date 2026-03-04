"""
执行数据库迁移脚本
将 role 字段改为 permission_level，将 user 值改为 write
"""
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def run_migration():
    """执行数据库迁移"""
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
            print("开始执行数据库迁移...")

            # 步骤1：检查当前表结构
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'datapivot'
                AND TABLE_NAME = 'user_case_permissions'
                AND COLUMN_NAME = 'role'
            """))
            column_exists = result.fetchone()[0]

            print(f"检查字段名: {'role' if column_exists > 0 else 'permission_level'}")

            # 步骤2：如果是 role 字段，重命名为 permission_level
            if column_exists > 0:
                print("正在重命名字段 role -> permission_level...")
                conn.execute(text("""
                    ALTER TABLE user_case_permissions
                    CHANGE COLUMN role permission_level
                    VARCHAR(20) DEFAULT 'read'
                    COMMENT '权限级别: read/write/admin'
                """))
                conn.commit()
                print("字段重命名完成")
            else:
                print("字段已经是 permission_level，跳过重命名")

            # 步骤3：更新现有数据（将 user 映射为 write）
            print("正在更新权限值 user -> write...")
            result = conn.execute(text("""
                UPDATE user_case_permissions
                SET permission_level = 'write'
                WHERE permission_level = 'user'
            """))
            conn.commit()
            print(f"更新了 {result.rowcount} 条记录")

            # 步骤4：验证迁移结果
            print("\n迁移完成，当前权限分布：")
            result = conn.execute(text("""
                SELECT permission_level, COUNT(*) as count
                FROM user_case_permissions
                GROUP BY permission_level
            """))

            for row in result:
                print(f"  {row[0]}: {row[1]} 条")

            print("\n✅ 数据库迁移成功完成！")

    except Exception as e:
        print(f"\n❌ 数据库迁移失败: {str(e)}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()
