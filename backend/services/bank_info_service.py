from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from datetime import datetime
import json
import pandas as pd
from io import BytesIO

from backend.models.bank_info_change import BankInfoChangeRequest
from backend.models.user import User
from backend.schemas.bank_info import (
    BankBinCreate, BankBinUpdate, BankBinResponse,
    SyBankCreate, SyBankUpdate, SyBankResponse,
    ChangeRequestResponse, ChangeRequestQueryParams
)


class BankInfoService:
    """银行信息管理服务"""

    # ==================== BankBin 相关方法 ====================

    @staticmethod
    def get_bank_bin_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        bin: Optional[str] = None,
        bank_name: Optional[str] = None,
        bin_len: Optional[int] = None,
        card_len: Optional[int] = None
    ) -> Tuple[List[Dict], int]:
        """获取 BankBin 列表"""
        # 构建查询条件
        conditions = []
        params = {}

        if bin:
            conditions.append("bin LIKE :bin")
            params["bin"] = f"%{bin}%"
        if bank_name:
            conditions.append("bank_name LIKE :bank_name")
            params["bank_name"] = f"%{bank_name}%"
        if bin_len is not None:
            conditions.append("bin_len = :bin_len")
            params["bin_len"] = bin_len
        if card_len is not None:
            conditions.append("card_len = :card_len")
            params["card_len"] = card_len

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM bank_bin WHERE {where_clause}"
        total = db.execute(text(count_sql), params).scalar()

        # 查询数据
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        data_sql = f"""
            SELECT bin, bin_len, card_len, bank_name
            FROM bank_bin
            WHERE {where_clause}
            ORDER BY bin
            LIMIT :limit OFFSET :offset
        """
        results = db.execute(text(data_sql), params).fetchall()

        items = [
            {
                "bin": row[0],
                "bin_len": row[1],
                "card_len": row[2],
                "bank_name": row[3]
            }
            for row in results
        ]

        return items, total

    @staticmethod
    def create_bank_bin(
        db: Session,
        data: BankBinCreate,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """创建 BankBin（提交申请或直接执行）"""
        new_data = data.model_dump()

        if direct_execute:
            # 直接执行
            insert_sql = text("""
                INSERT INTO bank_bin (bin, bin_len, card_len, bank_name)
                VALUES (:bin, :bin_len, :card_len, :bank_name)
            """)
            db.execute(insert_sql, new_data)

            # 创建已执行的变更记录
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="create",
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "创建成功", "direct": True}
        else:
            # 提交申请
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="create",
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    @staticmethod
    def update_bank_bin(
        db: Session,
        bin_code: str,
        data: BankBinUpdate,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """更新 BankBin"""
        # 获取原始数据
        old_sql = text("SELECT bin, bin_len, card_len, bank_name FROM bank_bin WHERE bin = :bin")
        old_row = db.execute(old_sql, {"bin": bin_code}).fetchone()

        if not old_row:
            raise ValueError("BIN码不存在")

        old_data = {
            "bin": old_row[0],
            "bin_len": old_row[1],
            "card_len": old_row[2],
            "bank_name": old_row[3]
        }
        new_data = data.model_dump()

        if direct_execute:
            # 直接执行
            update_sql = text("""
                UPDATE bank_bin
                SET bin = :bin, bin_len = :bin_len, card_len = :card_len, bank_name = :bank_name
                WHERE bin = :old_bin
            """)
            db.execute(update_sql, {**new_data, "old_bin": bin_code})

            # 创建已执行的变更记录
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="update",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "更新成功", "direct": True}
        else:
            # 提交申请
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="update",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    @staticmethod
    def delete_bank_bin(
        db: Session,
        bin_code: str,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """删除 BankBin"""
        # 获取原始数据
        old_sql = text("SELECT bin, bin_len, card_len, bank_name FROM bank_bin WHERE bin = :bin")
        old_row = db.execute(old_sql, {"bin": bin_code}).fetchone()

        if not old_row:
            raise ValueError("BIN码不存在")

        old_data = {
            "bin": old_row[0],
            "bin_len": old_row[1],
            "card_len": old_row[2],
            "bank_name": old_row[3]
        }

        if direct_execute:
            # 直接执行
            delete_sql = text("DELETE FROM bank_bin WHERE bin = :bin")
            db.execute(delete_sql, {"bin": bin_code})

            # 创建已执行的变更记录
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="delete",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps({"bin": bin_code}, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "删除成功", "direct": True}
        else:
            # 提交申请
            change_request = BankInfoChangeRequest(
                table_type="bank_bin",
                change_type="delete",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps({"bin": bin_code}, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    # ==================== SyBank 相关方法 ====================

    @staticmethod
    def get_sy_bank_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        from_bank: Optional[str] = None,
        to_bank: Optional[str] = None,
        sys: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """获取 SyBank 列表"""
        conditions = []
        params = {}

        if from_bank:
            conditions.append("from_bank LIKE :from_bank")
            params["from_bank"] = f"%{from_bank}%"
        if to_bank:
            conditions.append("to_bank LIKE :to_bank")
            params["to_bank"] = f"%{to_bank}%"
        if sys:
            conditions.append("sys = :sys")
            params["sys"] = sys

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM sy_bank WHERE {where_clause}"
        total = db.execute(text(count_sql), params).scalar()

        # 查询数据
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        data_sql = f"""
            SELECT from_bank, to_bank, sys
            FROM sy_bank
            WHERE {where_clause}
            ORDER BY from_bank
            LIMIT :limit OFFSET :offset
        """
        results = db.execute(text(data_sql), params).fetchall()

        items = [
            {
                "from_bank": row[0],
                "to_bank": row[1],
                "sys": row[2]
            }
            for row in results
        ]

        return items, total

    @staticmethod
    def create_sy_bank(
        db: Session,
        data: SyBankCreate,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """创建 SyBank"""
        new_data = data.model_dump()

        if direct_execute:
            insert_sql = text("""
                INSERT INTO sy_bank (from_bank, to_bank, sys)
                VALUES (:from_bank, :to_bank, :sys)
            """)
            db.execute(insert_sql, new_data)

            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="create",
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "创建成功", "direct": True}
        else:
            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="create",
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    @staticmethod
    def update_sy_bank(
        db: Session,
        from_bank: str,
        sys: str,
        data: SyBankUpdate,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """更新 SyBank"""
        old_sql = text("SELECT from_bank, to_bank, sys FROM sy_bank WHERE from_bank = :from_bank AND sys = :sys")
        old_row = db.execute(old_sql, {"from_bank": from_bank, "sys": sys}).fetchone()

        if not old_row:
            raise ValueError("银行映射不存在")

        old_data = {
            "from_bank": old_row[0],
            "to_bank": old_row[1],
            "sys": old_row[2]
        }
        new_data = data.model_dump()

        if direct_execute:
            update_sql = text("""
                UPDATE sy_bank
                SET from_bank = :from_bank, to_bank = :to_bank, sys = :sys
                WHERE from_bank = :old_from_bank AND sys = :old_sys
            """)
            db.execute(update_sql, {**new_data, "old_from_bank": from_bank, "old_sys": sys})

            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="update",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "更新成功", "direct": True}
        else:
            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="update",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps(new_data, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    @staticmethod
    def delete_sy_bank(
        db: Session,
        from_bank: str,
        sys: str,
        user_id: int,
        reason: Optional[str] = None,
        direct_execute: bool = False
    ) -> Dict:
        """删除 SyBank"""
        old_sql = text("SELECT from_bank, to_bank, sys FROM sy_bank WHERE from_bank = :from_bank AND sys = :sys")
        old_row = db.execute(old_sql, {"from_bank": from_bank, "sys": sys}).fetchone()

        if not old_row:
            raise ValueError("银行映射不存在")

        old_data = {
            "from_bank": old_row[0],
            "to_bank": old_row[1],
            "sys": old_row[2]
        }

        if direct_execute:
            delete_sql = text("DELETE FROM sy_bank WHERE from_bank = :from_bank AND sys = :sys")
            db.execute(delete_sql, {"from_bank": from_bank, "sys": sys})

            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="delete",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps({"from_bank": from_bank, "sys": sys}, ensure_ascii=False),
                reason=reason,
                status="executed",
                created_by=user_id,
                reviewed_by=user_id,
                reviewed_at=datetime.now(),
                executed_at=datetime.now()
            )
            db.add(change_request)
            db.commit()

            return {"message": "删除成功", "direct": True}
        else:
            change_request = BankInfoChangeRequest(
                table_type="sy_bank",
                change_type="delete",
                old_data=json.dumps(old_data, ensure_ascii=False),
                new_data=json.dumps({"from_bank": from_bank, "sys": sys}, ensure_ascii=False),
                reason=reason,
                status="pending",
                created_by=user_id
            )
            db.add(change_request)
            db.commit()

            return {"message": "申请已提交，等待审批", "request_id": change_request.id}

    # ==================== 变更申请管理 ====================

    @staticmethod
    def get_change_requests(
        db: Session,
        params: ChangeRequestQueryParams
    ) -> Tuple[List[ChangeRequestResponse], int]:
        """获取变更申请列表"""
        query = db.query(BankInfoChangeRequest)

        if params.status:
            query = query.filter(BankInfoChangeRequest.status == params.status)
        if params.table_type:
            query = query.filter(BankInfoChangeRequest.table_type == params.table_type)
        if params.change_type:
            query = query.filter(BankInfoChangeRequest.change_type == params.change_type)
        if params.created_by:
            query = query.filter(BankInfoChangeRequest.created_by == params.created_by)

        total = query.count()

        items = query.order_by(BankInfoChangeRequest.created_at.desc()) \
            .offset((params.page - 1) * params.page_size) \
            .limit(params.page_size) \
            .all()

        # 获取用户名
        creator_ids = [item.created_by for item in items]
        reviewer_ids = [item.reviewed_by for item in items if item.reviewed_by]
        user_ids = list(set(creator_ids + reviewer_ids))

        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {user.id: user.username for user in users}

        results = []
        for item in items:
            result = ChangeRequestResponse.model_validate(item)
            result.creator_name = user_map.get(item.created_by)
            result.reviewer_name = user_map.get(item.reviewed_by) if item.reviewed_by else None
            results.append(result)

        return results, total

    @staticmethod
    def approve_change_request(
        db: Session,
        request_id: int,
        reviewer_id: int,
        review_comment: Optional[str] = None
    ) -> Dict:
        """批准变���申请并执行"""
        request = db.query(BankInfoChangeRequest).filter(BankInfoChangeRequest.id == request_id).first()

        if not request:
            raise ValueError("变更申请不存在")

        if request.status != "pending":
            raise ValueError(f"变更申请状态为 {request.status}，无法审批")

        try:
            # 更新申请状态为 approved
            request.status = "approved"
            request.reviewed_by = reviewer_id
            request.reviewed_at = datetime.now()
            request.review_comment = review_comment

            # 执行变更
            new_data = json.loads(request.new_data)

            if request.table_type == "bank_bin":
                if request.change_type == "create":
                    sql = text("""
                        INSERT INTO bank_bin (bin, bin_len, card_len, bank_name)
                        VALUES (:bin, :bin_len, :card_len, :bank_name)
                    """)
                    db.execute(sql, new_data)
                elif request.change_type == "update":
                    old_data = json.loads(request.old_data)
                    sql = text("""
                        UPDATE bank_bin
                        SET bin = :bin, bin_len = :bin_len, card_len = :card_len, bank_name = :bank_name
                        WHERE bin = :old_bin
                    """)
                    db.execute(sql, {**new_data, "old_bin": old_data["bin"]})
                elif request.change_type == "delete":
                    sql = text("DELETE FROM bank_bin WHERE bin = :bin")
                    db.execute(sql, new_data)

            elif request.table_type == "sy_bank":
                if request.change_type == "create":
                    sql = text("""
                        INSERT INTO sy_bank (from_bank, to_bank, sys)
                        VALUES (:from_bank, :to_bank, :sys)
                    """)
                    db.execute(sql, new_data)
                elif request.change_type == "update":
                    old_data = json.loads(request.old_data)
                    sql = text("""
                        UPDATE sy_bank
                        SET from_bank = :from_bank, to_bank = :to_bank, sys = :sys
                        WHERE from_bank = :old_from_bank AND sys = :old_sys
                    """)
                    db.execute(sql, {**new_data, "old_from_bank": old_data["from_bank"], "old_sys": old_data["sys"]})
                elif request.change_type == "delete":
                    sql = text("DELETE FROM sy_bank WHERE from_bank = :from_bank AND sys = :sys")
                    db.execute(sql, new_data)

            # 更新申请状态为 executed
            request.status = "executed"
            request.executed_at = datetime.now()

            db.commit()

            return {"message": "审批通过，变更已执行"}

        except Exception as e:
            db.rollback()
            raise Exception(f"执行变更失败: {str(e)}")

    @staticmethod
    def reject_change_request(
        db: Session,
        request_id: int,
        reviewer_id: int,
        review_comment: Optional[str] = None
    ) -> Dict:
        """拒绝变更申请"""
        request = db.query(BankInfoChangeRequest).filter(BankInfoChangeRequest.id == request_id).first()

        if not request:
            raise ValueError("变更申请不存在")

        if request.status != "pending":
            raise ValueError(f"变更申请状态为 {request.status}，无法审批")

        request.status = "rejected"
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now()
        request.review_comment = review_comment

        db.commit()

        return {"message": "变更申请已拒绝"}

    @staticmethod
    def delete_change_request(
        db: Session,
        request_id: int,
        user_id: int
    ) -> Dict:
        """撤销变更申请（仅申请人可撤销待审批的申请）"""
        request = db.query(BankInfoChangeRequest).filter(BankInfoChangeRequest.id == request_id).first()

        if not request:
            raise ValueError("变更申请不存在")

        if request.created_by != user_id:
            raise ValueError("只能撤销自己的申请")

        if request.status != "pending":
            raise ValueError(f"变更申请状态为 {request.status}，无法撤销")

        db.delete(request)
        db.commit()

        return {"message": "变更申请已撤销"}

    # ==================== 导出功能 ====================

    @staticmethod
    def export_bank_bin(db: Session, **filters) -> BytesIO:
        """导出 BankBin 数据"""
        items, _ = BankInfoService.get_bank_bin_list(db, page=1, page_size=10000, **filters)

        df = pd.DataFrame(items)
        df.columns = ['BIN码', 'BIN长度', '卡长度', '银行名称']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='BIN码库')

        output.seek(0)
        return output

    @staticmethod
    def export_sy_bank(db: Session, **filters) -> BytesIO:
        """导出 SyBank 数据"""
        items, _ = BankInfoService.get_sy_bank_list(db, page=1, page_size=10000, **filters)

        df = pd.DataFrame(items)
        df.columns = ['原始银行名称', '标准银行名称', '系统标识']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='银行名称映射')

        output.seek(0)
        return output

    @staticmethod
    def get_bank_bin_template() -> BytesIO:
        """获取 BankBin 导入模板"""
        df = pd.DataFrame(columns=['BIN码', 'BIN长度', '卡长度', '银行名称'])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='BIN码库')

        output.seek(0)
        return output

    @staticmethod
    def get_sy_bank_template() -> BytesIO:
        """获取 SyBank 导入模板"""
        df = pd.DataFrame(columns=['原始银行名称', '标准银行名称', '系统标识'])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='银行名称映射')

        output.seek(0)
        return output
