"""
Celery配置
用于异步处理银行流水任务
"""
from celery import Celery
from backend.core.config import config

# 创建Celery应用
celery_app = Celery(
    "datapivot",
    broker=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/0",
    backend=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}/1",
    include=['backend.tasks.bank_statement_tasks', 'backend.tasks.case_tasks']  # 直接包含任务模块
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600 * 4,  # 4小时超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
