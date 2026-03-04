import argparse
import csv
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from sqlalchemy import text

from database import engine

try:
    from pypinyin import lazy_pinyin
except Exception:
    lazy_pinyin = None


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    s = str(value).strip().lower()
    if not s:
        return ""
    # 仅保留中文、字母、数字
    s = re.sub(r"[^\u4e00-\u9fff0-9a-zA-Z]+", "", s)
    return s


def to_pinyin(value: str) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return ""

    if lazy_pinyin is None:
        return cleaned

    out = []
    for ch in cleaned:
        if "\u4e00" <= ch <= "\u9fff":
            out.extend(lazy_pinyin(ch))
        else:
            out.append(ch)
    return "".join(out)


def normalize_key(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "", str(value)).lower()


def get_table_columns(table_name: str) -> list[str]:
    sql = text(
        """
        SELECT COLUMN_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = :table_name
        ORDER BY ORDINAL_POSITION
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql, {"table_name": table_name}).fetchall()
    return [str(row[0]) for row in rows if row and row[0] is not None]


def pick_column(columns: list[str], candidates: list[str]) -> str | None:
    norm_map = {normalize_key(c): c for c in columns}
    for cand in candidates:
        target = normalize_key(cand)
        if target in norm_map:
            return norm_map[target]
    return None


def pick_columns_by_keywords(
    columns: list[str],
    include_keywords: list[str],
    exclude_keywords: list[str] | None = None,
) -> list[str]:
    exclude_keywords = exclude_keywords or []
    picked = []
    for col in columns:
        norm_col = normalize_key(col)
        if not norm_col:
            continue
        if any(k in norm_col for k in include_keywords) and not any(k in norm_col for k in exclude_keywords):
            picked.append(col)
    return picked


def fetch_records(table_name: str, remark_col: str, account_col: str | None) -> list[dict]:
    if account_col:
        sql = text(
            f"SELECT `{remark_col}` AS remark, `{account_col}` AS account "
            f"FROM `{table_name}` "
            f"WHERE `{remark_col}` IS NOT NULL AND TRIM(`{remark_col}`) != ''"
        )
    else:
        sql = text(
            f"SELECT `{remark_col}` AS remark, NULL AS account "
            f"FROM `{table_name}` "
            f"WHERE `{remark_col}` IS NOT NULL AND TRIM(`{remark_col}`) != ''"
        )

    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    out = []
    for row in rows:
        remark = str(row["remark"]).strip() if row["remark"] is not None else ""
        account = str(row["account"]).strip() if row["account"] is not None else ""
        if remark:
            out.append({"remark": remark, "account": account})
    return out


def fetch_nicknames(table_name: str, nickname_col: str) -> list[str]:
    sql = text(
        f"SELECT `{nickname_col}` FROM `{table_name}` "
        f"WHERE `{nickname_col}` IS NOT NULL AND TRIM(`{nickname_col}`) != ''"
    )
    with engine.connect() as conn:
        rows = conn.execute(sql).fetchall()
    return [str(row[0]) for row in rows if row and row[0] is not None]


def build_person_profile_map_by_account() -> dict[str, dict[str, str]]:
    table_name = "人员总体归纳"
    columns = get_table_columns(table_name)

    account_col = pick_column(columns, ["账号"])
    source_cols = pick_columns_by_keywords(columns, include_keywords=["来源"], exclude_keywords=["身份证"])
    name_col = pick_column(columns, ["姓名", "名字", "人员姓名"])
    id_col = pick_column(columns, ["身份证号", "身份证号码", "公民身份号码", "证件号码", "证件号"])

    if not account_col or not source_cols:
        return {}

    select_cols = []
    select_cols.append(f"`{account_col}` AS account")
    if name_col:
        select_cols.append(f"`{name_col}` AS person_name")
    else:
        select_cols.append("NULL AS person_name")
    if id_col:
        select_cols.append(f"`{id_col}` AS id_number")
    else:
        select_cols.append("NULL AS id_number")
    for i, col in enumerate(source_cols):
        select_cols.append(f"`{col}` AS source_{i}")

    sql = text(f"SELECT {', '.join(select_cols)} FROM `{table_name}`")
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    account_source_set = defaultdict(set)
    account_name_set = defaultdict(set)
    account_id_set = defaultdict(set)

    for row in rows:
        account = normalize_key(row.get("account"))
        if not account:
            continue

        sources = []
        for i in range(len(source_cols)):
            v = row.get(f"source_{i}")
            if v is None:
                continue
            v = str(v).strip()
            if v:
                sources.append(v)

        if not sources:
            continue

        person_name = str(row.get("person_name")).strip() if row.get("person_name") is not None else ""
        id_number = str(row.get("id_number")).strip() if row.get("id_number") is not None else ""

        for source in sources:
            account_source_set[account].add(source)
        if person_name:
            account_name_set[account].add(person_name)
        if id_number:
            account_id_set[account].add(id_number)

    profile_map = {}
    for account, sources in account_source_set.items():
        profile_map[account] = {
            "账号来源": " | ".join(sorted(sources)),
            "人员姓名": " | ".join(sorted(account_name_set.get(account, set()))),
            "身份证": " | ".join(sorted(account_id_set.get(account, set()))),
        }
    return profile_map


def prepare_remarks(rows: list[dict], platform: str, profile_map: dict[str, dict[str, str]]) -> list[dict]:
    out = []
    seen = set()
    for row in rows:
        raw = row["remark"]
        account = row.get("account", "") or ""
        py = to_pinyin(raw)
        if not py:
            continue
        account_key = normalize_key(account)
        profile = profile_map.get(account_key, {})
        key = (raw, py, platform, account_key)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "platform": platform,
                "remark": raw,
                "remark_pinyin": py,
                "account": account,
                "account_source": profile.get("账号来源", ""),
                "person_name": profile.get("人员姓名", ""),
                "id_number": profile.get("身份证", ""),
            }
        )
    return out


def score_pair(nickname_py: str, remark_py: str) -> float:
    if not nickname_py or not remark_py:
        return 0.0

    if nickname_py in remark_py or remark_py in nickname_py:
        return 100.0

    return SequenceMatcher(None, nickname_py, remark_py).ratio() * 100


def is_strong_hit(nickname_py: str, remark_py: str) -> bool:
    if not nickname_py or not remark_py:
        return False
    return nickname_py in remark_py or remark_py in nickname_py


def match_nicknames(
    nicknames: list[str],
    remarks: list[dict],
    threshold: float,
    top_k: int,
) -> list[dict]:
    results = []

    # 外号也去重，避免重复计算
    uniq_nicknames = []
    seen_nick = set()
    for raw in nicknames:
        py = to_pinyin(raw)
        if not py:
            continue
        key = (raw, py)
        if key in seen_nick:
            continue
        seen_nick.add(key)
        uniq_nicknames.append({"nickname": raw, "nickname_pinyin": py})

    for item in uniq_nicknames:
        nickname = item["nickname"]
        nickname_py = item["nickname_pinyin"]

        candidates = []
        for r in remarks:
            # 长度差太大时先跳过，减少无意义计算
            length_gap = abs(len(r["remark_pinyin"]) - len(nickname_py))
            if length_gap > max(8, len(nickname_py) * 2):
                continue

            score = score_pair(nickname_py, r["remark_pinyin"])
            if score >= threshold:
                strong_hit = is_strong_hit(nickname_py, r["remark_pinyin"])
                candidates.append(
                    {
                        "外号": nickname,
                        "外号拼音": nickname_py,
                        "来源": r["platform"],
                        "主体账号": r["account"],
                        "账号来源": r["account_source"],
                        "人员姓名": r["person_name"],
                        "身份证": r["id_number"],
                        "好友备注": r["remark"],
                        "好友备注拼音": r["remark_pinyin"],
                        "相似度": round(score, 2),
                        "_strong_hit": strong_hit,
                    }
                )

        candidates.sort(key=lambda x: x["相似度"], reverse=True)
        if not candidates:
            results.append(
                {
                    "外号": nickname,
                    "外号拼音": nickname_py,
                    "来源": "",
                    "主体账号": "",
                    "账号来源": "",
                    "人员姓名": "",
                    "身份证": "",
                    "好友备注": "",
                    "好友备注拼音": "",
                    "相似度": 0,
                    "_strong_hit": False,
                }
            )
        else:
            strong_hits = [x for x in candidates if x["_strong_hit"]]
            weak_hits = [x for x in candidates if not x["_strong_hit"]]
            results.extend(strong_hits)
            results.extend(weak_hits[:top_k])

    return results


def save_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["外号", "外号拼音", "来源", "主体账号", "账号来源", "人员姓名", "身份证", "好友备注", "好友备注拼音", "相似度"]
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        cleaned_rows = []
        for row in rows:
            clean = dict(row)
            clean.pop("_strong_hit", None)
            cleaned_rows.append(clean)
        writer.writerows(cleaned_rows)


def parse_args():
    parser = argparse.ArgumentParser(description="将 tg-外号 的外号拼音与微信/QQ好友备注做模糊匹配")
    parser.add_argument("--threshold", type=float, default=72.0, help="模糊匹配阈值(0-100)，默认 72")
    parser.add_argument("--top-k", type=int, default=3, help="每个外号保留前 K 个命中结果，默认 3")
    parser.add_argument(
        "--output",
        type=str,
        default="data/tg外号_好友备注拼音匹配结果.csv",
        help="结果 CSV 路径",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("正在读取数据库数据...")
    tg_nicknames = fetch_nicknames("tg-外号", "外号")

    wx_columns = get_table_columns("29-微信好友")
    qq_columns = get_table_columns("29-qq好友")

    wx_remark_col = pick_column(wx_columns, ["好友备注"])
    qq_remark_col = pick_column(qq_columns, ["好友备注"])
    wx_account_col = pick_column(wx_columns, ["主体微信号"])
    qq_account_col = pick_column(qq_columns, ["主体qq号", "主体QQ号"])

    if not wx_remark_col or not qq_remark_col:
        raise RuntimeError("未找到 29-微信好友 或 29-qq好友 的 `好友备注` 列")
    if not wx_account_col:
        raise RuntimeError("未找到 29-微信好友 的 `主体微信号` 列")
    if not qq_account_col:
        raise RuntimeError("未找到 29-qq好友 的 `主体qq号` 列")

    wx_records = fetch_records("29-微信好友", wx_remark_col, wx_account_col)
    qq_records = fetch_records("29-qq好友", qq_remark_col, qq_account_col)

    profile_map = build_person_profile_map_by_account()
    print(
        f"账号画像映射(人员总体归纳.账号): {len(profile_map)} 条 | "
        f"账号列: 微信[{wx_account_col or '未识别'}], QQ[{qq_account_col or '未识别'}]"
    )

    remarks = []
    remarks.extend(prepare_remarks(wx_records, "微信", profile_map))
    remarks.extend(prepare_remarks(qq_records, "QQ", profile_map))

    print(
        f"外号数: {len(tg_nicknames)} | 微信备注: {len(wx_records)} | QQ备注: {len(qq_records)} | "
        f"去重后备注: {len(remarks)}"
    )

    print("正在进行拼音模糊匹配...")
    matched_rows = match_nicknames(
        nicknames=tg_nicknames,
        remarks=remarks,
        threshold=args.threshold,
        top_k=max(1, args.top_k),
    )

    out_path = Path(args.output)
    save_csv(matched_rows, out_path)

    # 统计命中率（按外号维度）
    hit_nick = set()
    all_nick = set()
    for row in matched_rows:
        all_nick.add(row["外号"])
        if row["相似度"] > 0:
            hit_nick.add(row["外号"])

    hit_count = len(hit_nick)
    total_count = len(all_nick)
    hit_rate = (hit_count / total_count * 100) if total_count else 0

    print("匹配完成")
    print(f"外号总数(去重后): {total_count}")
    print(f"命中外号数: {hit_count}")
    print(f"命中率: {hit_rate:.2f}%")
    print(f"结果文件: {out_path.resolve()}")


if __name__ == "__main__":
    main()
