"""
导入规则管理数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class ImportRuleTemplate(Base):
    """导入规则模板表"""
    __tablename__ = "import_rule_templates"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    template_name = Column(String(200), unique=True, nullable=False, index=True, comment="模板名称")
    description = Column(Text, comment="模板描述")
    is_default = Column(Boolean, default=False, index=True, comment="是否默认模板")
    is_active = Column(Boolean, default=True, index=True, comment="是否启用")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    field_mappings = relationship("ImportFieldMapping", back_populates="template", cascade="all, delete-orphan")
    cleaning_rules = relationship("ImportCleaningRule", back_populates="template", cascade="all, delete-orphan")
    usage_logs = relationship("ImportRuleUsageLog", back_populates="template")
    creator = relationship("User", foreign_keys=[created_by])


class ImportFieldMapping(Base):
    """字段映射规则表"""
    __tablename__ = "import_field_mappings"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    template_id = Column(Integer, ForeignKey("import_rule_templates.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属模板ID")
    data_type = Column(String(50), nullable=False, index=True, comment="数据类型")
    db_field_name = Column(String(100), nullable=False, comment="数据库字段名")
    csv_column_name = Column(String(200), nullable=False, comment="CSV列名")
    field_type = Column(String(50), nullable=False, comment="字段类型")
    sort_order = Column(Integer, default=0, index=True, comment="排序顺序")
    is_required = Column(Boolean, default=False, comment="是否必填")
    default_value = Column(String(200), comment="默认值")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    template = relationship("ImportRuleTemplate", back_populates="field_mappings")


class ImportCleaningRule(Base):
    """数据清洗规则表"""
    __tablename__ = "import_cleaning_rules"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    template_id = Column(Integer, ForeignKey("import_rule_templates.id", ondelete="CASCADE"), nullable=False, index=True, comment="所属模板ID")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    rule_type = Column(String(50), nullable=False, index=True, comment="规则类型")
    regex_pattern = Column(String(500), nullable=False, comment="正则表达式")
    description = Column(Text, comment="规则说明")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    template = relationship("ImportRuleTemplate", back_populates="cleaning_rules")


class ImportRuleUsageLog(Base):
    """规则使用记录表"""
    __tablename__ = "import_rule_usage_logs"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    template_id = Column(Integer, ForeignKey("import_rule_templates.id", ondelete="RESTRICT"), nullable=False, index=True, comment="使用的模板ID")
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True, comment="案件ID")
    task_id = Column(String(100), nullable=False, index=True, comment="任务ID")
    used_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True, comment="使用人ID")
    used_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="使用时间")

    # 关系
    template = relationship("ImportRuleTemplate", back_populates="usage_logs")
    case = relationship("Case", foreign_keys=[case_id])
    user = relationship("User", foreign_keys=[used_by])
