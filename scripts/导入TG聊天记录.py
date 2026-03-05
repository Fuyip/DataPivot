import os
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 尝试从 database.py 导入 engine，如果失败则提示用户
try:
    from database import engine
except ImportError:
    print("错误: 无法找到 database.py 或其中的 engine 对象。")
    print("请确保 database.py 在同一目录下，并且包含类似 'engine = create_engine(...)' 的代码。")
    exit(1)

# 定义ORM基类
Base = declarative_base()


# 定义 Telegram 消息模型
class TelegramMessage(Base):
    __tablename__ = 'tg_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_msg_id = Column(Integer, index=True, comment='Telegram原始消息ID')
    sender_name = Column(String(255), comment='发送者昵称')
    date_sent = Column(DateTime, comment='发送时间')
    content_text = Column(Text, comment='文本内容')
    reply_to_id = Column(Integer, nullable=True, comment='回复的消息ID')
    media_path = Column(String(500), nullable=True, comment='媒体文件路径')
    source_file = Column(String(255), comment='来源HTML文件')


# 创建表（如果表不存在）
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()


def parse_date(date_str):
    """
    解析时间字符串，例如: "17.07.2022 11:54:39 UTC+08:00"
    """
    try:
        # 移除 'UTC' 并处理时区 (这里简化处理，假设保留原时间，忽略时区转换或视为本地时间)
        # 如果需要严格的时区控制，可以使用 dateutil.parser
        clean_date_str = date_str.split(" UTC")[0].strip()
        dt = datetime.strptime(clean_date_str, "%d.%m.%Y %H:%M:%S")
        return dt
    except Exception as e:
        print(f"日期解析错误: {date_str} - {e}")
        return None


def parse_html_file(file_path):
    """
    解析单个 HTML 文件并返回消息对象列表
    """
    print(f"正在解析文件: {file_path}")
    messages_data = []

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

        # 查找所有消息块
        message_divs = soup.find_all('div', class_='message')

        for msg in message_divs:
            # 忽略 'service' 类型的系统消息（如日期分割线）
            if 'service' in msg.get('class', []):
                continue

            try:
                # 1. 提取 Telegram 消息 ID (格式如 "message123456")
                div_id = msg.get('id', '')
                tg_id = int(div_id.replace('message', '')) if div_id.startswith('message') else None

                # 2. 提取发送者
                from_name_div = msg.find('div', class_='from_name')
                sender = from_name_div.get_text(strip=True) if from_name_div else None

                # 3. 提取时间
                date_div = msg.find('div', class_='date')
                date_str = date_div.get('title') if date_div else None
                date_obj = parse_date(date_str) if date_str else None

                # 4. 提取文本内容
                text_div = msg.find('div', class_='text')
                text_content = text_div.get_text(separator='\n', strip=True) if text_div else None

                # 5. 提取回复引用 ID
                reply_div = msg.find('div', class_='reply_to')
                reply_id = None
                if reply_div:
                    link = reply_div.find('a')
                    if link and link.get('href'):
                        # href="#go_to_message178929"
                        match = re.search(r'message(\d+)', link.get('href'))
                        if match:
                            reply_id = int(match.group(1))

                # 6. 提取媒体路径 (如果是图片或文件)
                media_path = None
                media_wrap = msg.find('div', class_='media_wrap')
                if media_wrap:
                    photo_link = media_wrap.find('a', class_='photo_wrap') or media_wrap.find('a',
                                                                                              class_='video_file_wrap')
                    if photo_link:
                        media_path = photo_link.get('href')

                # 构建对象
                if tg_id:
                    msg_obj = TelegramMessage(
                        tg_msg_id=tg_id,
                        sender_name=sender,
                        date_sent=date_obj,
                        content_text=text_content,
                        reply_to_id=reply_id,
                        media_path=media_path,
                        source_file=os.path.basename(file_path)
                    )
                    messages_data.append(msg_obj)

            except Exception as e:
                print(f"解析消息出错 (ID: {div_id}): {e}")
                continue

    return messages_data


def main():
    base_dir = 'TG'  # 设置为你的HTML文件所在的根目录
    all_files = []

    # 1. 递归查找所有 messages*.html 文件
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            # 匹配 messages.html, messages2.html, messages15.html 等

            if file.startswith('messages') and file.endswith('.html'):
                full_path = os.path.join(root, file)
                all_files.append(full_path)

    print(f"找到 {len(all_files)} 个聊天记录文件。")

    # 2. 逐个解析并入库
    total_inserted = 0
    flag=1
    for file_path in all_files:
        if file_path=='TG/ChatExport_2025-02-03 (9)/messages2.html':
            flag=0
        if flag:
            continue
        msgs = parse_html_file(file_path)
        if msgs:
            # 批量插入以提高性能
            session.bulk_save_objects(msgs)
            session.commit()
            total_inserted += len(msgs)
            print(f"  - 已存入 {len(msgs)} 条消息。")

    print(f"完成！总计导入 {total_inserted} 条消息。")


if __name__ == '__main__':
    main()