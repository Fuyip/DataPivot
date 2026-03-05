#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出 fx_test 数据库结构脚本

功能：
1. 连接到 fx_test 数据库
2. 导出所有表结构的 CREATE TABLE 语句
3. 导出所有视图的 CREATE VIEW 语句
4. 生成案件数据库初始化模板

使用方法：
    python export_fx_test_schema.py

输出文件：
    sql/schema/fx_test_schema.sql - fx_test 完整数据库结构
    sql/schema/case_template.sql - 案件数据库初始化模板
"""

import pymysql
from config import config
from datetime import datetime
import os


class FxTestSchemaExporter:
    """fx_test 数据库结构导出器"""

    def __init__(self):
        self.host = config.MYSQL_HOST
        self.port = int(config.MYSQL_PORT)
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.database = "fx_test"  # 固定为 fx_test 数据库
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
            print(f"  请确保 fx_test 数据库存在")
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

    def export_schema(self, output_file):
        """导出完整数据库结构"""
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- fx_test 数据库结构\n")
                f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 数据库: {self.database}\n")
                f.write(f"-- 主机: {self.host}:{self.port}\n")
                f.write(f"\n")
                f.write(f"-- 说明: 此文件为案件数据库的标准结构模板\n")
                f.write(f"-- 所有新建案件数据库都应使用此结构\n")
                f.write(f"\n")
                f.write(f"SET NAMES utf8mb4;\n")
                f.write(f"SET FOREIGN_KEY_CHECKS = 0;\n")
                f.write(f"\n")

                # 导出表结构
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

                # 导出视图结构
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
            print(f"✗ 导出结构文件失败: {e}")
            return False

    def create_case_template(self, output_file):
        """创建案件数据库初始化模板"""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- 案件数据库初始化模板\n")
                f.write(f"-- 基于 fx_test 数据库结构\n")
                f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"\n")
                f.write(f"-- 使用方法:\n")
                f.write(f"-- 1. 创建案件数据库: CREATE DATABASE case_xxx CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
                f.write(f"-- 2. 导入结构: mysql -u{self.user} -p case_xxx < case_template.sql\n")
                f.write(f"\n")
                f.write(f"SET NAMES utf8mb4;\n")
                f.write(f"SET FOREIGN_KEY_CHECKS = 0;\n")
                f.write(f"\n")

                # 导出表结构
                tables = self.get_all_tables()
                f.write(f"-- ----------------------------\n")
                f.write(f"-- 案件数据库表结构 (共 {len(tables)} 个)\n")
                f.write(f"-- ----------------------------\n\n")

                for table in tables:
                    create_statement = self.get_table_create_statement(table)
                    if create_statement:
                        f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                        f.write(f"{create_statement};\n\n")

                # 导出视图结构
                views = self.get_all_views()
                if views:
                    f.write(f"-- ----------------------------\n")
                    f.write(f"-- 案件数据库视图 (共 {len(views)} 个)\n")
                    f.write(f"-- ----------------------------\n\n")

                    for view in views:
                        create_statement = self.get_view_create_statement(view)
                        if create_statement:
                            f.write(f"DROP VIEW IF EXISTS `{view}`;\n")
                            f.write(f"{create_statement};\n\n")

                f.write(f"SET FOREIGN_KEY_CHECKS = 1;\n")

            print(f"✓ 案件数据库模板已创建: {output_file}")
            return True

        except Exception as e:
            print(f"✗ 创建模板文件失败: {e}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("fx_test 数据库结构导出工具")
    print("=" * 60)
    print()

    exporter = FxTestSchemaExporter()

    # 连接数据库
    if not exporter.connect():
        print("\n提示: 如果 fx_test 数据库不存在，请先创建或指定正确的数据库名称")
        return

    try:
        # 导出 fx_test 完整结构
        print("\n[1/2] 导出 fx_test 数据库完整结构...")
        exporter.export_schema('sql/schema/fx_test_schema.sql')

        # 创建案件数据库模板
        print("\n[2/2] 创建案件数据库初始化模板...")
        exporter.create_case_template('sql/schema/case_template.sql')

        print("\n" + "=" * 60)
        print("✓ 导出完成！")
        print("=" * 60)
        print("\n生成的文件:")
        print("  - sql/schema/fx_test_schema.sql  (fx_test 完整结构)")
        print("  - sql/schema/case_template.sql   (案件数据库模板)")
        print("\n使用案件模板创建新数据库:")
        print("  1. CREATE DATABASE case_xxx CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("  2. mysql -uroot -p case_xxx < sql/schema/case_template.sql")
        print()

    except Exception as e:
        print(f"\n✗ 执行过程中出错: {e}")

    finally:
        # 关闭连接
        exporter.close()


if __name__ == "__main__":
    main()
