from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import get_system_db
from backend.services.auth_service import get_current_user, require_admin, require_super_admin
from backend.models.user import User
from backend.services.bank_info_service import BankInfoService
from backend.schemas.bank_info import (
    BankBinCreate, BankBinUpdate, BankBinQueryParams,
    SyBankCreate, SyBankUpdate, SyBankQueryParams,
    ChangeRequestQueryParams, ChangeRequestReview,
    BankBinOperationRequest, SyBankOperationRequest
)
from backend.schemas.common import success_response

router = APIRouter()


# ==================== BankBin 相关接口 ====================

@router.get("/bank-bin")
async def get_bank_bin_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    bin: Optional[str] = None,
    bank_name: Optional[str] = None,
    bin_len: Optional[int] = None,
    card_len: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """获取 BankBin 列表"""
    try:
        items, total = BankInfoService.get_bank_bin_list(
            db, page, page_size, bin, bank_name, bin_len, card_len
        )
        return success_response(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bank-bin")
async def create_bank_bin(
    request: BankBinOperationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """创建 BankBin"""
    try:
        # 检查是否是超级管理员
        is_super_admin = current_user.role == "super_admin"
        direct_execute = request.direct_execute and is_super_admin

        result = BankInfoService.create_bank_bin(
            db, request.data, current_user.id, request.reason, direct_execute
        )
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/bank-bin/{bin_code}")
async def update_bank_bin(
    bin_code: str,
    request: BankBinOperationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """更新 BankBin"""
    try:
        is_super_admin = current_user.role == "super_admin"
        direct_execute = request.direct_execute and is_super_admin

        result = BankInfoService.update_bank_bin(
            db, bin_code, request.data, current_user.id, request.reason, direct_execute
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/bank-bin/{bin_code}")
async def delete_bank_bin(
    bin_code: str,
    reason: Optional[str] = None,
    direct_execute: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """删除 BankBin"""
    try:
        is_super_admin = current_user.role == "super_admin"
        direct_exec = direct_execute and is_super_admin

        result = BankInfoService.delete_bank_bin(
            db, bin_code, current_user.id, reason, direct_exec
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bank-bin/export")
async def export_bank_bin(
    bin: Optional[str] = None,
    bank_name: Optional[str] = None,
    bin_len: Optional[int] = None,
    card_len: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """导出 BankBin 数据"""
    try:
        output = BankInfoService.export_bank_bin(
            db, bin=bin, bank_name=bank_name, bin_len=bin_len, card_len=card_len
        )
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=bank_bin.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bank-bin/template")
async def get_bank_bin_template(
    current_user: User = Depends(require_admin)
):
    """下载 BankBin 导入模板"""
    try:
        output = BankInfoService.get_bank_bin_template()
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=bank_bin_template.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SyBank 相关接口 ====================

@router.get("/sy-bank")
async def get_sy_bank_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    from_bank: Optional[str] = None,
    to_bank: Optional[str] = None,
    sys: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """获取 SyBank 列表"""
    try:
        items, total = BankInfoService.get_sy_bank_list(
            db, page, page_size, from_bank, to_bank, sys
        )
        return success_response(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sy-bank")
async def create_sy_bank(
    request: SyBankOperationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """创建 SyBank"""
    try:
        is_super_admin = current_user.role == "super_admin"
        direct_execute = request.direct_execute and is_super_admin

        result = BankInfoService.create_sy_bank(
            db, request.data, current_user.id, request.reason, direct_execute
        )
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/sy-bank/{from_bank}/{sys}")
async def update_sy_bank(
    from_bank: str,
    sys: str,
    request: SyBankOperationRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """更新 SyBank"""
    try:
        is_super_admin = current_user.role == "super_admin"
        direct_execute = request.direct_execute and is_super_admin

        result = BankInfoService.update_sy_bank(
            db, from_bank, sys, request.data, current_user.id, request.reason, direct_execute
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/sy-bank/{from_bank}/{sys}")
async def delete_sy_bank(
    from_bank: str,
    sys: str,
    reason: Optional[str] = None,
    direct_execute: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """删除 SyBank"""
    try:
        is_super_admin = current_user.role == "super_admin"
        direct_exec = direct_execute and is_super_admin

        result = BankInfoService.delete_sy_bank(
            db, from_bank, sys, current_user.id, reason, direct_exec
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sy-bank/export")
async def export_sy_bank(
    from_bank: Optional[str] = None,
    to_bank: Optional[str] = None,
    sys: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """导出 SyBank 数据"""
    try:
        output = BankInfoService.export_sy_bank(
            db, from_bank=from_bank, to_bank=to_bank, sys=sys
        )
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=sy_bank.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sy-bank/template")
async def get_sy_bank_template(
    current_user: User = Depends(require_admin)
):
    """下载 SyBank 导入模板"""
    try:
        output = BankInfoService.get_sy_bank_template()
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=sy_bank_template.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 变更申请相关接口 ====================

@router.get("/change-requests")
async def get_change_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    table_type: Optional[str] = None,
    change_type: Optional[str] = None,
    created_by: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """获取变更申请列表"""
    try:
        params = ChangeRequestQueryParams(
            page=page,
            page_size=page_size,
            status=status,
            table_type=table_type,
            change_type=change_type,
            created_by=created_by
        )
        items, total = BankInfoService.get_change_requests(db, params)

        return success_response(data={
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/change-requests/{request_id}/approve")
async def approve_change_request(
    request_id: int,
    review: ChangeRequestReview,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_system_db)
):
    """批准变更申请"""
    try:
        result = BankInfoService.approve_change_request(
            db, request_id, current_user.id, review.review_comment
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-requests/{request_id}/reject")
async def reject_change_request(
    request_id: int,
    review: ChangeRequestReview,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_system_db)
):
    """拒绝变更申请"""
    try:
        result = BankInfoService.reject_change_request(
            db, request_id, current_user.id, review.review_comment
        )
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/change-requests/{request_id}")
async def delete_change_request(
    request_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_system_db)
):
    """撤销变更申请"""
    try:
        result = BankInfoService.delete_change_request(db, request_id, current_user.id)
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
