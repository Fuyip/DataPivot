"""
银行流水异步处理任务
"""
from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from backend.core.celery_app import celery_app
from backend.services.bank_statement_service import BankStatementProcessor
from backend.services.file_storage_service import FileStorageService
from backend.models.bank_statement_task import BankStatementTask
from database import SystemSessionLocal


class CallbackTask(Task):
    """带回调的任务基类"""

    @staticmethod
    def resolve_business_task_id(celery_task_id, args, kwargs):
        """优先使用业务任务ID，回退到 Celery 任务ID。"""
        if kwargs and kwargs.get("task_id"):
            return kwargs["task_id"]
        if args and len(args) >= 3:
            return args[2]
        return celery_task_id

    def on_success(self, retval, task_id, args, kwargs):
        """任务成功回调"""
        self.update_task_status(
            self.resolve_business_task_id(task_id, args, kwargs),
            "completed",
            progress=100
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        self.update_task_status(
            self.resolve_business_task_id(task_id, args, kwargs),
            "failed",
            error_message=str(exc)
        )

    def update_task_status(self, task_id, status, **kwargs):
        """更新任务状态"""
        db = SystemSessionLocal()
        try:
            task = db.query(BankStatementTask).filter(
                BankStatementTask.task_id == task_id
            ).first()

            if task:
                task.status = status
                for key, value in kwargs.items():
                    setattr(task, key, value)

                if status in {"completed", "failed", "cancelled"}:
                    task.completed_at = datetime.now()

                db.commit()
        finally:
            db.close()


@celery_app.task(base=CallbackTask, bind=True)
def process_bank_statements(self, case_id: int, database_name: str,
                           task_id: str, storage_path: str,
                           template_id: int | None = None):
    """
    处理银行流水任务

    Args:
        self: Celery任务实例
        case_id: 案件ID
        database_name: 案件数据库名称
        task_id: 任务ID
        storage_path: 文件存储路径

    Returns:
        dict: 处理结果
    """

    db = SystemSessionLocal()
    processor = None
    file_service = FileStorageService()

    try:
        # 更新任务状态为处理中
        task = db.query(BankStatementTask).filter(
            BankStatementTask.task_id == task_id
        ).first()

        if not task:
            raise Exception(f"任务不存在: {task_id}")

        task.status = "processing"
        task.started_at = datetime.now()
        db.commit()

        logger.info(f"开始处理银行流水任务: {task_id}, 案件ID: {case_id}")

        # 初始化处理器
        processor = BankStatementProcessor(
            case_id,
            database_name,
            task_id,
            template_id=template_id,
            db_session=db
        )
        processor.connect_database()

        # 移动文件到处理目录
        processing_dir = file_service.move_to_processing(case_id, task_id)

        # 进度回调函数
        def update_progress(
            step: str,
            progress: float = None,
            processed_files: int | None = None,
            total_files: int | None = None
        ):
            task.current_step = step
            if progress is not None:
                task.progress = progress
            if processed_files is not None:
                task.processed_files = processed_files
            if total_files is not None:
                task.file_count = total_files
            db.commit()

            # 更新Celery任务状态
            self.update_state(
                state='PROGRESS',
                meta={
                    'current_step': step,
                    'progress': progress or task.progress,
                    'processed_files': task.processed_files,
                    'total_files': task.file_count
                }
            )

        # 1. 解压文件
        update_progress("解压文件", 10)
        processor.extract_archives(processing_dir, update_progress)

        # 2. 统计文件
        update_progress("统计文件", 20)
        file_counts = processor.count_files(processing_dir)
        task.file_count = sum(file_counts.values())
        task.processed_files = 0
        db.commit()

        # 3. 清空临时表
        update_progress("准备数据库", 25)
        processor.truncate_tmp_tables()

        # 4. 处理文件
        update_progress("处理数据文件", 30)
        processor.process_files(processing_dir, update_progress)

        # 5. 转移到正式表
        update_progress("转移数据到正式表", 90)
        processor.transfer_to_final_tables(update_progress)

        # 6. 执行后处理SQL脚本
        update_progress("执行后处理SQL脚本", 95)
        processor.execute_post_processing_sql(update_progress)

        # 7. 获取统计信息
        stats = processor.get_statistics()
        task.statistics = stats["statistics"]
        task.total_records = stats["total_records"]
        task.success_records = stats["success_records"]
        task.error_records = stats["error_records"]
        task.error_files = stats["error_files"]
        task.progress = 100
        task.current_step = "处理完成"
        task.status = "completed"
        task.completed_at = datetime.now()
        db.commit()

        # 8. 归档文件
        file_service.archive_processed_files(case_id, task_id)

        logger.info(f"银行流水任务处理完成: {task_id}")

        return {
            "status": "success",
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"处理银行流水任务失败: {task_id}, 错误: {str(e)}")
        # 记录错误
        task = db.query(BankStatementTask).filter(
            BankStatementTask.task_id == task_id
        ).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
        raise

    finally:
        if processor:
            processor.cleanup()
        db.close()
