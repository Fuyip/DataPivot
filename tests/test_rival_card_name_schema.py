from pathlib import Path
import re
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASE_TEMPLATE_PATH = PROJECT_ROOT / "sql" / "schema" / "case_template.sql"
FX_TEST_SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema" / "fx_test_schema.sql"

TARGET_TABLES = [
    "bank_all_statements",
    "bank_all_statements_lastest",
    "bank_all_statements_tmp",
    "bank_all_statements_turn",
    "bank_all_statements_with_info",
    "bank_statements",
    "bank_statements_turn",
]


def extract_create_statement(sql_text: str, table_name: str) -> str:
    pattern = re.compile(
        rf"CREATE TABLE `{table_name}` \((.*?)\) ENGINE=",
        re.DOTALL,
    )
    match = pattern.search(sql_text)
    if not match:
        raise AssertionError(f"missing CREATE TABLE for {table_name}")
    return match.group(1)


class RivalCardNameSchemaTest(unittest.TestCase):
    def test_case_template_uses_varchar_255_for_rival_card_name(self):
        template_sql = CASE_TEMPLATE_PATH.read_text(encoding="utf-8")

        for table_name in TARGET_TABLES:
            create_sql = extract_create_statement(template_sql, table_name)
            self.assertIn("`rival_card_name` varchar(255)", create_sql, table_name)

    def test_fx_test_schema_uses_varchar_255_for_rival_card_name(self):
        fx_test_schema_sql = FX_TEST_SCHEMA_PATH.read_text(encoding="utf-8")

        for table_name in TARGET_TABLES:
            create_sql = extract_create_statement(fx_test_schema_sql, table_name)
            self.assertIn("`rival_card_name` varchar(255)", create_sql, table_name)


if __name__ == "__main__":
    unittest.main()
