from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from backend.services.bank_card_match_service import BankCardMatchService
from backend.services.auth_service import get_current_user
from backend.models.user import User
from backend.schemas.common import success_response

router = APIRouter()


class BatchMatchRequest(BaseModel):
    card_numbers: List[str]


@router.post("/bank-cards/batch-match")
async def batch_match_banks(
    request: BatchMatchRequest,
    current_user: User = Depends(get_current_user)
):
    """批量匹配银行卡归属"""
    try:
        result = BankCardMatchService.batch_match(request.card_numbers)
        return success_response(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匹配失败: {str(e)}")


@router.post("/bank-cards/batch-match/export")
async def export_match_result(
    request: BatchMatchRequest,
    current_user: User = Depends(get_current_user)
):
    """导出匹配结果为Excel"""
    try:
        result = BankCardMatchService.batch_match(request.card_numbers)
        output = BankCardMatchService.export_to_excel(result)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=bank_card_match_result.xlsx"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
