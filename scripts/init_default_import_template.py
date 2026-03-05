#!/usr/bin/env python3
"""
初始化默认导入规则模板
从 bank_config.py 导入现有配置创建默认模板
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from backend.models.import_rule import (
    ImportRuleTemplate, ImportFieldMapping, ImportCleaningRule
)
from bank_config import NAME_DICT, REG_STR, REG_TIME_STR
from loguru import logger


def init_default_template():
    """初始化默认模板"""
    db: Session = SessionLocal()

    try:
        # 检查是否已存在默认模板
        existing = db.query(ImportRuleTemplate).filter_by(template_name="默认模板").first()
        if existing:
            logger.info("默认模板已存在，跳过初始化")
            return

        logger.info("开始创建默认导入规则模板...")

        # 创建默认模板
        template = ImportRuleTemplate(
            template_name="默认模板",
            description="从 bank_config.py 导入的默认配置",
            is_default=True,
            is_active=True,
            created_by=1  # 假设系统管理员ID为1
        )
        db.add(template)
        db.flush()

        logger.info(f"已创建模板: {template.template_name} (ID: {template.id})")

        # 导入字段映射
        mapping_count = 0
        for data_type, fields in NAME_DICT.items():
            sort_order = 0
            for db_field_name, (csv_column_name, field_type) in fields.items():
                mapping = ImportFieldMapping(
                    template_id=template.id,
                    data_type=data_type,
                    db_field_name=db_field_name,
                    csv_column_name=csv_column_name,
                    field_type=field_type,
                    sort_order=sort_order,
                    is_required=False,
                    default_value=None
                )
                db.add(mapping)
                mapping_count += 1
                sort_order += 1

        logger.info(f"已导入 {mapping_count} 条字段映射")

        # 导入清洗规则
        cleaning_rules = [
            {
                'rule_name': '通用清洗规则',
                'rule_type': 'general',
                'regex_pattern': REG_STR,
                'description': '去除制表符、空格、引号、反斜杠、nan等特殊字符'
            },
            {
                'rule_name': '日期时间清洗规则',
                'rule_type': 'datetime',
                'regex_pattern': REG_TIME_STR,
                'description': '清理日期时间字段中的非数字字符'
            }
        ]

        for rule_data in cleaning_rules:
            rule = ImportCleaningRule(
                template_id=template.id,
                **rule_data
            )
            db.add(rule)

        logger.info(f"已导入 {len(cleaning_rules)} 条清洗规则")

        # 提交事务
        db.commit()

        logger.info("✅ 默认模板初始化完成！")
        logger.info(f"   - 模板名称: {template.template_name}")
        logger.info(f"   - 模板ID: {template.id}")
        logger.info(f"   - 字段映射: {mapping_count} 条")
        logger.info(f"   - 清洗规则: {len(cleaning_rules)} 条")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ 初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("初始化默认导入规则模板")
    logger.info("=" * 60)

    try:
        init_default_template()
    except Exception as e:
        logger.error(f"执行失败: {e}")
        sys.exit(1)
