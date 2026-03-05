"""
案件相关的异步任务
"""
import logging
from backend.core.celery_app import celery_app
from backend.services.case_service import initialize_case_database_schema

# 配置日志
logger = logging.getLogger(__name__)


@celery_app.task(name='tasks.initialize_case_database', bind=True, max_retries=3)
def initialize_case_database_task(self, database_name: str, case_code: str):
    """
    异步初始化案件数据库表结构

    Args:
        database_name: 数据库名称
        case_code: 案件编号

    Returns:
        dict: 包含状态和消息的字典
    """
    logger.info(f"开始执行案件数据库初始化任务: {database_name}")

    try:
        initialize_case_database_schema(database_name, case_code)

        success_msg = f'案件数据库 {database_name} 初始化成功'
        logger.info(success_msg)

        return {
            'status': 'success',
            'message': success_msg,
            'database_name': database_name,
            'case_code': case_code
        }
    except Exception as e:
        error_msg = f'案件数据库初始化失败: {str(e)}'
        logger.error(f"任务执行失败: {error_msg}")
        logger.exception(e)  # 记录完整的异常堆栈

        # 尝试重试
        try:
            raise self.retry(exc=e, countdown=60)  # 60秒后重试
        except self.MaxRetriesExceededError:
            logger.error(f"任务重试次数已达上限，最终失败: {database_name}")
            return {
                'status': 'error',
                'message': error_msg,
                'database_name': database_name,
                'case_code': case_code,
                'retries_exceeded': True
            }

