import asyncio
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException, UploadFile

from backend.api.v1 import case_cards


class CaseCardImportAsyncTests(unittest.TestCase):
    def test_import_case_cards_returns_pending_task_instead_of_sync_result(self):
        async def run_test():
            file = UploadFile(filename="cards.xlsx", file=io.BytesIO(b"fake excel"))
            user = SimpleNamespace(id=7, role="admin")

            with patch.object(
                case_cards,
                "check_case_permission",
                return_value=SimpleNamespace(database_name="case_test_db", case_code="CASE001")
            ), patch.object(
                case_cards.CaseCardService,
                "import_from_template",
                side_effect=AssertionError("同步导入不应在请求线程执行")
            ), patch.object(
                case_cards.CaseCardService,
                "enqueue_import_task",
                return_value={
                    "task_id": 123,
                    "status": "pending",
                    "file_name": "cards.xlsx"
                },
                create=True
            ):
                return await case_cards.import_case_cards(
                    case_id=1,
                    file=file,
                    current_user=user,
                    db=object()
                )

        response = asyncio.run(run_test())

        self.assertEqual(response["message"], "导入任务已创建")
        self.assertEqual(
            response["data"],
            {
                "task_id": 123,
                "status": "pending",
                "file_name": "cards.xlsx"
            }
        )

    def test_import_case_cards_rejects_non_excel_files(self):
        async def run_test():
            file = UploadFile(filename="cards.csv", file=io.BytesIO(b"bad"))
            user = SimpleNamespace(id=7, role="admin")

            with patch.object(
                case_cards,
                "check_case_permission",
                return_value=SimpleNamespace(database_name="case_test_db", case_code="CASE001")
            ):
                return await case_cards.import_case_cards(
                    case_id=1,
                    file=file,
                    current_user=user,
                    db=object()
                )

        with self.assertRaises(HTTPException) as exc_info:
            asyncio.run(run_test())

        self.assertEqual(exc_info.exception.status_code, 400)
        self.assertEqual(exc_info.exception.detail, "只支持Excel文件(.xlsx, .xls)")


if __name__ == "__main__":
    unittest.main()
