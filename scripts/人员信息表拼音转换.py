from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base
from pypinyin import lazy_pinyin
from database import engine

# 1. 定义ORM模型
Base = declarative_base()


class PinyinTurn(Base):
    __tablename__ = 'pinyin_turn'

    # 设置字符集和排序规则为 utf8mb4_0900_ai_ci
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_0900_ai_ci'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')
    中文 = Column(String(255), comment='原始中文姓名')
    pinyin = Column(String(255), comment='转换后的拼音')
    标签 = Column(String(50), comment='数据标签')


def process_and_migrate():
    # 尝试创建表（只有当表不存在时才会创建，不会覆盖旧表）
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("开始读取数据...")

        # 确认源表名称。根据之前的日志，表名可能是 "人员电子档案" 或 "人员电子档案表"
        # 这里使用 text() 直接查询，请确保数据库中表名一致
        source_table = "人员电子档案"

        sql = f"SELECT `姓名` FROM `{source_table}` WHERE `姓名` IS NOT NULL AND `姓名` != ''"
        result = session.execute(text(sql))
        original_names = result.fetchall()

        if not original_names:
            print(f"未在表 '{source_table}' 中找到数据。")
            return

        print(f"读取到 {len(original_names)} 条数据，正在转换...")

        batch_data = []
        for row in original_names:
            name_cn = row[0]
            # 转换为拼音字符串
            name_py = "".join(lazy_pinyin(name_cn))

            record = {
                "中文": name_cn,
                "pinyin": name_py,
                "标签": "姓名"
            }
            batch_data.append(record)

        if batch_data:
            # 批量插入
            session.bulk_insert_mappings(PinyinTurn, batch_data)
            session.commit()
            print(f"成功！已将 {len(batch_data)} 条记录写入 'pinyin_turn' 表。")
        else:
            print("没有有效数据需要处理。")

    except Exception as e:
        session.rollback()
        print(f"发生错误: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    process_and_migrate()