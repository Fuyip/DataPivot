"""
导入规则管理Schema定义
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ============ 规则模板 Schema ============

class ImportRuleTemplateBase(BaseModel):
    """规则模板基础Schema"""
    template_name: str = Field(..., min_length=1, max_length=200, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    is_active: bool = Field(True, description="是否启用")


class ImportRuleTemplateCreate(ImportRuleTemplateBase):
    """创建规则模板Schema"""
    pass


class ImportRuleTemplateUpdate(BaseModel):
    """更新规则模板Schema"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=200, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ImportRuleTemplate(ImportRuleTemplateBase):
    """规则模板响应Schema"""
    id: int
    is_default: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportRuleTemplateDetail(ImportRuleTemplate):
    """规则模板详情Schema（包含统计信息）"""
    field_mapping_count: int = Field(0, description="字段映射数量")
    cleaning_rule_count: int = Field(0, description="清洗规则数量")
    usage_count: int = Field(0, description="使用次数")


# ============ 字段映射 Schema ============

class FieldMappingBase(BaseModel):
    """字段映射基础Schema"""
    data_type: str = Field(..., max_length=50, description="数据类型")
    db_field_name: str = Field(..., max_length=100, description="数据库字段名")
    csv_column_name: str = Field(..., max_length=200, description="CSV列名")
    field_type: str = Field(..., max_length=50, description="字段类型")
    sort_order: int = Field(0, description="排序顺序")
    is_required: bool = Field(False, description="是否必填")
    default_value: Optional[str] = Field(None, max_length=200, description="默认值")

    @field_validator('field_type')
    @classmethod
    def validate_field_type(cls, v):
        allowed_types = ['str', 'float', 'datetime', 'card_no', 'tag', 'none', 'source']
        if v not in allowed_types:
            raise ValueError(f'字段类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class FieldMappingCreate(FieldMappingBase):
    """创建字段映射Schema"""
    pass


class FieldMappingUpdate(BaseModel):
    """更新字段映射Schema"""
    csv_column_name: Optional[str] = Field(None, max_length=200, description="CSV列名")
    field_type: Optional[str] = Field(None, max_length=50, description="字段类型")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    is_required: Optional[bool] = Field(None, description="是否必填")
    default_value: Optional[str] = Field(None, max_length=200, description="默认值")


class FieldMapping(FieldMappingBase):
    """字段映射响应Schema"""
    id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FieldMappingBatchCreate(BaseModel):
    """批量创建字段映射Schema"""
    data_type: str = Field(..., description="数据类型")
    mappings: List[FieldMappingCreate] = Field(..., description="字段映射列表")


# ============ 清洗规则 Schema ============

class CleaningRuleBase(BaseModel):
    """清洗规则基础Schema"""
    rule_name: str = Field(..., max_length=100, description="规则名称")
    rule_type: str = Field(..., max_length=50, description="规则类型")
    regex_pattern: str = Field(..., max_length=500, description="正则表达式")
    description: Optional[str] = Field(None, description="规则说明")

    @field_validator('rule_type')
    @classmethod
    def validate_rule_type(cls, v):
        allowed_types = ['general', 'datetime']
        if v not in allowed_types:
            raise ValueError(f'规则类型必须是以下之一: {", ".join(allowed_types)}')
        return v


class CleaningRuleCreate(CleaningRuleBase):
    """创建清洗规则Schema"""
    pass


class CleaningRuleUpdate(BaseModel):
    """更新清洗规则Schema"""
    rule_name: Optional[str] = Field(None, max_length=100, description="规则名称")
    rule_type: Optional[str] = Field(None, max_length=50, description="规则类型")
    regex_pattern: Optional[str] = Field(None, max_length=500, description="正则表达式")
    description: Optional[str] = Field(None, description="规则说明")


class CleaningRule(CleaningRuleBase):
    """清洗规则响应Schema"""
    id: int
    template_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 使用记录 Schema ============

class ImportRuleUsageLog(BaseModel):
    """规则使用记录Schema"""
    id: int
    template_id: int
    case_id: int
    task_id: str
    used_by: int
    used_at: datetime

    class Config:
        from_attributes = True


# ============ 辅助 Schema ============

class DataTypeInfo(BaseModel):
    """数据类型信息Schema"""
    name: str = Field(..., description="数据类型名称")
    description: str = Field(..., description="数据类型描述")


class FieldTypeInfo(BaseModel):
    """字段类型信息Schema"""
    value: str = Field(..., description="字段类型值")
    label: str = Field(..., description="字段类型标签")
    description: str = Field(..., description="字段类型描述")


class TemplateValidationResult(BaseModel):
    """模板验证结果Schema"""
    valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
