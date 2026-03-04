"""
数据库初始化工具
使用 SQLAlchemy 创建表并插入初始数据
"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from backend.models.user import User
from backend.core.security import get_password_hash


def create_tables():
    """创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")


def create_default_admin(db: Session):
    """创建默认管理员账户"""
    print("正在检查默认管理员账户...")

    # 检查是否已存在管理员账户
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("✓ 管理员账户已存在，跳过创建")
        return

    # 创建管理员账户
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="系统管理员",
        role="admin",
        is_active=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print("✓ 默认管理员账户创建成功")
    print(f"  用户名: admin")
    print(f"  密码: admin123")
    print(f"  ⚠️  请在生产环境中立即修改默认密码！")


def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("DataPivot 数据库初始化")
    print("=" * 50)

    try:
        # 创建表
        create_tables()

        # 创建默认管理员
        db = SessionLocal()
        try:
            create_default_admin(db)
        finally:
            db.close()

        print("=" * 50)
        print("✓ 数据库初始化完成！")
        print("=" * 50)

    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_database()
