import argparse
import csv
import datetime as dt
import re
from collections import defaultdict

from sqlalchemy import text

from database import engine

try:
    from pypinyin import lazy_pinyin
except Exception:
    lazy_pinyin = None


def normalize_key(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "", str(value)).lower()


def quote_ident(name: str) -> str:
    # 仅允许常见表名/列名字符，避免 SQL 注入。
    if not re.fullmatch(r"[0-9a-zA-Z_\u4e00-\u9fff]+", name or ""):
        raise ValueError(f"非法标识符: {name}")
    return f"`{name}`"


def has_chinese(s: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", s or ""))


def to_name_pinyin(value: str) -> str:
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    if has_chinese(s) and lazy_pinyin is not None:
        chars = []
        for ch in s:
            if "\u4e00" <= ch <= "\u9fff":
                chars.extend(lazy_pinyin(ch))
            elif ch.isalnum():
                chars.append(ch.lower())
        return re.sub(r"[^0-9a-z]+", "", "".join(chars).lower())

    return re.sub(r"[^0-9a-z]+", "", s.lower())


def normalize_birthdate(value) -> str:
    if value is None:
        return ""

    if isinstance(value, (dt.date, dt.datetime)):
        return value.strftime("%Y%m%d")

    s = str(value).strip()
    if not s:
        return ""

    # 常见 datetime 字符串
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(s, fmt).strftime("%Y%m%d")
        except ValueError:
            pass

    digits = re.sub(r"\D", "", s)
    if len(digits) >= 8:
        candidate = digits[:8]
        try:
            dt.datetime.strptime(candidate, "%Y%m%d")
            return candidate
        except ValueError:
            return ""

    return ""


def extract_birth_from_id(id_number: str) -> str:
    if id_number is None:
        return ""
    s = re.sub(r"\s+", "", str(id_number)).upper()
    s = re.sub(r"[^0-9X]", "", s)

    if len(s) == 18 and re.fullmatch(r"\d{17}[0-9X]", s):
        candidate = s[6:14]
    elif len(s) == 15 and re.fullmatch(r"\d{15}", s):
        candidate = "19" + s[6:12]
    else:
        return ""

    try:
        dt.datetime.strptime(candidate, "%Y%m%d")
        return candidate
    except ValueError:
        return ""


def get_table_columns(table_name: str) -> list[str]:
    sql = text(
        """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql, {"table_name": table_name}).fetchall()
    return [str(r[0]) for r in rows]


def pick_column(columns: list[str], candidates: list[str]) -> str | None:
    norm_map = {normalize_key(c): c for c in columns}
    for cand in candidates:
        key = normalize_key(cand)
        if key in norm_map:
            return norm_map[key]

    # 兜底：包含匹配
    norm_cols = [(normalize_key(c), c) for c in columns]
    for cand in candidates:
        key = normalize_key(cand)
        for col_key, col_name in norm_cols:
            if key and key in col_key:
                return col_name
    return None


def fetch_person_rows(table_name: str, name_col: str, id_col: str) -> list[dict]:
    sql = text(
        f"SELECT {quote_ident(name_col)} AS name_value, {quote_ident(id_col)} AS id_value "
        f"FROM {quote_ident(table_name)}"
    )
    with engine.connect() as conn:
        return conn.execute(sql).mappings().all()


def fetch_visa_rows(table_name: str) -> list[dict]:
    sql = text(f"SELECT * FROM {quote_ident(table_name)}")
    with engine.connect() as conn:
        return conn.execute(sql).mappings().all()


def write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="根据人员总体归纳姓名拼音 + 身份证出生日期，匹配签证表姓名 + 出生日期并输出签证信息"
    )
    parser.add_argument("--person-table", default="人员总体归纳", help="人员总体表名")
    parser.add_argument("--visa-table", default="签证表", help="签证表表名")
    parser.add_argument("--output", default="data/签证表匹配结果.csv", help="输出 CSV 路径")
    args = parser.parse_args()

    person_columns = get_table_columns(args.person_table)
    if not person_columns:
        raise RuntimeError(f"未找到人员表: {args.person_table}")

    visa_columns = get_table_columns(args.visa_table)
    if not visa_columns:
        raise RuntimeError(f"未找到签证表: {args.visa_table}")

    person_name_col = pick_column(person_columns, ["姓名", "中文姓名", "人员姓名", "姓名中文"])
    person_id_col = pick_column(person_columns, ["身份证号", "身份证号码", "身份证", "证件号", "公民身份号码"])

    visa_name_col = pick_column(visa_columns, ["姓名", "英文姓名", "name", "申请人姓名", "护照姓名"])
    visa_birth_col = pick_column(visa_columns, ["出生日期", "出生年月日", "生日", "dob", "dateofbirth"])

    missing = []
    if not person_name_col:
        missing.append("人员表姓名列")
    if not person_id_col:
        missing.append("人员表身份证列")
    if not visa_name_col:
        missing.append("签证表姓名列")
    if not visa_birth_col:
        missing.append("签证表出生日期列")

    if missing:
        raise RuntimeError("字段识别失败: " + ", ".join(missing))

    person_rows = fetch_person_rows(args.person_table, person_name_col, person_id_col)
    visa_rows = fetch_visa_rows(args.visa_table)

    person_index = defaultdict(list)
    for row in person_rows:
        raw_name = row.get("name_value")
        raw_id = row.get("id_value")

        name_py = to_name_pinyin(raw_name)
        birth = extract_birth_from_id(raw_id)
        if not name_py or not birth:
            continue

        person_index[(name_py, birth)].append(
            {
                "人员姓名": "" if raw_name is None else str(raw_name),
                "人员身份证号": "" if raw_id is None else str(raw_id),
                "人员姓名拼音": name_py,
                "人员出生日期": birth,
            }
        )

    matched_rows = []
    for visa in visa_rows:
        visa_name = visa.get(visa_name_col)
        visa_birth = visa.get(visa_birth_col)

        visa_name_py = to_name_pinyin(visa_name)
        visa_birth_norm = normalize_birthdate(visa_birth)

        if not visa_name_py or not visa_birth_norm:
            continue

        matches = person_index.get((visa_name_py, visa_birth_norm), [])
        for m in matches:
            out = {k: ("" if v is None else str(v)) for k, v in visa.items()}
            out["匹配姓名拼音"] = visa_name_py
            out["匹配出生日期"] = visa_birth_norm
            out.update(m)
            matched_rows.append(out)

    extra_cols = ["匹配姓名拼音", "匹配出生日期", "人员姓名", "人员身份证号", "人员姓名拼音", "人员出生日期"]
    output_columns = visa_columns + [c for c in extra_cols if c not in visa_columns]

    write_csv(args.output, matched_rows, output_columns)

    print(f"人员总记录: {len(person_rows)}")
    print(f"签证总记录: {len(visa_rows)}")
    print(f"匹配结果数: {len(matched_rows)}")
    print(f"输出文件: {args.output}")
    print(f"字段映射: 人员姓名={person_name_col}, 人员身份证={person_id_col}, 签证姓名={visa_name_col}, 签证出生日期={visa_birth_col}")


if __name__ == "__main__":
    main()
