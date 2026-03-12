import unittest
import sys
from types import SimpleNamespace
from types import ModuleType
from unittest.mock import MagicMock, patch

from backend.api.v1 import cases
from backend.schemas.case import CaseCreate


class CaseCreationInitializationTest(unittest.TestCase):
    def test_create_case_initializes_schema_before_returning_success(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        current_user = SimpleNamespace(id=1, role="admin")
        case_data = CaseCreate(case_name="测试案件", case_code="ABCDE", description="desc")
        fake_task_module = ModuleType("backend.tasks.case_tasks")
        fake_task_module.initialize_case_database_task = SimpleNamespace(delay=MagicMock())

        with patch("backend.api.v1.cases.create_case_database", return_value="测试案件_ABCDE"), \
             patch("backend.api.v1.cases.initialize_case_database_schema", create=True) as init_schema, \
             patch.dict(sys.modules, {"backend.tasks.case_tasks": fake_task_module}):
            response = cases.create_case(case_data, current_user=current_user, db=db)

        self.assertEqual(response["code"], 200)
        init_schema.assert_called_once_with("测试案件_ABCDE", "ABCDE")
        fake_task_module.initialize_case_database_task.delay.assert_not_called()


if __name__ == "__main__":
    unittest.main()
