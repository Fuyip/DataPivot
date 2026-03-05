from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy.orm import Session
from backend.schemas.case_card import (
    CaseCardCreate, CaseCardUpdate, CaseCardResponse, CaseCardListResponse
)
from backend.schemas.common import success_response
from backend.services.case_card_service import CaseCardService
from backend.services.auth_service import get_current_user
from backend.models.user import User
from backend.models.case import Case
from database import get_system_db

router = APIRouter()


def check_case_permission(case_id: int, user: User, db: Session, required_permission: str = "read"):
    """检查案件权限"""
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="案件不存在")

    # 超级管理员有所有权限
    if user.role == "super_admin":
        return case

    # 检查用户权限
    from backend.services.case_service import check_case_permission as check_perm
    has_permission = check_perm(db, user.id, case_id, required_permission)

    if not has_permission:
        raise HTTPException(status_code=403, detail="权限不足")

    return case


@router.get("/{case_id}/case-cards")
async def get_case_cards(
    case_id: int,
    page: int = 1,
    page_size: int = 20,
    card_no: Optional[str] = None,
    bank_name: Optional[str] = None,
    card_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """获取案件银行卡列表"""
    case = check_case_permission(case_id, current_user, db, "read")

    try:
        result = CaseCardService.get_case_cards(
            case.database_name, page, page_size, card_no, bank_name, card_type
        )
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/{case_id}/case-cards/{card_id}")
async def get_case_card(
    case_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """获取单个案件银行卡"""
    case = check_case_permission(case_id, current_user, db, "read")

    card = CaseCardService.get_case_card(case.database_name, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="银行卡不存在")

    return success_response(data=card)


@router.post("/{case_id}/case-cards")
async def create_case_card(
    case_id: int,
    card_data: CaseCardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """创建案件银行卡"""
    case = check_case_permission(case_id, current_user, db, "write")

    try:
        card = CaseCardService.create_case_card(case.database_name, case.case_code, card_data)
        return success_response(data=card, message="创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/{case_id}/case-cards/{card_id}")
async def update_case_card(
    case_id: int,
    card_id: int,
    card_data: CaseCardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """更新案件银行卡"""
    case = check_case_permission(case_id, current_user, db, "write")

    try:
        card = CaseCardService.update_case_card(case.database_name, card_id, card_data)
        if not card:
            raise HTTPException(status_code=404, detail="银行卡不存在")
        return success_response(data=card, message="更新成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{case_id}/case-cards/{card_id}")
async def delete_case_card(
    case_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """删除案件银行卡"""
    case = check_case_permission(case_id, current_user, db, "write")

    try:
        success = CaseCardService.delete_case_card(case.database_name, card_id)
        if not success:
            raise HTTPException(status_code=404, detail="银行卡不存在")
        return success_response(message="删除成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/{case_id}/case-cards/export/excel")
async def export_case_cards(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """导出案件银行卡为Excel"""
    case = check_case_permission(case_id, current_user, db, "read")

    try:
        output = CaseCardService.export_case_cards(case.database_name)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=case_cards_{case.case_code}.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/{case_id}/case-cards/template/download")
async def download_template(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """下载导入模板"""
    check_case_permission(case_id, current_user, db, "read")

    try:
        output = CaseCardService.get_template()

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=case_card_template.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载模板失败: {str(e)}")


@router.post("/{case_id}/case-cards/import")
async def import_case_cards(
    case_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_system_db)
):
    """从模板导入案件银行卡"""
    case = check_case_permission(case_id, current_user, db, "write")

    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")

    try:
        content = await file.read()
        result = CaseCardService.import_from_template(case.database_name, case.case_code, content)

        return success_response(
            data={
                "success_count": result['success_count'],
                "error_count": result['error_count'],
                "errors": result['errors']
            },
            message="导入完成"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
