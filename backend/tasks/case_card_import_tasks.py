"""
案件银行卡导入异步任务
"""
import json
from datetime import datetime

from celery import Task
from loguru import logger

from backend.core.celery_app import celery_app
from backend.models.import_task import ImportTask
from backend.services.case_card_service import CaseCardService
from database import SystemSessionLocal


class CaseCardImportTask(Task):
    """案件银行卡导入任务基类"""

    @staticmethod
    def update_import_task(import_task_id: int, **fields):
        db = SystemSessionLocal()
        try:
            task = db.query(ImportTask).filter(ImportTask.id == import_task_id).first()
            if not task:
                return

            for key, value in fields.items():
                setattr(task, key, value)

            db.commit()
        finally:
            db.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        import_task_id = args[0] if args else None
        if import_task_id is not None:
            self.update_import_task(
                import_task_id,
                status="failed",
                progress=100,
                current_step="导入失败",
                error_message=str(exc),
                completed_at=datetime.now()
            )


@celery_app.task(base=CaseCardImportTask, bind=True, name="tasks.process_case_card_import")
def process_case_card_import(
    self,
    import_task_id: int,
    case_id: int,
    database_name: str,
    case_code: str,
    file_path: str
):
    """后台处理案件银行卡导入"""

    logger.info(f"开始处理案件银行卡导入任务: import_task_id={import_task_id}, case_id={case_id}")

    def progress_callback(step: str, progress: float, total_count: int | None = None):
        update_fields = {
            "current_step": step,
            "progress": progress
        }
        if total_count is not None:
            update_fields["total_count"] = total_count

        self.update_import_task(import_task_id, **update_fields)
        self.update_state(state="PROGRESS", meta={"step": step, "progress": progress})

    self.update_import_task(
        import_task_id,
        status="processing",
        progress=1,
        current_step="准备导入",
        started_at=datetime.now(),
        error_message=None
    )

    result = CaseCardService.process_import_file(
        database_name=database_name,
        case_code=case_code,
        file_path=file_path,
        task_id=import_task_id,
        progress_callback=progress_callback
    )

    self.update_import_task(
        import_task_id,
        status="completed",
        progress=100,
        current_step="导入完成",
        total_count=result["total_count"],
        success_count=result["success_count"],
        error_count=result["error_count"],
        error_details=json.dumps(result["errors"], ensure_ascii=False),
        completed_at=datetime.now()
    )

    logger.info(f"案件银行卡导入任务完成: import_task_id={import_task_id}")
    return result
