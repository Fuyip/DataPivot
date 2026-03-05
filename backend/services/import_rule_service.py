"""
导入规则管理服务层
"""
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from backend.models.import_rule import (
    ImportRuleTemplate, ImportFieldMapping,
    ImportCleaningRule, ImportRuleUsageLog
)
from backend.schemas.import_rule import (
    ImportRuleTemplateCreate, ImportRuleTemplateUpdate,
    FieldMappingCreate, CleaningRuleCreate
)


def get_default_template(db: Session) -> Optional[ImportRuleTemplate]:
    """获取默认模板"""
    return db.query(ImportRuleTemplate).filter(
        ImportRuleTemplate.is_default == True,
        ImportRuleTemplate.is_active == True
    ).first()


def get_active_template(db: Session, template_id: Optional[int] = None) -> Optional[ImportRuleTemplate]:
    """
    获取启用的模板
    如果指定template_id则返回该模板，否则返回默认模板
    """
    if template_id:
        return db.query(ImportRuleTemplate).filter(
            ImportRuleTemplate.id == template_id,
            ImportRuleTemplate.is_active == True
        ).first()
    return get_default_template(db)


def load_template_config(db: Session, template_id: int) -> Dict:
    """
    加载模板配置并转换为NAME_DICT格式

    Returns:
        {
            'NAME_DICT': {...},
            'REG_STR': '...',
            'REG_TIME_STR': '...'
        }
    """
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        raise ValueError(f"模板不存在: {template_id}")

    if not template.is_active:
        raise ValueError(f"模板未启用: {template.template_name}")

    # 加载字段映射
    mappings = db.query(ImportFieldMapping).filter_by(
        template_id=template_id
    ).order_by(ImportFieldMapping.sort_order).all()

    # 按数据类型分组
    name_dict = {}
    for mapping in mappings:
        if mapping.data_type not in name_dict:
            name_dict[mapping.data_type] = {}

        name_dict[mapping.data_type][mapping.db_field_name] = [
            mapping.csv_column_name,
            mapping.field_type
        ]

    # 加载清洗规则
    cleaning_rules = db.query(ImportCleaningRule).filter_by(template_id=template_id).all()
    reg_str = next((r.regex_pattern for r in cleaning_rules if r.rule_type == 'general'), r'\t| |"|\\\\|(nan)|\\|,')
    reg_time_str = next((r.regex_pattern for r in cleaning_rules if r.rule_type == 'datetime'), r'\D|\b0\b')

    logger.info(f"已加载模板配置: {template.template_name} (ID: {template_id})")

    return {
        'NAME_DICT': name_dict,
        'REG_STR': reg_str,
        'REG_TIME_STR': reg_time_str
    }


