#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库结构生成脚本

功能：
1. 连接到现有数据库
2. 导出所有表结构的 CREATE TABLE 语句
3. 导出所有视图的 CREATE VIEW 语句
4. 生成完整的数据库初始化 SQL 文件

使用方法：
    python generate_db_schema.py

输出文件：
    sql/schema/database_schema.sql - 完整数据库结构
    sql/schema/tables.sql - 仅表结构
    sql/schema/views.sql - 仅视图结构
"""

import pymysql
from config import config
from datetime import datetime
import os


class DatabaseSchemaGenerator:
    """数据库结构生成器"""

    def __init__(self):
        self.host = config.MYSQL_HOST
        self.port = int(config.MYSQL_PORT)
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.database = config.MYSQL_DB
        self.connection = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            self.cursor = self.connection.cursor()
            print(f"✓ 成功连接到数据库: {self.database}")
            return True
        except Exception as e:
            print(f"✗ 数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("✓ 数据库连接已关闭")

    def get_all_tables(self):
        """获取所有表名"""
        self.cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        tables = [row[0] for row in self.cursor.fetchall()]
        print(f"✓ 找到 {len(tables)} 个表")
        return tables

    def get_all_views(self):
        """获取所有视图名"""
        self.cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = [row[0] for row in self.cursor.fetchall()]
        print(f"✓ 找到 {len(views)} 个视图")
        return views

    def get_table_create_statement(self, table_name):
        """获取表的 CREATE TABLE 语句"""
        try:
            self.cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            result = self.cursor.fetchone()
            if result:
                return result[1]
        except Exception as e:
            print(f"✗ 获取表 {table_name} 结构失败: {e}")
        return None

    def get_view_create_statement(self, view_name):
        """获取视图的 CREATE VIEW 语句"""
        try:
            self.cursor.execute(f"SHOW CREATE VIEW `{view_name}`")
            result = self.cursor.fetchone()
            if result:
                # 清理视图定义，移除 DEFINER 信息
                create_view = result[1]
                # 移除 DEFINER 子句
                if 'DEFINER=' in create_view:
                    start = create_view.find('DEFINER=')
                    end = create_view.find('VIEW', start)
                    if start != -1 and end != -1:
                        create_view = create_view[:start] + create_view[end:]
                return create_view
        except Exception as e:
            print(f"✗ 获取视图 {view_name} 结构失败: {e}")
        return None

    def get_table_info(self, table_name):
        """获取表的详细信息（字段、索引等）"""
        try:
            # 获取字段信息
            self.cursor.execute(f"DESCRIBE `{table_name}`")
            columns = self.cursor.fetchall()

            # 获取索引信息
            self.cursor.execute(f"SHOW INDEX FROM `{table_name}`")
            indexes = self.cursor.fetchall()

            # 获取表注释
            self.cursor.execute(f"""
                SELECT TABLE_COMMENT
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = '{self.database}'
                AND TABLE_NAME = '{table_name}'
            """)
            comment_result = self.cursor.fetchone()
            table_comment = comment_result[0] if comment_result else ""

            return {
                'columns': columns,
                'indexes': indexes,
                'comment': table_comment
            }
        except Exception as e:
            print(f"✗ 获取表 {table_name} 信息失败: {e}")
            return None

    def generate_schema_file(self, output_file, include_tables=True, include_views=True):
        """生成数据库结构文件"""
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- DataPivot 数据库结构\n")
                f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 数据库: {self.database}\n")
                f.write(f"-- 主机: {self.host}:{self.port}\n")
                f.write(f"\n")
                f.write(f"-- 使用方法:\n")
                f.write(f"-- mysql -u{self.user} -p {self.database} < {os.path.basename(output_file)}\n")
                f.write(f"\n")
                f.write(f"SET NAMES utf8mb4;\n")
                f.write(f"SET FOREIGN_KEY_CHECKS = 0;\n")
                f.write(f"\n")

                # 生成表结构
                if include_tables:
                    tables = self.get_all_tables()
                    f.write(f"-- ----------------------------\n")
                    f.write(f"-- 表结构 (共 {len(tables)} 个)\n")
                    f.write(f"-- ----------------------------\n\n")

                    for i, table in enumerate(tables, 1):
                        print(f"  [{i}/{len(tables)}] 导出表: {table}")
                        create_statement = self.get_table_create_statement(table)
                        if create_statement:
                            f.write(f"-- ----------------------------\n")
                            f.write(f"-- Table structure for {table}\n")
                            f.write(f"-- ----------------------------\n")
                            f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                            f.write(f"{create_statement};\n\n")

                # 生成视图结构
                if include_views:
                    views = self.get_all_views()
                    if views:
                        f.write(f"\n-- ----------------------------\n")
                        f.write(f"-- 视图结构 (共 {len(views)} 个)\n")
                        f.write(f"-- ----------------------------\n\n")

                        for i, view in enumerate(views, 1):
                            print(f"  [{i}/{len(views)}] 导出视图: {view}")
                            create_statement = self.get_view_create_statement(view)
                            if create_statement:
                                f.write(f"-- ----------------------------\n")
                                f.write(f"-- View structure for {view}\n")
                                f.write(f"-- ----------------------------\n")
                                f.write(f"DROP VIEW IF EXISTS `{view}`;\n")
                                f.write(f"{create_statement};\n\n")

                # 写入文件尾
                f.write(f"SET FOREIGN_KEY_CHECKS = 1;\n")

            print(f"✓ 数据库结构已导出到: {output_file}")
            return True

        except Exception as e:
            print(f"✗ 生成结构文件失败: {e}")
            return False

    def generate_markdown_documentation(self, output_file):
        """生成 Markdown 格式的数据库文档"""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# {self.database} 数据库结构文档\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 表结构文档
                tables = self.get_all_tables()
                f.write(f"## 数据表 (共 {len(tables)} 个)\n\n")

                for i, table in enumerate(tables, 1):
                    print(f"  [{i}/{len(tables)}] 生成表文档: {table}")
                    table_info = self.get_table_info(table)

                    if table_info:
                        f.write(f"### {i}. {table}\n\n")
                        if table_info['comment']:
                            f.write(f"**说明**: {table_info['comment']}\n\n")

                        # 字段信息
                        f.write(f"**字段列表**:\n\n")
                        f.write(f"| 字段名 | 类型 | 允许空 | 键 | 默认值 | 额外说明 |\n")
                        f.write(f"|--------|------|--------|-----|--------|----------|\n")

                        for col in table_info['columns']:
                            field = col[0]
                            type_ = col[1]
                            null = col[2]
                            key = col[3]
                            default = col[4] if col[4] is not None else ''
                            extra = col[5]
                            f.write(f"| {field} | {type_} | {null} | {key} | {default} | {extra} |\n")

                        f.write(f"\n")

                        # 索引信息
                        if table_info['indexes']:
                            f.write(f"**索引**:\n\n")
                            index_dict = {}
                            for idx in table_info['indexes']:
                                key_name = idx[2]
                                if key_name not in index_dict:
                                    index_dict[key_name] = {
                                        'unique': idx[1] == 0,
                                        'columns': []
                                    }
                                index_dict[key_name]['columns'].append(idx[4])

                            for key_name, info in index_dict.items():
                                unique_str = "唯一索引" if info['unique'] else "普通索引"
                                columns_str = ", ".join(info['columns'])
                                f.write(f"- `{key_name}` ({unique_str}): {columns_str}\n")

                            f.write(f"\n")

                        f.write(f"---\n\n")

                # 视图文档
                views = self.get_all_views()
                if views:
                    f.write(f"## 视图 (共 {len(views)} 个)\n\n")
                    for i, view in enumerate(views, 1):
                        f.write(f"{i}. `{view}`\n")
                    f.write(f"\n")

            print(f"✓ 数据库文档已生成: {output_file}")
            return True

        except Exception as e:
            print(f"✗ 生成文档失败: {e}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("DataPivot 数据库结构生成工具")
    print("=" * 60)
    print()

    generator = DatabaseSchemaGenerator()

    # 连接数据库
    if not generator.connect():
        return

    try:
        # 生成完整结构文件
        print("\n[1/4] 生成完整数据库结构...")
        generator.generate_schema_file(
            'sql/schema/database_schema.sql',
            include_tables=True,
            include_views=True
        )

        # 生成仅表结构文件
        print("\n[2/4] 生成表结构文件...")
        generator.generate_schema_file(
            'sql/schema/tables.sql',
            include_tables=True,
            include_views=False
        )

        # 生成仅视图结构文件
        print("\n[3/4] 生成视图结构文件...")
        generator.generate_schema_file(
            'sql/schema/views.sql',
            include_tables=False,
            include_views=True
        )

        # 生成 Markdown 文档
        print("\n[4/4] 生成数据库文档...")
        generator.generate_markdown_documentation(
            'docs/DATABASE_SCHEMA.md'
        )

        print("\n" + "=" * 60)
        print("✓ 所有文件生成完成！")
        print("=" * 60)
        print("\n生成的文件:")
        print("  - sql/schema/database_schema.sql  (完整数据库结构)")
        print("  - sql/schema/tables.sql           (仅表结构)")
        print("  - sql/schema/views.sql            (仅视图结构)")
        print("  - docs/DATABASE_SCHEMA.md         (数据库文档)")
        print()

    except Exception as e:
        print(f"\n✗ 执行过程中出错: {e}")

    finally:
        # 关闭连接
        generator.close()


if __name__ == "__main__":
    main()
