from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASE_TEMPLATE_PATH = PROJECT_ROOT / "sql" / "schema" / "case_template.sql"
CASE_SERVICE_PATH = PROJECT_ROOT / "backend" / "services" / "case_service.py"
FX_TEST_SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema" / "fx_test_schema.sql"


class CaseTemplateBankInfoChangeTableTest(unittest.TestCase):
    def test_case_template_includes_bank_info_change_requests_table(self):
        template_sql = CASE_TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("CREATE TABLE `bank_info_change_requests`", template_sql)

    def test_case_service_verifies_bank_info_change_requests_table(self):
        case_service_source = CASE_SERVICE_PATH.read_text(encoding="utf-8")

        self.assertIn("'bank_info_change_requests'", case_service_source)

    def test_fx_test_schema_stays_aligned_with_case_template(self):
        fx_test_schema_sql = FX_TEST_SCHEMA_PATH.read_text(encoding="utf-8")

        self.assertIn("CREATE TABLE `bank_info_change_requests`", fx_test_schema_sql)


if __name__ == "__main__":
    unittest.main()
