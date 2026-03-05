#!/usr/bin/env python3
"""执行字段长度修复的SQL脚本"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from config import config, quote_plus

def fix_field_lengths():
    """修复银行流水表字段长度"""
    sql_content = """
ALTER TABLE `bank_all_statements_tmp`
  MODIFY COLUMN `ip_loc` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  MODIFY COLUMN `mac_loc` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'MAC地址',
  MODIFY COLUMN `transaction_loc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地',
  MODIFY COLUMN `summary_description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '摘要说明',
  MODIFY COLUMN `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  MODIFY COLUMN `rival_card_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易对手账卡号',
  MODIFY COLUMN `transaction_teller_num` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易柜员号',
  MODIFY COLUMN `card_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易卡号',
  MODIFY COLUMN `card_account` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易账号',
  MODIFY COLUMN `transaction_serial_num` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易流水号';

ALTER TABLE `bank_all_statements`
  MODIFY COLUMN `ip_loc` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'IP地址',
  MODIFY COLUMN `mac_loc` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'MAC地址',
  MODIFY COLUMN `transaction_loc` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易发生地',
  MODIFY COLUMN `summary_description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '摘要说明',
  MODIFY COLUMN `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '备注',
  MODIFY COLUMN `rival_card_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易对手账卡号',
  MODIFY COLUMN `transaction_teller_num` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易柜员号',
  MODIFY COLUMN `card_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易卡号',
  MODIFY COLUMN `card_account` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易账号',
  MODIFY COLUMN `transaction_serial_num` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '交易流水号';
"""

    encoded_password = quote_plus(config.MYSQL_PASSWORD)
    system_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/?charset=utf8mb4"
    system_engine = create_engine(system_url)

    with system_engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES LIKE 'fx_%'"))
        databases = [row[0] for row in result]

    print(f"找到 {len(databases)} 个案件数据库")

    for db_name in databases:
        case_url = f"mysql+pymysql://{config.MYSQL_USER}:{encoded_password}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{db_name}?charset=utf8mb4"

        try:
            engine = create_engine(case_url)
            with engine.connect() as conn:
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                for stmt in statements:
                    conn.execute(text(stmt))
                conn.commit()
            print(f"✓ 修复完成: {db_name}")
        except Exception as e:
            print(f"✗ 修复失败: {db_name} - {e}")

    print("\n所有数据库字段长度修复完成！")

if __name__ == "__main__":
    fix_field_lengths()
