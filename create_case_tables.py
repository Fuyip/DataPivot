"""
创建案件管理相关数据库表
使用SQLAlchemy自动创建表结构
"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from database import Base, system_engine
from backend.models.case import Case, UserCasePermission
from backend.models.user import User


def create_case_tables():
    """创建案件管理相关表"""
    print("开始创建案件管理相关表...")

    try:
        # 创建所有表
        Base.metadata.create_all(bind=system_engine)
        print("✓ 案件管理表创建成功！")
        print("  - cases (案件表)")
        print("  - user_case_permissions (用户案件权限表)")
    except Exception as e:
        print(f"✗ 创建表失败: {str(e)}")
        return False

    return True


if __name__ == "__main__":
    success = create_case_tables()
    sys.exit(0 if success else 1)
