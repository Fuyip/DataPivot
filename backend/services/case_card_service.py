from typing import Optional
from sqlalchemy import text, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from database import get_db
from backend.schemas.case_card import CaseCardCreate, CaseCardUpdate
from backend.services.case_service import get_case_database_url
import pandas as pd
from io import BytesIO


class CaseCardService:
    """案件银行卡服务"""

    @staticmethod
    def _get_case_db(database_name: str) -> Session:
        """获取案件数据库连接"""
        database_url = get_case_database_url(database_name)
        engine = create_engine(database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()

    @staticmethod
    def get_case_cards(database_name: str, page: int = 1, page_size: int = 20,
                       card_no: Optional[str] = None, bank_name: Optional[str] = None,
                       card_type: Optional[str] = None) -> dict:
        """获取案件银行卡列表"""
        db = CaseCardService._get_case_db(database_name)

        try:
            # 构建查询条件
            where_clauses = []
            params = {}

            if card_no:
                where_clauses.append("card_no LIKE :card_no")
                params['card_no'] = f"%{card_no}%"

            if bank_name:
                where_clauses.append("bank_name LIKE :bank_name")
                params['bank_name'] = f"%{bank_name}%"

            if card_type:
                where_clauses.append("card_type = :card_type")
                params['card_type'] = card_type

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM case_card WHERE {where_sql}"
            total = db.execute(text(count_sql), params).scalar()

            # 查询数据
            offset = (page - 1) * page_size
            params['limit'] = page_size
            params['offset'] = offset

            query_sql = f"""
                SELECT id, case_no, source, user_id, card_no, bank_name, card_type,
                       add_date, batch, is_in_bg, is_main
                FROM case_card
                WHERE {where_sql}
                ORDER BY add_date DESC
                LIMIT :limit OFFSET :offset
            """

            result = db.execute(text(query_sql), params)
            items = [dict(row._mapping) for row in result]

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        finally:
            db.close()

    @staticmethod
    def get_case_card(database_name: str, card_id: int) -> Optional[dict]:
        """获取单个案件银行卡"""
        db = CaseCardService._get_case_db(database_name)

        try:
            query_sql = """
                SELECT id, case_no, source, user_id, card_no, bank_name, card_type,
                       add_date, batch, is_in_bg, is_main
                FROM case_card
                WHERE id = :card_id
            """

            result = db.execute(text(query_sql), {"card_id": card_id}).fetchone()
            return dict(result._mapping) if result else None
        finally:
            db.close()

    @staticmethod
    def create_case_card(database_name: str, case_code: str, card_data: CaseCardCreate) -> dict:
        """创建案件银行卡"""
        db = CaseCardService._get_case_db(database_name)

        try:
            insert_sql = """
                INSERT INTO case_card (case_no, source, user_id, card_no, bank_name,
                                      card_type, batch, is_in_bg, is_main)
                VALUES (:case_no, :source, :user_id, :card_no, :bank_name,
                        :card_type, :batch, :is_in_bg, :is_main)
            """

            params = {
                "case_no": case_code,
                "source": card_data.source,
                "user_id": card_data.user_id,
                "card_no": card_data.card_no,
                "bank_name": card_data.bank_name,
                "card_type": card_data.card_type,
                "batch": card_data.batch,
                "is_in_bg": card_data.is_in_bg,
                "is_main": card_data.is_main
            }

            result = db.execute(text(insert_sql), params)
            db.commit()

            # 获取插入的ID
            card_id = result.lastrowid
            return CaseCardService.get_case_card(database_name, card_id)

        except IntegrityError:
            db.rollback()
            raise ValueError(f"卡号 {card_data.card_no} 已存在")
        finally:
            db.close()

    @staticmethod
    def update_case_card(database_name: str, card_id: int, card_data: CaseCardUpdate) -> Optional[dict]:
        """更新案件银行卡"""
        db = CaseCardService._get_case_db(database_name)

        try:
            # 构建更新字段
            update_fields = []
            params = {"card_id": card_id}

            if card_data.bank_name is not None:
                update_fields.append("bank_name = :bank_name")
                params['bank_name'] = card_data.bank_name

            if card_data.card_type is not None:
                update_fields.append("card_type = :card_type")
                params['card_type'] = card_data.card_type

            if card_data.source is not None:
                update_fields.append("source = :source")
                params['source'] = card_data.source

            if card_data.user_id is not None:
                update_fields.append("user_id = :user_id")
                params['user_id'] = card_data.user_id

            if card_data.batch is not None:
                update_fields.append("batch = :batch")
                params['batch'] = card_data.batch

            if card_data.is_in_bg is not None:
                update_fields.append("is_in_bg = :is_in_bg")
                params['is_in_bg'] = card_data.is_in_bg

            if card_data.is_main is not None:
                update_fields.append("is_main = :is_main")
                params['is_main'] = card_data.is_main

            if not update_fields:
                return CaseCardService.get_case_card(database_name, card_id)

            update_sql = f"""
                UPDATE case_card
                SET {', '.join(update_fields)}
                WHERE id = :card_id
            """

            db.execute(text(update_sql), params)
            db.commit()

            return CaseCardService.get_case_card(database_name, card_id)
        finally:
            db.close()

    @staticmethod
    def delete_case_card(database_name: str, card_id: int) -> bool:
        """删除案件银行卡"""
        db = CaseCardService._get_case_db(database_name)

        try:
            delete_sql = "DELETE FROM case_card WHERE id = :card_id"
            result = db.execute(text(delete_sql), {"card_id": card_id})
            db.commit()

            return result.rowcount > 0
        finally:
            db.close()

    @staticmethod
    def export_case_cards(database_name: str) -> BytesIO:
        """导出案件银行卡为Excel"""
        db = CaseCardService._get_case_db(database_name)

        try:
            query_sql = """
                SELECT id, case_no, source, user_id, card_no, bank_name, card_type,
                       add_date, batch, is_in_bg, is_main
                FROM case_card
                ORDER BY add_date DESC
            """

            result = db.execute(text(query_sql))
            data = [dict(row._mapping) for row in result]

            # 转换为DataFrame
            df = pd.DataFrame(data)

            # 重命名列
            df.columns = ['ID', '案件编号', '来源', '用户ID', '卡号', '银行名称',
                          '卡类型', '添加日期', '批次', '是否在后台', '是否主卡']

            # 导出到Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='案件银行卡')

            output.seek(0)
            return output
        finally:
            db.close()

    @staticmethod
    def import_from_template(database_name: str, case_code: str, file_content: bytes) -> dict:
        """从模板导入案件银行卡"""
        db = CaseCardService._get_case_db(database_name)

        try:
            # 读取Excel文件
            df = pd.read_excel(BytesIO(file_content))

            # 验证必需列
            required_columns = ['卡号']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            success_count = 0
            error_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # 准备数据
                    card_data = {
                        "case_no": case_code,
                        "card_no": str(row['卡号']).strip(),
                        "bank_name": str(row.get('银行名称', '')).strip() if pd.notna(row.get('银行名称')) else None,
                        "card_type": str(row.get('卡类型', '')).strip() if pd.notna(row.get('卡类型')) else None,
                        "source": str(row.get('来源', '')).strip() if pd.notna(row.get('来源')) else None,
                        "user_id": str(row.get('用户ID', '')).strip() if pd.notna(row.get('用户ID')) else None,
                        "batch": int(row.get('批次', 0)) if pd.notna(row.get('批次')) else None,
                        "is_in_bg": int(row.get('是否在后台', 0)) if pd.notna(row.get('是否在后台')) else None,
                        "is_main": int(row.get('是否主卡', 0)) if pd.notna(row.get('是否主卡')) else None
                    }

                    # 插入数据
                    insert_sql = """
                        INSERT INTO case_card (case_no, source, user_id, card_no, bank_name,
                                              card_type, batch, is_in_bg, is_main)
                        VALUES (:case_no, :source, :user_id, :card_no, :bank_name,
                                :card_type, :batch, :is_in_bg, :is_main)
                    """

                    db.execute(text(insert_sql), card_data)
                    success_count += 1

                except IntegrityError:
                    error_count += 1
                    errors.append(f"第{index + 2}行: 卡号 {row['卡号']} 已存在")
                    db.rollback()
                except Exception as e:
                    error_count += 1
                    errors.append(f"第{index + 2}行: {str(e)}")
                    db.rollback()

            db.commit()

            return {
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors[:10]  # 只返回前10个错误
            }

        except Exception as e:
            db.rollback()
            raise ValueError(f"导入失败: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def get_template() -> BytesIO:
        """获取导入模板"""
        # 创建模板DataFrame
        template_data = {
            '卡号': ['6222021234567890123', '6228481234567890123'],
            '银行名称': ['工商银行', '农业银行'],
            '卡类型': ['借记卡', '借记卡'],
            '来源': ['线索', '调证'],
            '用户ID': ['', ''],
            '批次': [1, 1],
            '是否在后台': [0, 0],
            '是否主卡': [1, 0]
        }

        df = pd.DataFrame(template_data)

        # 导出到Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='案件银行卡模板')

        output.seek(0)
        return output
