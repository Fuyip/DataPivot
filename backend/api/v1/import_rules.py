"""
导入规则管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from database import get_system_db
from backend.models.import_rule import (
    ImportRuleTemplate, ImportFieldMapping,
    ImportCleaningRule, ImportRuleUsageLog
)
from backend.schemas.import_rule import (
    ImportRuleTemplate as ImportRuleTemplateSchema,
    ImportRuleTemplateCreate, ImportRuleTemplateUpdate, ImportRuleTemplateDetail,
    FieldMapping as FieldMappingSchema,
    FieldMappingCreate, FieldMappingUpdate, FieldMappingBatchCreate,
    CleaningRule as CleaningRuleSchema,
    CleaningRuleCreate, CleaningRuleUpdate,
    DataTypeInfo, FieldTypeInfo, TemplateValidationResult
)
from backend.schemas.common import success_response, error_response
from backend.schemas.user import User as UserSchema
from backend.services.auth_service import get_current_active_user
from backend.services.import_rule_service import (
    get_default_template, set_default_template, duplicate_template,
    validate_template, get_template_statistics,
    get_supported_data_types, get_supported_field_types, get_database_fields_by_type
)

router = APIRouter(tags=["导入规则管理"])


# ============ 模板管理接口 ============

@router.get("/templates", summary="获取模板列表")
def get_template_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """获取模板列表（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可访问")

    # 构建查询
    query = db.query(ImportRuleTemplate)

    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                ImportRuleTemplate.template_name.like(f"%{search}%"),
                ImportRuleTemplate.description.like(f"%{search}%")
            )
        )

    # 状态过滤
    if is_active is not None:
        query = query.filter(ImportRuleTemplate.is_active == is_active)

    # 总数
    total = query.count()

    # 分页
    templates = query.order_by(
        desc(ImportRuleTemplate.is_default),
        desc(ImportRuleTemplate.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()

    # 转换为响应格式
    items = []
    for template in templates:
        stats = get_template_statistics(db, template.id)
        items.append({
            **ImportRuleTemplateSchema.model_validate(template).model_dump(),
            **stats
        })

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/templates/{template_id}", summary="获取模板详情")
def get_template_detail(
    template_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """获取模板详情（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可访问")

    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    stats = get_template_statistics(db, template_id)

    return success_response(
        data={
            **ImportRuleTemplateSchema.model_validate(template).model_dump(),
            **stats
        }
    )


@router.post("/templates", summary="创建模板")
def create_template(
    template_data: ImportRuleTemplateCreate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """创建模板（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    # 检查名称是否重复
    existing = db.query(ImportRuleTemplate).filter_by(
        template_name=template_data.template_name
    ).first()
    if existing:
        return error_response(400, "模板名称已存在")

    # 创建模板
    template = ImportRuleTemplate(
        **template_data.model_dump(),
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)

    return success_response(
        data=ImportRuleTemplateSchema.model_validate(template).model_dump(),
        message="模板创建成功"
    )


@router.put("/templates/{template_id}", summary="更新模板")
def update_template(
    template_id: int,
    template_data: ImportRuleTemplateUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """更新模板（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    # 更新字段
    update_data = template_data.model_dump(exclude_unset=True)

    # 检查名称是否重复
    if 'template_name' in update_data:
        existing = db.query(ImportRuleTemplate).filter(
            ImportRuleTemplate.template_name == update_data['template_name'],
            ImportRuleTemplate.id != template_id
        ).first()
        if existing:
            return error_response(400, "模板名称已存在")

    for key, value in update_data.items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)

    return success_response(
        data=ImportRuleTemplateSchema.model_validate(template).model_dump(),
        message="模板更新成功"
    )


@router.delete("/templates/{template_id}", summary="删除模板")
def delete_template(
    template_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """删除模板（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    # 不能删除默认模板
    if template.is_default:
        return error_response(400, "不能删除默认模板，请先设置其他模板为默认")

    # 检查是否有使用记录
    usage_count = db.query(ImportRuleUsageLog).filter_by(template_id=template_id).count()
    if usage_count > 0:
        return error_response(400, f"该模板已被使用{usage_count}次，不能删除")

    db.delete(template)
    db.commit()

    return success_response(message="模板删除成功")


@router.post("/templates/{template_id}/set-default", summary="设为默认模板")
def set_as_default_template(
    template_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """设为默认模板（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    try:
        template = set_default_template(db, template_id)
        return success_response(
            data=ImportRuleTemplateSchema.model_validate(template).model_dump(),
            message="已设为默认模板"
        )
    except ValueError as e:
        return error_response(400, str(e))


@router.post("/templates/{template_id}/duplicate", summary="复制模板")
def duplicate_template_endpoint(
    template_id: int,
    new_name: str = Query(..., description="新模板名称"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """复制模板（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    # 检查名称是否重复
    existing = db.query(ImportRuleTemplate).filter_by(template_name=new_name).first()
    if existing:
        return error_response(400, "模板名称已存在")

    try:
        new_template = duplicate_template(db, template_id, new_name, current_user.id)
        return success_response(
            data=ImportRuleTemplateSchema.model_validate(new_template).model_dump(),
            message="模板复制成功"
        )
    except ValueError as e:
        return error_response(400, str(e))


@router.post("/templates/{template_id}/validate", summary="验证模板")
def validate_template_endpoint(
    template_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """验证模板配置完整性（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可访问")

    result = validate_template(db, template_id)
    return success_response(data=result)


# ============ 字段映射管理接口 ============

@router.get("/templates/{template_id}/mappings", summary="获取字段映射列表")
def get_field_mappings(
    template_id: int,
    data_type: Optional[str] = Query(None, description="数据类型筛选"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """获取字段映射列表（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可访问")

    # 检查模板是否存在
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    # 构建查询
    query = db.query(ImportFieldMapping).filter_by(template_id=template_id)

    # 数据类型筛选
    if data_type:
        query = query.filter(ImportFieldMapping.data_type == data_type)

    # 按排序顺序和数据类型排序
    mappings = query.order_by(
        ImportFieldMapping.data_type,
        ImportFieldMapping.sort_order
    ).all()

    # 按数据类型分组
    grouped_data = {}
    for mapping in mappings:
        if mapping.data_type not in grouped_data:
            grouped_data[mapping.data_type] = []
        grouped_data[mapping.data_type].append(
            FieldMappingSchema.model_validate(mapping).model_dump()
        )

    return success_response(data=grouped_data)


@router.post("/templates/{template_id}/mappings", summary="批量创建/更新字段映射")
def batch_save_field_mappings(
    template_id: int,
    batch_data: FieldMappingBatchCreate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """批量创建/更新字段映射（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    # 检查模板是否存在
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    # 删除该数据类型的现有映射
    db.query(ImportFieldMapping).filter(
        ImportFieldMapping.template_id == template_id,
        ImportFieldMapping.data_type == batch_data.data_type
    ).delete()

    # 批量创建新映射
    for mapping_data in batch_data.mappings:
        mapping = ImportFieldMapping(
            template_id=template_id,
            **mapping_data.model_dump()
        )
        db.add(mapping)

    db.commit()

    return success_response(message=f"已保存{len(batch_data.mappings)}条字段映射")


@router.put("/mappings/{mapping_id}", summary="更新单个字段映射")
def update_field_mapping(
    mapping_id: int,
    mapping_data: FieldMappingUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """更新单个字段映射（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    mapping = db.query(ImportFieldMapping).filter_by(id=mapping_id).first()
    if not mapping:
        return error_response(404, "字段映射不存在")

    # 更新字段
    update_data = mapping_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mapping, key, value)

    db.commit()
    db.refresh(mapping)

    return success_response(
        data=FieldMappingSchema.model_validate(mapping).model_dump(),
        message="字段映射更新成功"
    )


@router.delete("/mappings/{mapping_id}", summary="删除字段映射")
def delete_field_mapping(
    mapping_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """删除字段映射（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    mapping = db.query(ImportFieldMapping).filter_by(id=mapping_id).first()
    if not mapping:
        return error_response(404, "字段映射不存在")

    db.delete(mapping)
    db.commit()

    return success_response(message="字段映射删除成功")


# ============ 清洗规则管理接口 ============

@router.get("/templates/{template_id}/cleaning-rules", summary="获取清洗规则列表")
def get_cleaning_rules(
    template_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """获取清洗规则列表（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可访问")

    # 检查模板是否存在
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    rules = db.query(ImportCleaningRule).filter_by(template_id=template_id).all()

    return success_response(
        data=[CleaningRuleSchema.model_validate(rule).model_dump() for rule in rules]
    )


@router.post("/templates/{template_id}/cleaning-rules", summary="创建清洗规则")
def create_cleaning_rule(
    template_id: int,
    rule_data: CleaningRuleCreate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """创建清洗规则（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    # 检查模板是否存在
    template = db.query(ImportRuleTemplate).filter_by(id=template_id).first()
    if not template:
        return error_response(404, "模板不存在")

    rule = ImportCleaningRule(
        template_id=template_id,
        **rule_data.model_dump()
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    return success_response(
        data=CleaningRuleSchema.model_validate(rule).model_dump(),
        message="清洗规则创建成功"
    )


@router.put("/cleaning-rules/{rule_id}", summary="更新清洗规则")
def update_cleaning_rule(
    rule_id: int,
    rule_data: CleaningRuleUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """更新清洗规则（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    rule = db.query(ImportCleaningRule).filter_by(id=rule_id).first()
    if not rule:
        return error_response(404, "清洗规则不存在")

    # 更新字段
    update_data = rule_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)

    return success_response(
        data=CleaningRuleSchema.model_validate(rule).model_dump(),
        message="清洗规则更新成功"
    )


@router.delete("/cleaning-rules/{rule_id}", summary="删除清洗规则")
def delete_cleaning_rule(
    rule_id: int,
    current_user: UserSchema = Depends(get_current_active_user),
    db: Session = Depends(get_system_db)
):
    """删除清洗规则（仅管理员）"""
    if current_user.role not in ["super_admin", "admin"]:
        return error_response(403, "权限不足，仅管理员可操作")

    rule = db.query(ImportCleaningRule).filter_by(id=rule_id).first()
    if not rule:
        return error_response(404, "清洗规则不存在")

    db.delete(rule)
    db.commit()

    return success_response(message="清洗规则删除成功")


# ============ 辅助接口 ============

@router.get("/data-types", summary="获取支持的数据类型")
def get_data_types(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """获取支持的数据类型列表"""
    return success_response(data=get_supported_data_types())


@router.get("/field-types", summary="获取支持的字段类型")
def get_field_types(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """获取支持的字段类型列表"""
    return success_response(data=get_supported_field_types())


@router.get("/database-fields", summary="获取数据库字段定义")
def get_database_fields(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """获取每个数据类型对应的数据库字段列表"""
    return success_response(data=get_database_fields_by_type())
