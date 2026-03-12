import unittest
from unittest.mock import Mock, mock_open, patch

import pandas as pd

from backend.services.bank_statement_service import BankStatementProcessor
from backend.tasks.bank_statement_tasks import CallbackTask
from tools.bank_config import NAME_DICT


class CallbackTaskStatusTests(unittest.TestCase):
    def test_on_failure_updates_business_task_id_from_kwargs(self):
        task = CallbackTask()
        task.update_task_status = Mock()

        task.on_failure(
            Exception("boom"),
            "celery-task-id",
            (),
            {"task_id": "business-task-id"},
            None
        )

        task.update_task_status.assert_called_once_with(
            "business-task-id",
            "failed",
            error_message="boom"
        )


class TransferTableTests(unittest.TestCase):
    def test_transfer_table_uses_single_insert_without_batch_delete(self):
        processor = BankStatementProcessor(case_id=1, database_name="case_db", task_id="task-1")

        class FakeResult:
            def __init__(self, scalar_value=None, rowcount=0):
                self._scalar_value = scalar_value
                self.rowcount = rowcount

            def scalar(self):
                return self._scalar_value

        executed_sql = []
        results = iter([
            FakeResult(scalar_value=25000),
            FakeResult(rowcount=25000),
        ])

        class FakeConnection:
            def execute(self, sql):
                executed_sql.append(str(sql))
                return next(results)

            def commit(self):
                return None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        fake_engine = Mock()
        fake_engine.connect.return_value = FakeConnection()
        processor.engine = fake_engine

        processor._transfer_table("bank_all_statements")

        insert_statements = [sql for sql in executed_sql if "INSERT IGNORE INTO bank_all_statements" in sql]
        delete_statements = [sql for sql in executed_sql if "DELETE FROM bank_all_statements_tmp" in sql]

        self.assertEqual(len(insert_statements), 1)
        self.assertEqual(len(delete_statements), 0)
        self.assertNotIn("LIMIT", insert_statements[0].upper())
        self.assertNotIn("OFFSET", insert_statements[0].upper())


class ProcessFilesProgressTests(unittest.TestCase):
    def test_process_files_reports_csv_progress_with_consistent_counts(self):
        processor = BankStatementProcessor(case_id=1, database_name="case_db", task_id="task-1")
        progress_events = []

        with patch.object(
            processor,
            "count_files",
            return_value={"交易明细": 2, "人员信息": 0, "账户信息": 0, "子账户信息": 0, "强制措施信息": 0, "失败信息": 0}
        ), patch(
            "backend.services.bank_statement_service.os.walk",
            return_value=[("/tmp", [], ["a_交易明细.csv", "b_交易明细.csv"])]
        ), patch.object(
            processor,
            "_process_single_file",
            return_value=None
        ):
            processor.process_files(
                "/tmp",
                lambda step, progress=None, processed_files=None, total_files=None: progress_events.append(
                    (step, progress, processed_files, total_files)
                )
            )

        self.assertEqual(
            progress_events,
            [
                ("正在处理: a_交易明细.csv", 60.0, 1, 2),
                ("正在处理: b_交易明细.csv", 90.0, 2, 2),
            ]
        )


class DateNormalizationTests(unittest.TestCase):
    def test_invalid_datetime_values_are_written_as_null(self):
        processor = BankStatementProcessor(case_id=1, database_name="case_db", task_id="task-1")
        row = {
            column_name: ""
            for field_name, (column_name, _field_type) in NAME_DICT["账户信息"].items()
            if field_name != "source"
        }
        row["账号开户时间\t"] = "20240101"
        row["销户日期\t"] = "00000000"
        row["最后交易时间\t"] = "000000"

        processed = processor.process_dataframe(pd.DataFrame([row]), "账户信息")

        self.assertEqual(str(processed.loc[0, "accountOpeningTime"]), "2024-01-01 00:00:00")
        self.assertTrue(pd.isna(processed.loc[0, "accountClosureDate"]))
        self.assertTrue(pd.isna(processed.loc[0, "lastTradingTime"]))


class PostProcessingSqlTests(unittest.TestCase):
    def test_post_processing_insert_select_uses_single_statement_without_offset(self):
        processor = BankStatementProcessor(case_id=1, database_name="case_db", task_id="task-1")

        class FakeResult:
            def __init__(self, rowcount=0):
                self.rowcount = rowcount

        executed_sql = []

        class FakeConnection:
            def execute(self, sql):
                executed_sql.append(str(sql))
                return FakeResult(rowcount=123)

            def commit(self):
                return None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        fake_engine = Mock()
        fake_engine.connect.return_value = FakeConnection()
        processor.engine = fake_engine

        sql_content = "TRUNCATE TABLE bank_statements; INSERT INTO bank_statements SELECT * FROM bank_all_statements"

        with patch("builtins.open", mock_open(read_data=sql_content)):
            processor.execute_post_processing_sql()

        insert_statements = [sql for sql in executed_sql if "INSERT INTO bank_statements SELECT * FROM bank_all_statements" in sql]

        self.assertEqual(len(insert_statements), 4)
        self.assertTrue(all("LIMIT" not in sql.upper() for sql in insert_statements))
        self.assertTrue(all("OFFSET" not in sql.upper() for sql in insert_statements))


if __name__ == "__main__":
    unittest.main()
