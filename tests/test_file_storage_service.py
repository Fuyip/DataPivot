import io
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi import UploadFile

from backend.services.file_storage_service import FileStorageService


class FileStorageServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="file-storage-service-")
        self.service = FileStorageService(base_dir=self.temp_dir)
        self.save_path = Path(self.temp_dir) / "uploads"
        self.save_path.mkdir(parents=True, exist_ok=True)

    async def asyncTearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_save_upload_file_preserves_relative_path(self):
        upload = UploadFile(
            filename="交易明细.csv",
            file=io.BytesIO("header\nvalue\n".encode("utf-8"))
        )

        saved_name, _ = await self.service.save_upload_file(
            upload,
            self.save_path,
            "银行A/账户1/交易明细.csv"
        )

        self.assertEqual(saved_name, "银行A/账户1/交易明细.csv")
        self.assertTrue((self.save_path / "银行A" / "账户1" / "交易明细.csv").exists())

    async def test_save_upload_file_rejects_path_traversal(self):
        upload = UploadFile(
            filename="交易明细.csv",
            file=io.BytesIO("header\nvalue\n".encode("utf-8"))
        )

        saved_name, _ = await self.service.save_upload_file(
            upload,
            self.save_path,
            "../交易明细.csv"
        )

        self.assertEqual(saved_name, "交易明细.csv")
        self.assertTrue((self.save_path / "交易明细.csv").exists())
        self.assertFalse((Path(self.temp_dir).parent / "交易明细.csv").exists())


if __name__ == "__main__":
    unittest.main()
