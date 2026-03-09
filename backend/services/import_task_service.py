"""
导入任务服务
"""
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_system_db
from backend.models.import_task import ImportTask
import json


class ImportTaskService:
    """导入任务服务"""

    @staticmethod
    def _clean_nan_values(obj):
        """递归清理对象中的 NaN 值，替换为字符串"""
        import math

        if isinstance(obj, dict):
            return {k: ImportTaskService._clean_nan_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ImportTaskService._clean_nan_values(item) for item in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return "未知"
        else:
            return obj

    @staticmethod
    def get_import_tasks(case_id: int, page: int = 1, page_size: int = 20) -> dict:
        """获取导入任务列表"""
        db = next(get_system_db())

        try:
            # 查询总数
            count_sql = "SELECT COUNT(*) FROM import_task WHERE case_id = :case_id"
            total = db.execute(text(count_sql), {"case_id": case_id}).scalar()

            # 查询数据
            offset = (page - 1) * page_size
            query_sql = """
                SELECT id, case_id, task_type, file_name, total_count,
                       success_count, error_count, error_details,
                       created_by, created_at
                FROM import_task
                WHERE case_id = :case_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """

            result = db.execute(text(query_sql), {
                "case_id": case_id,
                "limit": page_size,
                "offset": offset
            })

            items = []
            for row in result:
                item = dict(row._mapping)
                # 解析错误详情JSON
                if item['error_details']:
                    try:
                        error_details = json.loads(item['error_details'])
                        # 清理 NaN 值，确保可以序列化
                        item['error_details'] = ImportTaskService._clean_nan_values(error_details)
                    except:
                        item['error_details'] = []
                items.append(item)

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        finally:
            db.close()

    @staticmethod
    def get_import_task(task_id: int) -> Optional[dict]:
        """获取单个导入任务"""
        db = next(get_system_db())

        try:
            query_sql = """
                SELECT id, case_id, task_type, file_name, total_count,
                       success_count, error_count, error_details,
                       created_by, created_at
                FROM import_task
                WHERE id = :task_id
            """

            result = db.execute(text(query_sql), {"task_id": task_id}).fetchone()

            if result:
                item = dict(result._mapping)
                # 解析错误详情JSON
                if item['error_details']:
                    try:
                        error_details = json.loads(item['error_details'])
                        # 清理 NaN 值，确保可以序列化
                        item['error_details'] = ImportTaskService._clean_nan_values(error_details)
                    except:
                        item['error_details'] = []
                return item
            return None
        finally:
            db.close()

    @staticmethod
    def delete_cards_by_task(database_name: str, task_id: int) -> dict:
        """根据导入任务ID批量删除银行卡"""
        from backend.services.case_card_service import CaseCardService

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

            if not has_import_task_id:
                # 如果表中没有 import_task_id 字段，无法按任务删除
                return {
                    "deleted_count": 0,
                    "expected_count": 0,
                    "message": "该案件数据库表结构不支持按导入任务删除"
                }

            # 查询要删除的记录数
            count_sql = "SELECT COUNT(*) FROM case_card WHERE import_task_id = :task_id"
            count = db.execute(text(count_sql), {"task_id": task_id}).scalar()

            # 删除记录
            delete_sql = "DELETE FROM case_card WHERE import_task_id = :task_id"
            result = db.execute(text(delete_sql), {"task_id": task_id})
            db.commit()

            return {
                "deleted_count": result.rowcount,
                "expected_count": count
            }
        except Exception as e:
            db.rollback()
            raise ValueError(f"删除失败: {str(e)}")
        finally:
            db.close()
