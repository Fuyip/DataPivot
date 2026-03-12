import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable, Optional
from uuid import uuid4

import pandas as pd
from sqlalchemy import text, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, Session
from database import get_db, get_system_db
from backend.schemas.case_card import CaseCardCreate, CaseCardUpdate
from backend.services.case_service import get_case_database_url
from io import BytesIO


class CaseCardService:
    """案件银行卡服务"""

    IMPORT_BASE_DIR = Path("./data/case_card_imports")

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

            # 检查表是否有 import_task_id 字段
            check_column_sql = """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'case_card'
                AND COLUMN_NAME = 'import_task_id'
            """
            has_import_task_id = db.execute(text(check_column_sql)).scalar() > 0

            # 根据字段是否存在构建查询
            if has_import_task_id:
                query_sql = f"""
                    SELECT id, case_no, source, user_id, card_no, bank_name, card_type,
                           add_date, batch, is_in_bg, is_main, import_task_id
                    FROM case_card
                    WHERE {where_sql}
                    ORDER BY add_date DESC
                    LIMIT :limit OFFSET :offset
                """
            else:
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
            # 检查表是否有 import_task_id 字段
            check_column_sql = """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'case_card'
                AND COLUMN_NAME = 'import_task_id'
            """
            has_import_task_id = db.execute(text(check_column_sql)).scalar() > 0

            # 根据字段是否存在构建查询
            if has_import_task_id:
                query_sql = """
                    SELECT id, case_no, source, user_id, card_no, bank_name, card_type,
                           add_date, batch, is_in_bg, is_main, import_task_id
                    FROM case_card
                    WHERE id = :card_id
                """
            else:
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
    def import_from_template(database_name: str, case_code: str, file_content: bytes, case_id: int, user_id: int) -> dict:
        """从模板导入案件银行卡"""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name

            return CaseCardService.process_import_file(
                database_name=database_name,
                case_code=case_code,
                file_path=temp_path
            )
        except Exception as e:
            raise ValueError(f"导入失败: {str(e)}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

    @staticmethod
    def enqueue_import_task(
        database_name: str,
        case_code: str,
        case_id: int,
        user_id: int,
        upload_file
    ) -> dict:
        """创建后台导入任务并保存上传文件"""
        from database import SystemSessionLocal
        from backend.models.import_task import ImportTask
        from backend.tasks.case_card_import_tasks import process_case_card_import

        system_db = SystemSessionLocal()
        storage_dir = None

        try:
            original_filename = Path(upload_file.filename or "case_card_import.xlsx").name
            task_ref = str(uuid4())
            storage_dir = CaseCardService.IMPORT_BASE_DIR / "raw" / f"case_{case_id}" / task_ref
            storage_dir.mkdir(parents=True, exist_ok=True)
            storage_path = storage_dir / original_filename

            upload_file.file.seek(0)
            with open(storage_path, "wb") as target:
                shutil.copyfileobj(upload_file.file, target)

            import_task = ImportTask(
                case_id=case_id,
                task_type="case_card",
                file_name=original_filename,
                status="pending",
                progress=0,
                current_step="等待后台处理",
                created_by=user_id,
                storage_path=str(storage_path)
            )
            system_db.add(import_task)
            system_db.commit()
            system_db.refresh(import_task)

            async_result = process_case_card_import.delay(
                import_task.id,
                case_id,
                database_name,
                case_code,
                str(storage_path)
            )

            import_task.task_ref = async_result.id
            system_db.commit()

            return {
                "task_id": import_task.id,
                "status": import_task.status,
                "file_name": import_task.file_name
            }
        except Exception:
            system_db.rollback()
            if storage_dir and storage_dir.exists():
                shutil.rmtree(storage_dir, ignore_errors=True)
            raise
        finally:
            system_db.close()

    @staticmethod
    def process_import_file(
        database_name: str,
        case_code: str,
        file_path: str,
        task_id: int | None = None,
        progress_callback: Optional[Callable[[str, float, int | None], None]] = None
    ) -> dict:
        """处理导入文件并写入案件银行卡表"""
        db = CaseCardService._get_case_db(database_name)

        try:
            if progress_callback:
                progress_callback("读取导入文件", 5, None)

            df = pd.read_excel(file_path, dtype={'卡号': str})

            required_columns = ['卡号']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"缺少必需列: {col}")

            total_count = len(df)
            if progress_callback:
                progress_callback("校验导入数据", 10, total_count)

            card_types = CaseCardService.get_card_types()
            value_to_label_map = {ct['value']: ct['label'] for ct in card_types}
            label_to_label_map = {ct['label']: ct['label'] for ct in card_types}

            check_column_sql = """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'case_card'
                AND COLUMN_NAME = 'import_task_id'
            """
            has_import_task_id = db.execute(text(check_column_sql)).scalar() > 0

            success_count = 0
            error_count = 0
            errors = []
            progress_interval = max(1, min(200, total_count // 20 or 1))

            for index, row in df.iterrows():
                try:
                    if pd.isna(row['卡号']) or str(row['卡号']).strip() == '':
                        error_count += 1
                        errors.append({
                            "row": index + 2,
                            "card_no": "空",
                            "error": "卡号不能为空"
                        })
                        continue

                    card_no = str(row['卡号']).strip()

                    check_sql = "SELECT id FROM case_card WHERE card_no = :card_no"
                    existing = db.execute(text(check_sql), {"card_no": card_no}).fetchone()
                    if existing:
                        error_count += 1
                        errors.append({
                            "row": index + 2,
                            "card_no": card_no,
                            "error": "卡号已存在"
                        })
                        continue

                    match_result = CaseCardService.match_bank_name(card_no)
                    bank_name = match_result['bank_name'] if match_result['matched'] else None

                    card_type_input = str(row.get('卡类型', '')).strip() if pd.notna(row.get('卡类型')) else None
                    card_type_label = None
                    if card_type_input:
                        if card_type_input in label_to_label_map:
                            card_type_label = card_type_input
                        elif card_type_input in value_to_label_map:
                            card_type_label = value_to_label_map[card_type_input]
                        else:
                            error_count += 1
                            errors.append({
                                "row": index + 2,
                                "card_no": card_no,
                                "error": f"无效的卡类型: {card_type_input}"
                            })
                            continue
                    else:
                        error_count += 1
                        errors.append({
                            "row": index + 2,
                            "card_no": card_no,
                            "error": "卡类型不能为空"
                        })
                        continue

                    card_data = {
                        "case_no": case_code,
                        "card_no": card_no,
                        "bank_name": bank_name,
                        "card_type": card_type_label,
                        "source": str(row.get('卡主姓名', '')).strip() if pd.notna(row.get('卡主姓名')) else None,
                        "user_id": str(row.get('用户ID', '')).strip() if pd.notna(row.get('用户ID')) else None,
                        "batch": int(row.get('批次', 0)) if pd.notna(row.get('批次')) else 0,
                        "is_in_bg": 0,
                        "is_main": 0
                    }

                    if has_import_task_id and task_id is not None:
                        card_data["import_task_id"] = task_id
                        insert_sql = """
                            INSERT INTO case_card (case_no, source, user_id, card_no, bank_name,
                                                  card_type, batch, is_in_bg, is_main, import_task_id)
                            VALUES (:case_no, :source, :user_id, :card_no, :bank_name,
                                    :card_type, :batch, :is_in_bg, :is_main, :import_task_id)
                        """
                    else:
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
                    errors.append({
                        "row": index + 2,
                        "card_no": card_no if 'card_no' in locals() else "未知",
                        "error": "卡号已存在"
                    })
                except Exception as e:
                    error_count += 1
                    safe_card_no = "未知"
                    if 'card_no' in locals():
                        safe_card_no = card_no
                    elif pd.notna(row.get('卡号')):
                        safe_card_no = str(row.get('卡号'))

                    errors.append({
                        "row": index + 2,
                        "card_no": safe_card_no,
                        "error": str(e)
                    })
                finally:
                    if progress_callback and (
                        index == total_count - 1 or (index + 1) % progress_interval == 0
                    ):
                        progress = 15 + ((index + 1) / max(total_count, 1)) * 80
                        progress_callback("导入银行卡数据", round(progress, 2), total_count)

            db.commit()

            if progress_callback:
                progress_callback("整理导入结果", 95, total_count)

            return {
                "task_id": task_id,
                "total_count": total_count,
                "success_count": success_count,
                "error_count": error_count,
                "errors": errors[:50]
            }
        except Exception as e:
            db.rollback()
            raise ValueError(f"导入失败: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def match_bank_name(card_no: str) -> dict:
        """
        根据卡号自动匹配银行名称

        Args:
            card_no: 银行卡号

        Returns:
            {"bank_name": "中国工商银行", "matched": True} 或
            {"bank_name": None, "matched": False}
        """
        db = next(get_system_db())
        try:
            sql = text("""
                SELECT t3.to_bank
                FROM bank_bin t1
                LEFT JOIN sy_bank t3
                    ON t3.from_bank = t1.bank_name AND t3.sys = 'jz'
                WHERE t1.bin = LEFT(:card_no, t1.bin_len)
                    AND t1.card_len = LENGTH(:card_no)
                LIMIT 1
            """)

            result = db.execute(sql, {"card_no": card_no}).fetchone()

            if result and result[0]:
                return {"bank_name": result[0], "matched": True}
            else:
                return {"bank_name": None, "matched": False}
        finally:
            db.close()

    @staticmethod
    def get_card_types() -> list:
        """
        获取卡类型字典

        Returns:
            [{"value": "c30", "label": "疑似员工卡"}, ...]
        """
        db = next(get_system_db())
        try:
            sql = text("""
                SELECT d_value, d_label
                FROM sys_dict
                WHERE d_type = 'card_type'
                ORDER BY d_value
            """)

            result = db.execute(sql)
            return [{"value": row[0], "label": row[1]} for row in result]
        finally:
            db.close()

    @staticmethod
    def batch_delete_case_cards(database_name: str, card_ids: list) -> dict:
        """
        批量删除案件银行卡

        Args:
            database_name: 案件数据库名称
            card_ids: 要删除的卡片ID列表

        Returns:
            {"success_count": 3, "failed_count": 0}
        """
        db = CaseCardService._get_case_db(database_name)

        try:
            success_count = 0
            failed_count = 0

            for card_id in card_ids:
                try:
                    delete_sql = "DELETE FROM case_card WHERE id = :card_id"
                    result = db.execute(text(delete_sql), {"card_id": card_id})
                    if result.rowcount > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception:
                    failed_count += 1

            db.commit()

            return {
                "success_count": success_count,
                "failed_count": failed_count
            }
        except Exception as e:
            db.rollback()
            raise ValueError(f"批量删除失败: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def rematch_unmatched_banks(database_name: str) -> dict:
        """
        重新匹配未匹配的银行名称

        Returns:
            {"matched_count": 5, "unmatched_count": 2}
        """
        db = CaseCardService._get_case_db(database_name)

        try:
            # 查询所有未匹配银行名称的卡（bank_name为NULL）
            query_sql = "SELECT id, card_no FROM case_card WHERE bank_name IS NULL"
            result = db.execute(text(query_sql))
            unmatched_cards = [dict(row._mapping) for row in result]

            matched_count = 0
            unmatched_count = 0

            for card in unmatched_cards:
                # 尝试匹配银行名称
                match_result = CaseCardService.match_bank_name(card['card_no'])

                if match_result['matched']:
                    # 更新银行名称
                    update_sql = "UPDATE case_card SET bank_name = :bank_name WHERE id = :card_id"
                    db.execute(text(update_sql), {
                        "bank_name": match_result['bank_name'],
                        "card_id": card['id']
                    })
                    matched_count += 1
                else:
                    unmatched_count += 1

            db.commit()

            return {
                "matched_count": matched_count,
                "unmatched_count": unmatched_count
            }
        except Exception as e:
            db.rollback()
            raise ValueError(f"重新匹配失败: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def get_template() -> BytesIO:
        """获取导入模板"""
        from openpyxl import Workbook
        from openpyxl.worksheet.datavalidation import DataValidation

        # 获取卡类型字典
        card_types = CaseCardService.get_card_types()
        card_type_labels = [ct['label'] for ct in card_types]

        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = '案件银行卡模板'

        # 设置表头
        headers = ['卡号', '卡类型', '卡主姓名', '用户ID', '批次']
        ws.append(headers)

        # 添加示例数据
        ws.append(['6222021234567890123', '公司入款卡', '张三', 'user001', 1])
        ws.append(['6228481234567890123', '四方(跑分)入款卡', '李四', 'user002', 1])

        # 为卡类型列添加数据验证（下拉选项）
        if card_type_labels:
            dv = DataValidation(
                type="list",
                formula1=f'"{",".join(card_type_labels)}"',
                allow_blank=True
            )
            dv.error = '请从下拉列表中选择卡类型'
            dv.errorTitle = '无效的卡类型'
            ws.add_data_validation(dv)
            # 应用到B列（卡类型列）的所有行
            dv.add(f'B2:B1000')

        # 调整列宽
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 10

        # 保存到BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_import_errors(errors: list) -> BytesIO:
        """导出导入错误报告为Excel"""
        from openpyxl import Workbook

        # 创建工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = '导入错误报告'

        # 设置表头
        headers = ['行号', '卡号', '错误原因']
        ws.append(headers)

        # 添加错误数据
        for error in errors:
            ws.append([
                error.get('row', ''),
                error.get('card_no', ''),
                error.get('error', '')
            ])

        # 调整列宽
        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 50

        # 保存到BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output
