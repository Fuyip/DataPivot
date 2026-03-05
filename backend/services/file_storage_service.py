"""
文件存储服务
管理银行流水文件的上传、存储、移动和清理
"""
import os
import shutil
from pathlib import Path
from typing import List, Tuple
from fastapi import UploadFile
from loguru import logger


class FileStorageService:
    """文件存储服务"""

    def __init__(self, base_dir: str = "./data/bank_statements"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.processing_dir = self.base_dir / "processing"
        self.processed_dir = self.base_dir / "processed"
        self.error_dir = self.base_dir / "error_files"

        # 确保目录存在
        for dir_path in [self.raw_dir, self.processing_dir,
                         self.processed_dir, self.error_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_case_upload_dir(self, case_id: int, task_id: str) -> Path:
        """获取案件上传目录"""
        upload_dir = self.raw_dir / f"case_{case_id}" / task_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    async def save_upload_file(self, file: UploadFile, save_path: Path) -> Tuple[str, float]:
        """
        保存上传文件

        Args:
            file: 上传的文件
            save_path: 保存目录

        Returns:
            Tuple[str, float]: 文件名和大小（MB）
        """
        file_path = save_path / file.filename

        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 计算文件大小
        file_size = len(content) / (1024 * 1024)  # MB

        logger.info(f"文件已保存: {file_path}, 大小: {file_size:.2f}MB")
        return file.filename, file_size

    def move_to_processing(self, case_id: int, task_id: str) -> Path:
        """
        将文件移动到处理目录

        Args:
            case_id: 案件ID
            task_id: 任务ID

        Returns:
            Path: 处理目录路径
        """
        src_dir = self.raw_dir / f"case_{case_id}" / task_id
        dst_dir = self.processing_dir / f"case_{case_id}" / task_id

        if src_dir.exists():
            dst_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_dir), str(dst_dir))
            logger.info(f"文件已移动到处理目录: {dst_dir}")

        return dst_dir

    def archive_processed_files(self, case_id: int, task_id: str):
        """
        归档已处理文件

        Args:
            case_id: 案件ID
            task_id: 任务ID
        """
        src_dir = self.processing_dir / f"case_{case_id}" / task_id
        dst_dir = self.processed_dir / f"case_{case_id}" / task_id

        if src_dir.exists():
            dst_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_dir), str(dst_dir))
            logger.info(f"文件已归档: {dst_dir}")

    def cleanup_task_files(self, case_id: int, task_id: str):
        """
        清理任务文件

        Args:
            case_id: 案件ID
            task_id: 任务ID
        """
        for base_dir in [self.raw_dir, self.processing_dir]:
            task_dir = base_dir / f"case_{case_id}" / task_id
            if task_dir.exists():
                shutil.rmtree(task_dir)
                logger.info(f"已清理任务文件: {task_dir}")

    def get_task_directory(self, case_id: int, task_id: str) -> Path:
        """
        获取任务目录（优先返回processing，其次raw）

        Args:
            case_id: 案件ID
            task_id: 任务ID

        Returns:
            Path: 任务目录路径
        """
        processing_dir = self.processing_dir / f"case_{case_id}" / task_id
        if processing_dir.exists():
            return processing_dir

        raw_dir = self.raw_dir / f"case_{case_id}" / task_id
        if raw_dir.exists():
            return raw_dir

        raise FileNotFoundError(f"任务目录不存在: case_{case_id}/{task_id}")