def validate_template(db: Session, template_id: int) -> Dict:
    """
    验证模板配置的完整性

    Returns:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    errors = []
    warnings = []

    # 检查模板是否存在
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        errors.append("模板不存在")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # 检查必需的数据类型
    required_data_types = ['人员信息', '账户信息', '交易明细']
    mappings = db.query(ImportFieldMapping).filter_by(template_id=template_id).all()
    data_types = set(m.data_type for m in mappings)

    for dt in required_data_types:
        if dt not in data_types:
            errors.append(f"缺少必需的数据类型: {dt}")

    # 检查交易明细的必需字段
    if '交易明细' in data_types:
        trade_fields = [m.db_field_name for m in mappings if m.data_type == '交易明细']
        required_fields = ['card_no', 'trade_date', 'trade_money', 'dict_trade_tag']
        for field in required_fields:
            if field not in trade_fields:
                errors.append(f"交易明细缺少必需字段: {field}")

    # 检查清洗规则
    cleaning_rules = db.query(ImportCleaningRule).filter_by(template_id=template_id).all()
    if not any(r.rule_type == 'general' for r in cleaning_rules):
        warnings.append("未配置通用清洗规则")
    if not any(r.rule_type == 'datetime' for r in cleaning_rules):
        warnings.append("未配置日期时间清洗规则")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def set_default_template(db: Session, template_id: int) -> ImportRuleTemplate:
    """设置默认模板"""
    # 取消其他模板的默认状态
    db.query(ImportRuleTemplate).filter(
        ImportRuleTemplate.is_default == True
    ).update({'is_default': False})

    # 设置新的默认模板
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        raise ValueError(f"模板不存在: {template_id}")

    template.is_default = True
    template.is_active = True  # 默认模板必须启用
    db.commit()
    db.refresh(template)

    logger.info(f"已设置默认模板: {template.template_name} (ID: {template_id})")
    return template


def duplicate_template(db: Session, template_id: int, new_name: str, user_id: int) -> ImportRuleTemplate:
    """复制模板"""
    # 查询原模板
    original = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not original:
        raise ValueError(f"模板不存在: {template_id}")

    # 创建新模板
    new_template = ImportRuleTemplate(
        template_name=new_name,
        description=f"复制自: {original.template_name}",
        is_default=False,
        is_active=True,
        created_by=user_id
    )
    db.add(new_template)
    db.flush()

    # 复制字段映射
    mappings = db.query(ImportFieldMapping).filter_by(template_id=template_id).all()
    for mapping in mappings:
        new_mapping = ImportFieldMapping(
            template_id=new_template.id,
            data_type=mapping.data_type,
            db_field_name=mapping.db_field_name,
            csv_column_name=mapping.csv_column_name,
            field_type=mapping.field_type,
            sort_order=mapping.sort_order,
            is_required=mapping.is_required,
            default_value=mapping.default_value
        )
        db.add(new_mapping)

    # 复制清洗规则
    cleaning_rules = db.query(ImportCleaningRule).filter_by(template_id=template_id).all()
    for rule in cleaning_rules:
        new_rule = ImportCleaningRule(
            template_id=new_template.id,
            rule_name=rule.rule_name,
            rule_type=rule.rule_type,
            regex_pattern=rule.regex_pattern,
            description=rule.description
        )
        db.add(new_rule)

    db.commit()
    db.refresh(new_template)

    logger.info(f"已复制模板: {original.template_name} -> {new_name} (ID: {new_template.id})")
    return new_template


def log_template_usage(db: Session, template_id: int, case_id: int, task_id: str, user_id: int):
    """记录模板使用日志"""
    log = ImportRuleUsageLog(
        template_id=template_id,
        case_id=case_id,
        task_id=task_id,
        used_by=user_id
    )
    db.add(log)
    db.commit()
    logger.debug(f"记录模板使用: template_id={template_id}, task_id={task_id}")


def get_template_statistics(db: Session, template_id: int) -> Dict:
    """获取模板统计信息"""
    field_mapping_count = db.query(func.count(ImportFieldMapping.id)).filter(
        ImportFieldMapping.template_id == template_id
    ).scalar()

    cleaning_rule_count = db.query(func.count(ImportCleaningRule.id)).filter(
        ImportCleaningRule.template_id == template_id
    ).scalar()

    usage_count = db.query(func.count(ImportRuleUsageLog.id)).filter(
        ImportRuleUsageLog.template_id == template_id
    ).scalar()

    return {
        'field_mapping_count': field_mapping_count,
        'cleaning_rule_count': cleaning_rule_count,
        'usage_count': usage_count
    }


def get_supported_data_types() -> List[Dict]:
    """获取支持的数据类型列表"""
    return [
        {'name': '人员信息', 'description': '银行账户持有人的个人信息'},
        {'name': '账户信息', 'description': '银行账户的基本信息'},
        {'name': '子账户信息', 'description': '银行子账户信息'},
        {'name': '强制措施信息', 'description': '账户冻结等强制措施信息'},
        {'name': '交易明细', 'description': '银行流水交易明细'},
        {'name': '失败信息', 'description': '查询失败的任务信息'}
    ]


def get_supported_field_types() -> List[Dict]:
    """获取支持的字段类型列表"""
    return [
        {'value': 'str', 'label': '字符串', 'description': '保持原样的文本字段'},
        {'value': 'float', 'label': '浮点数', 'description': '数值字段，空值转为NULL'},
        {'value': 'datetime', 'label': '日期时间', 'description': '日期时间字段，清理非数字字符'},
        {'value': 'card_no', 'label': '卡号', 'description': '银行卡号，提取第一个数字串'},
        {'value': 'tag', 'label': '收付标志', 'description': '转换为in/out标识'},
        {'value': 'none', 'label': '不处理', 'description': '跳过该字段'},
        {'value': 'source', 'label': '来源标记', 'description': '特殊标记字段'}
    ]


def get_database_fields_by_type() -> Dict[str, List[Dict]]:
    """获取每个数据类型对应的数据库字段列表"""
    return {
        '人员信息': [
            {'field': 'name', 'label': '姓名', 'description': '账户持有人姓名'},
            {'field': 'id_card', 'label': '身份证号', 'description': '身份证号码'},
            {'field': 'phone', 'label': '手机号', 'description': '联系电话'},
            {'field': 'address', 'label': '地址', 'description': '联系地址'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ],
        '账户信息': [
            {'field': 'account_name', 'label': '账户名称', 'description': '银行账户名称'},
            {'field': 'account_no', 'label': '账号', 'description': '银行账号'},
            {'field': 'bank_name', 'label': '开户行', 'description': '开户银行名称'},
            {'field': 'account_type', 'label': '账户类型', 'description': '账户类型'},
            {'field': 'open_date', 'label': '开户日期', 'description': '账户开户日期'},
            {'field': 'status', 'label': '账户状态', 'description': '账户当前状态'},
            {'field': 'balance', 'label': '余额', 'description': '账户余额'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ],
        '子账户信息': [
            {'field': 'sub_account_no', 'label': '子账号', 'description': '子账户账号'},
            {'field': 'sub_account_name', 'label': '子账户名称', 'description': '子账户名称'},
            {'field': 'parent_account', 'label': '主账号', 'description': '关联的主账号'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ],
        '强制措施信息': [
            {'field': 'measure_type', 'label': '措施类型', 'description': '强制措施类型'},
            {'field': 'measure_date', 'label': '措施日期', 'description': '执行日期'},
            {'field': 'measure_amount', 'label': '冻结金额', 'description': '冻结金额'},
            {'field': 'measure_reason', 'label': '措施原因', 'description': '执行原因'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ],
        '交易明细': [
            {'field': 'card_no', 'label': '交易卡号', 'description': '交易银行卡号'},
            {'field': 'card_account', 'label': '交易账号', 'description': '交易账号'},
            {'field': 'account_name', 'label': '交易户名', 'description': '交易户名'},
            {'field': 'trade_date', 'label': '交易日期', 'description': '交易发生日期'},
            {'field': 'trade_time', 'label': '交易时间', 'description': '交易时间'},
            {'field': 'trade_money', 'label': '交易金额', 'description': '交易金额'},
            {'field': 'balance', 'label': '余额', 'description': '交易后余额'},
            {'field': 'dict_trade_tag', 'label': '收付标志', 'description': '收入/支出标识'},
            {'field': 'opposite_name', 'label': '对方户名', 'description': '交易对方户名'},
            {'field': 'opposite_card_no', 'label': '对方卡号', 'description': '交易对方卡号'},
            {'field': 'opposite_account', 'label': '对方账号', 'description': '交易对方账号'},
            {'field': 'opposite_bank', 'label': '对方开户行', 'description': '对方开户银行'},
            {'field': 'trade_type', 'label': '交易类型', 'description': '交易类型'},
            {'field': 'trade_channel', 'label': '交易渠道', 'description': '交易渠道'},
            {'field': 'trade_location', 'label': '交易地点', 'description': '交易地点'},
            {'field': 'remark', 'label': '备注', 'description': '交易备注'},
            {'field': 'result', 'label': '查询结果', 'description': '查询反馈结果'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ],
        '失败信息': [
            {'field': 'error_message', 'label': '错误信息', 'description': '失败原因'},
            {'field': 'error_code', 'label': '错误代码', 'description': '错误代码'},
            {'field': 'source', 'label': '来源标记', 'description': '数据来源标识'},
        ]
    }

