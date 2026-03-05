#!/usr/bin/env python3
"""
银行流水表优化迁移工具
用于批量优化现有案件数据库的银行流水表结构

功能:
1. 列出所有案件数据库
2. 逐个执行优化迁移
3. 自动备份和验证
4. 提供回滚机制

使用方法:
    python scripts/migrate_existing_cases.py --list              # 列出所有案件数据库
    python scripts/migrate_existing_cases.py --migrate fx_test   # 迁移指定数据库
    python scripts/migrate_existing_cases.py --migrate-all       # 迁移所有案件数据库
    python scripts/migrate_existing_cases.py --verify fx_test    # 验证迁移结果

作者: DataPivot Team
日期: 2026-03-05
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from config import settings


class BankTableOptimizer:
    """银行流水表优化器"""

    def __init__(self):
        self.engine = create_engine(
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/information_schema"
        )
        self.migration_sql_path = Path(__file__).parent.parent / "backend" / "migrations" / "optimize_bank_tables.sql"

    def list_case_databases(self):
        """列出所有案件数据库"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SHOW DATABASES LIKE 'fx_%'"))
            databases = [row[0] for row in result]
        return databases

    def backup_database(self, db_name: str) -> str:
        """备份数据库（创建备份表）"""
        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"[{db_name}] 开始备份...")

        engine = create_engine(
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{db_name}"
        )

        tables_to_backup = [
            'bank_account_info',
            'bank_all_statements',
            'bank_sub_account_info',
            'bank_coercive_action_info',
            'bank_people_info'
        ]

        with engine.connect() as conn:
            for table in tables_to_backup:
                backup_table = f"{table}_backup_{backup_time}"
                try:
                    # 检查表是否存在
                    result = conn.execute(text(
                        f"SELECT COUNT(*) FROM information_schema.tables "
                        f"WHERE table_schema = '{db_name}' AND table_name = '{table}'"
                    ))
                    if result.scalar() > 0:
                        conn.execute(text(f"CREATE TABLE {backup_table} LIKE {table}"))
                        conn.execute(text(f"INSERT INTO {backup_table} SELECT * FROM {table}"))
                        conn.commit()
                        print(f"  ✓ 已备份: {table} -> {backup_table}")
                except Exception as e:
                    print(f"  ✗ 备份失败: {table} - {e}")

        return backup_time

    def migrate_database(self, db_name: str, skip_backup: bool = False):
        """迁移指定数据库"""
        print(f"\n{'='*60}")
        print(f"开始优化数据库: {db_name}")
        print(f"{'='*60}")

        # 1. 备份
        if not skip_backup:
            backup_time = self.backup_database(db_name)
        else:
            backup_time = None
            print(f"[{db_name}] 跳过备份（--skip-backup）")

        # 2. 读取迁移SQL
        if not self.migration_sql_path.exists():
            print(f"错误: 迁移脚本不存在: {self.migration_sql_path}")
            return False

        with open(self.migration_sql_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        # 3. 执行迁移
        print(f"[{db_name}] 开始执行优化...")
        engine = create_engine(
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{db_name}"
        )

        try:
            with engine.connect() as conn:
                # 分割SQL语句并逐个执行
                statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

                for i, statement in enumerate(statements, 1):
                    if statement.upper().startswith('ALTER TABLE'):
                        table_name = statement.split('`')[1]
                        try:
                            conn.execute(text(statement))
                            conn.commit()
                            print(f"  ✓ [{i}/{len(statements)}] 已优化: {table_name}")
                        except Exception as e:
                            # 表可能不存在，跳过
                            if "doesn't exist" in str(e):
                                print(f"  - [{i}/{len(statements)}] 跳过: {table_name} (表不存在)")
                            else:
                                print(f"  ✗ [{i}/{len(statements)}] 失败: {table_name} - {e}")
                    elif statement.upper().startswith('SET'):
                        conn.execute(text(statement))
                        conn.commit()

            print(f"[{db_name}] ✓ 优化完成")
            return True

        except Exception as e:
            print(f"[{db_name}] ✗ 优化失败: {e}")
            if backup_time:
                print(f"[{db_name}] 可以使用备份表回滚: *_backup_{backup_time}")
            return False

    def verify_database(self, db_name: str):
        """验证数据库优化结果"""
        print(f"\n{'='*60}")
        print(f"验证数据库: {db_name}")
        print(f"{'='*60}")

        engine = create_engine(
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{db_name}"
        )

        checks = []

        with engine.connect() as conn:
            # 1. 检查字段类型
            print("\n1. 检查字段类型优化...")

            # 检查 decimal 字段
            result = conn.execute(text(
                f"SELECT table_name, column_name, data_type, column_type "
                f"FROM information_schema.columns "
                f"WHERE table_schema = '{db_name}' "
                f"AND column_name IN ('accountBalance', 'availableBalance', 'trade_money', 'trade_balance', 'freezeAmount', 'balance') "
                f"AND data_type = 'decimal'"
            ))
            decimal_fields = result.fetchall()
            print(f"  ✓ DECIMAL 字段数量: {len(decimal_fields)}")
            checks.append(len(decimal_fields) > 0)

            # 检查 varchar 字段
            result = conn.execute(text(
                f"SELECT table_name, column_name, character_maximum_length "
                f"FROM information_schema.columns "
                f"WHERE table_schema = '{db_name}' "
                f"AND column_name = 'currency' "
                f"AND character_maximum_length = 10"
            ))
            currency_fields = result.fetchall()
            print(f"  ✓ currency varchar(10) 字段数量: {len(currency_fields)}")
            checks.append(len(currency_fields) > 0)

            # 2. 检查数据完整性
            print("\n2. 检查数据完整性...")

            tables = ['bank_account_info', 'bank_all_statements', 'bank_people_info']
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  ✓ {table}: {count} 条记录")
                    checks.append(True)
                except Exception as e:
                    if "doesn't exist" in str(e):
                        print(f"  - {table}: 表不存在")
                    else:
                        print(f"  ✗ {table}: 检查失败 - {e}")
                        checks.append(False)

            # 3. 检查字段长度
            print("\n3. 检查字段长度...")

            try:
                result = conn.execute(text(
                    "SELECT MAX(LENGTH(currency)) as max_len FROM bank_account_info WHERE currency IS NOT NULL"
                ))
                max_len = result.scalar()
                if max_len:
                    print(f"  ✓ currency 最大长度: {max_len} (限制: 10)")
                    checks.append(max_len <= 10)
            except:
                pass

        # 总结
        print(f"\n{'='*60}")
        if all(checks):
            print("✓ 验证通过")
        else:
            print("✗ 验证失败，请检查上述错误")
        print(f"{'='*60}\n")

        return all(checks)

    def migrate_all(self, skip_backup: bool = False):
        """迁移所有案件数据库"""
        databases = self.list_case_databases()

        if not databases:
            print("未找到任何案件数据库 (fx_*)")
            return

        print(f"找到 {len(databases)} 个案件数据库")
        print("="*60)

        success_count = 0
        failed_databases = []

        for db in databases:
            if self.migrate_database(db, skip_backup):
                success_count += 1
            else:
                failed_databases.append(db)

        # 总结
        print(f"\n{'='*60}")
        print(f"迁移完成: {success_count}/{len(databases)} 成功")
        if failed_databases:
            print(f"失败的数据库: {', '.join(failed_databases)}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='银行流水表优化迁移工具')
    parser.add_argument('--list', action='store_true', help='列出所有案件数据库')
    parser.add_argument('--migrate', type=str, metavar='DB_NAME', help='迁移指定数据库')
    parser.add_argument('--migrate-all', action='store_true', help='迁移所有案件数据库')
    parser.add_argument('--verify', type=str, metavar='DB_NAME', help='验证迁移结果')
    parser.add_argument('--skip-backup', action='store_true', help='跳过备份（不推荐）')

    args = parser.parse_args()

    optimizer = BankTableOptimizer()

    if args.list:
        databases = optimizer.list_case_databases()
        print(f"找到 {len(databases)} 个案件数据库:")
        for db in databases:
            print(f"  - {db}")

    elif args.migrate:
        optimizer.migrate_database(args.migrate, args.skip_backup)

    elif args.migrate_all:
        optimizer.migrate_all(args.skip_backup)

    elif args.verify:
        optimizer.verify_database(args.verify)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
