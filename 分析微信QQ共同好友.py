import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

from sqlalchemy import text

from database import engine

EXCLUDED_ACCOUNTS = {
    "fmessage",
    "medianote",
    "weixin",
    "floatbottle",
    "qmessage",
    "qqmail",
    "qqsync",
    "filehelper",
    "mcdonalds888",
    "tmessage",
    "weibo"
}

EXCLUDED_ACCOUNTS_NORM = {re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "", x.lower()) for x in EXCLUDED_ACCOUNTS}


def normalize_key(value) -> str:
    if value is None:
        return ""
    s = str(value).strip().lower()
    if not s:
        return ""
    return re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "", s)


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
        c = norm_map.get(normalize_key(cand))
        if c:
            return c
    return None


def pick_source_columns(columns: list[str]) -> list[str]:
    picked = []
    for col in columns:
        c = normalize_key(col)
        if "来源" in c and "身份证" not in c:
            picked.append(col)
    return picked


def quote_col(col: str) -> str:
    return f"`{col.replace('`', '``')}`"


def is_excluded_account(value: str) -> bool:
    if value is None:
        return False
    raw = str(value).strip().lower()
    if not raw:
        return False
    if raw in EXCLUDED_ACCOUNTS:
        return True
    return normalize_key(raw) in EXCLUDED_ACCOUNTS_NORM


def build_person_map() -> dict[str, dict[str, str]]:
    table = "人员总体归纳"
    cols = get_table_columns(table)
    account_col = pick_column(cols, ["账号"])
    name_col = pick_column(cols, ["姓名", "人员姓名", "名字", "name"])
    id_card_col = pick_column(cols, ["身份证号", "身份证号码", "公民身份号码", "证件号"])
    source_cols = pick_source_columns(cols)

    if not account_col:
        raise RuntimeError("表 `人员总体归纳` 未识别到 `账号` 列")

    select_items = [f"{quote_col(account_col)} AS account"]
    if name_col:
        select_items.append(f"{quote_col(name_col)} AS person_name")
    else:
        select_items.append("NULL AS person_name")
    if id_card_col:
        select_items.append(f"{quote_col(id_card_col)} AS id_card")
    else:
        select_items.append("NULL AS id_card")
    for i, col in enumerate(source_cols):
        select_items.append(f"{quote_col(col)} AS source_{i}")

    sql = text(f"SELECT {', '.join(select_items)} FROM `{table}`")
    out = {}
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()
    for r in rows:
        account_raw = r.get("account")
        account_norm = normalize_key(account_raw)
        if not account_norm:
            continue
        person_name = str(r.get("person_name")).strip() if r.get("person_name") is not None else ""
        id_card_raw = r.get("id_card")
        id_card = str(id_card_raw).strip().upper() if id_card_raw is not None else ""
        sources = []
        for i in range(len(source_cols)):
            v = r.get(f"source_{i}")
            if v is None:
                continue
            s = str(v).strip()
            if s:
                sources.append(s)

        if account_norm not in out:
            out[account_norm] = {
                "account": str(account_raw).strip() if account_raw is not None else "",
                "person_name": person_name,
                "id_card": id_card,
                "account_source": " | ".join(sorted(set(sources))),
            }
        else:
            # 同账号多行时补充信息
            if not out[account_norm]["person_name"] and person_name:
                out[account_norm]["person_name"] = person_name
            if not out[account_norm]["id_card"] and id_card:
                out[account_norm]["id_card"] = id_card
            if sources:
                merged = set(filter(None, out[account_norm]["account_source"].split(" | ")))
                merged.update(sources)
                out[account_norm]["account_source"] = " | ".join(sorted(merged))
    return out


def load_friend_rows(
    table_name: str,
    subject_col: str,
    friend_id_col: str | None,
    friend_name_col: str | None,
    platform: str,
) -> list[dict]:
    select_items = [f"{quote_col(subject_col)} AS subject_account"]
    if friend_id_col:
        select_items.append(f"{quote_col(friend_id_col)} AS friend_id")
    else:
        select_items.append("NULL AS friend_id")
    if friend_name_col:
        select_items.append(f"{quote_col(friend_name_col)} AS friend_name")
    else:
        select_items.append("NULL AS friend_name")

    sql = text(f"SELECT {', '.join(select_items)} FROM `{table_name}`")
    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    records = []
    for r in rows:
        subject_account = str(r.get("subject_account")).strip() if r.get("subject_account") is not None else ""
        friend_id = str(r.get("friend_id")).strip() if r.get("friend_id") is not None else ""
        friend_name = str(r.get("friend_name")).strip() if r.get("friend_name") is not None else ""
        if not subject_account:
            continue
        if is_excluded_account(subject_account):
            continue
        if friend_id and is_excluded_account(friend_id):
            continue
        if platform == "微信" and subject_account.lower().startswith("gh_"):
            continue
        if platform == "微信" and friend_id.lower().startswith("gh_"):
            # 过滤公众号类微信号（gh_开头）
            continue
        if not friend_id and not friend_name:
            continue
        records.append(
            {
                "platform": platform,
                "subject_account": subject_account,
                "subject_source": f"{platform}主体",
                "friend_id": friend_id,
                "friend_name": friend_name,
            }
        )
    return records


def friend_key(record: dict) -> str:
    # 优先使用好友账号类字段；否则回退到好友名/备注
    key = normalize_key(record.get("friend_id", ""))
    if key:
        return f"id:{key}"
    name_key = normalize_key(record.get("friend_name", ""))
    if name_key:
        return f"name:{name_key}"
    return ""


def friend_display(record: dict) -> str:
    fid = (record.get("friend_id") or "").strip()
    fname = (record.get("friend_name") or "").strip()
    if fid and fname:
        return f"{fname}({fid})"
    return fname or fid


def save_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build_person_mutual_rows(all_rows: list[dict], person_map: dict[str, dict[str, str]]) -> list[dict]:
    directed = defaultdict(list)
    for r in all_rows:
        a = normalize_key(r.get("subject_account", ""))
        b = normalize_key(r.get("friend_id", ""))
        platform = r.get("platform", "")
        if not a or not b or not platform:
            continue
        if a == b:
            continue
        if a not in person_map or b not in person_map:
            continue
        directed[(platform, a, b)].append(r)

    rows = []
    seen = set()
    for platform, a, b in directed.keys():
        pair_key = (platform, min(a, b), max(a, b))
        if pair_key in seen:
            continue
        seen.add(pair_key)
        reverse_exists = (platform, b, a) in directed

        a_info = person_map.get(a, {})
        b_info = person_map.get(b, {})
        a_to_b = directed.get((platform, a, b), [])
        b_to_a = directed.get((platform, b, a), [])

        a_remark = " | ".join(sorted({(x.get("friend_name") or "").strip() for x in a_to_b if (x.get("friend_name") or "").strip()}))
        b_remark = " | ".join(sorted({(x.get("friend_name") or "").strip() for x in b_to_a if (x.get("friend_name") or "").strip()}))

        rows.append(
            {
                "平台": platform,
                "关系类型": "双向" if reverse_exists else "单向",
                "账号A": a_info.get("account", a),
                "姓名A(人员总体归纳)": a_info.get("person_name", ""),
                "账号A来源(人员总体归纳)": a_info.get("account_source", ""),
                "账号B": b_info.get("account", b),
                "姓名B(人员总体归纳)": b_info.get("person_name", ""),
                "账号B来源(人员总体归纳)": b_info.get("account_source", ""),
                "A备注B": a_remark,
                "B备注A": b_remark,
                "A->B记录数": len(a_to_b),
                "B->A记录数": len(b_to_a),
            }
        )

    rows.sort(key=lambda x: (x["平台"], x["关系类型"], x["账号A"], x["账号B"]))
    return rows


def save_excel_report(report_path: Path, summary_rows: list[dict], detail_rows: list[dict], mutual_rows: list[dict]) -> None:
    try:
        import pandas as pd
    except Exception as e:
        raise RuntimeError(f"生成Excel报告失败：未安装 pandas（{e}）")

    report_path.parent.mkdir(parents=True, exist_ok=True)

    summary_cols = ["共同好友键", "共同好友展示", "平台分布", "是否跨平台", "关联主体数", "命中记录数", "微信侧被备注明细", "关联主体明细"]
    detail_cols = [
        "共同好友键",
        "共同好友展示",
        "平台",
        "关联主体来源",
        "主体账号",
        "主体姓名(人员总体归纳)",
        "主体账号来源(人员总体归纳)",
        "好友账号",
        "好友名称/备注",
    ]
    mutual_cols = [
        "平台",
        "关系类型",
        "账号A",
        "姓名A(人员总体归纳)",
        "账号A来源(人员总体归纳)",
        "账号B",
        "姓名B(人员总体归纳)",
        "账号B来源(人员总体归纳)",
        "A备注B",
        "B备注A",
        "A->B记录数",
        "B->A记录数",
    ]

    summary_df = pd.DataFrame(summary_rows, columns=summary_cols)
    detail_df = pd.DataFrame(detail_rows, columns=detail_cols)
    mutual_df = pd.DataFrame(mutual_rows, columns=mutual_cols)

    with pd.ExcelWriter(report_path) as writer:
        summary_df.to_excel(writer, sheet_name="共同好友汇总", index=False)
        detail_df.to_excel(writer, sheet_name="共同好友明细", index=False)
        mutual_df.to_excel(writer, sheet_name="人员总体归纳互为好友", index=False)


def parse_args():
    parser = argparse.ArgumentParser(description="查找微信/QQ共同好友，并标明关联主体及来源")
    parser.add_argument(
        "--output",
        default="data/微信QQ共同好友_汇总.csv",
        help="共同好友汇总输出路径",
    )
    parser.add_argument(
        "--detail-output",
        default="data/微信QQ共同好友_明细.csv",
        help="共同好友明细输出路径",
    )
    parser.add_argument(
        "--min-subjects",
        type=int,
        default=2,
        help="至少关联多少个不同主体才算共同好友，默认 2",
    )
    parser.add_argument(
        "--report-output",
        default="data/微信QQ共同好友_汇总报告.xlsx",
        help="Excel汇总报告输出路径（包含多个选项卡）",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    person_map = build_person_map()

    wx_cols = get_table_columns("29-微信好友")
    qq_cols = get_table_columns("29-qq好友")

    wx_subject_col = pick_column(wx_cols, ["主体微信号"])
    qq_subject_col = pick_column(qq_cols, ["主体qq号", "主体QQ号"])
    if not wx_subject_col:
        raise RuntimeError("表 `29-微信好友` 未识别到 `主体微信号` 列")
    if not qq_subject_col:
        raise RuntimeError("表 `29-qq好友` 未识别到 `主体qq号` 列")

    wx_friend_id_col = pick_column(wx_cols, ["好友微信号", "好友账号", "微信号", "对方微信号", "好友id", "好友ID"])
    qq_friend_id_col = pick_column(qq_cols, ["好友qq号", "好友QQ号", "好友账号", "qq号", "QQ号", "对方QQ号", "好友id", "好友ID"])
    wx_friend_name_col = pick_column(wx_cols, ["好友备注", "好友昵称", "昵称", "名称", "好友名"])
    qq_friend_name_col = pick_column(qq_cols, ["好友备注", "好友昵称", "昵称", "名称", "好友名"])

    if not wx_friend_id_col and not wx_friend_name_col:
        raise RuntimeError("表 `29-微信好友` 未识别到可用好友标识列（账号或备注/昵称）")
    if not qq_friend_id_col and not qq_friend_name_col:
        raise RuntimeError("表 `29-qq好友` 未识别到可用好友标识列（账号或备注/昵称）")

    wx_rows = load_friend_rows("29-微信好友", wx_subject_col, wx_friend_id_col, wx_friend_name_col, "微信")
    qq_rows = load_friend_rows("29-qq好友", qq_subject_col, qq_friend_id_col, qq_friend_name_col, "QQ")
    all_rows = wx_rows + qq_rows

    grouped = defaultdict(list)
    for row in all_rows:
        k = friend_key(row)
        if not k:
            continue
        grouped[k].append(row)

    summary_rows = []
    detail_rows = []

    for k, rows in grouped.items():
        # Group by ID card if available, otherwise by account
        subject_identities = set()
        for r in rows:
            subject_norm = normalize_key(r["subject_account"])
            if not subject_norm:
                continue
            person = person_map.get(subject_norm, {})
            id_card = person.get("id_card", "").strip()
            if id_card:
                subject_identities.add(f"id:{id_card}")
            else:
                subject_identities.add(f"account:{subject_norm}")

        if len(subject_identities) < max(1, args.min_subjects):
            continue

        platforms = sorted({r["platform"] for r in rows})
        is_cross_platform = "是" if len(platforms) >= 2 else "否"

        # Group subjects by ID card for display
        id_card_groups = defaultdict(list)
        ungrouped_subjects = []
        subject_seen = set()

        for r in rows:
            subject_norm = normalize_key(r["subject_account"])
            if not subject_norm:
                continue
            subject_key = (r["platform"], subject_norm)
            if subject_key in subject_seen:
                continue
            subject_seen.add(subject_key)

            person = person_map.get(subject_norm, {})
            id_card = person.get("id_card", "").strip()

            subject_info = {
                "platform": r['platform'],
                "account": r['subject_account'],
                "person_name": person.get('person_name', ''),
                "account_source": person.get('account_source', '')
            }

            if id_card:
                id_card_groups[id_card].append(subject_info)
            else:
                ungrouped_subjects.append(subject_info)

        # Format output with grouping indicators
        subject_labels = []
        for id_card, subjects in id_card_groups.items():
            if len(subjects) > 1:
                # Multiple accounts for same ID card
                accounts_str = " + ".join([f"{s['platform']}:{s['account']}" for s in subjects])
                label = f"[同一身份证:{id_card[:6]}***] {accounts_str}"
                if subjects[0]['person_name']:
                    label += f" | 姓名:{subjects[0]['person_name']}"
            else:
                # Single account with ID card
                s = subjects[0]
                label = f"{s['platform']}:{s['account']}"
                if s['person_name']:
                    label += f" | 姓名:{s['person_name']}"
                if s['account_source']:
                    label += f" | 账号来源:{s['account_source']}"
            subject_labels.append(label)

        for s in ungrouped_subjects:
            label = f"{s['platform']}:{s['account']}"
            if s['person_name']:
                label += f" | 姓名:{s['person_name']}"
            if s['account_source']:
                label += f" | 账号来源:{s['account_source']}"
            subject_labels.append(label)

        sample_display = friend_display(rows[0]) if rows else ""
        wx_remark_parts = []
        wx_seen = set()
        for r in rows:
            if r["platform"] != "微信":
                continue
            subject = (r.get("subject_account") or "").strip()
            remark = (r.get("friend_name") or "").strip()
            if not subject or not remark:
                continue
            item = (subject, remark)
            if item in wx_seen:
                continue
            wx_seen.add(item)
            wx_remark_parts.append(f"{subject}:{remark}")

        summary_rows.append(
            {
                "共同好友键": k,
                "共同好友展示": sample_display,
                "平台分布": " | ".join(platforms),
                "是否跨平台": is_cross_platform,
                "关联主体数": len(subject_identities),
                "命中记录数": len(rows),
                "微信侧被备注明细": " || ".join(wx_remark_parts),
                "关联主体明细": " || ".join(subject_labels),
            }
        )

        for r in rows:
            subject_norm = normalize_key(r["subject_account"])
            person = person_map.get(subject_norm, {})
            detail_rows.append(
                {
                    "共同好友键": k,
                    "共同好友展示": friend_display(r),
                    "平台": r["platform"],
                    "关联主体来源": r["subject_source"],
                    "主体账号": r["subject_account"],
                    "主体姓名(人员总体归纳)": person.get("person_name", ""),
                    "主体账号来源(人员总体归纳)": person.get("account_source", ""),
                    "好友账号": r["friend_id"],
                    "好友名称/备注": r["friend_name"],
                }
            )

    summary_rows.sort(key=lambda x: (-x["关联主体数"], -x["命中记录数"], x["共同好友键"]))
    detail_rows.sort(key=lambda x: (x["共同好友键"], x["平台"], x["主体账号"]))
    mutual_rows = build_person_mutual_rows(all_rows, person_map)

    save_csv(
        Path(args.output),
        summary_rows,
        ["共同好友键", "共同好友展示", "平台分布", "是否跨平台", "关联主体数", "命中记录数", "微信侧被备注明细", "关联主体明细"],
    )
    save_csv(
        Path(args.detail_output),
        detail_rows,
        [
            "共同好友键",
            "共同好友展示",
            "平台",
            "关联主体来源",
            "主体账号",
            "主体姓名(人员总体归纳)",
            "主体账号来源(人员总体归纳)",
            "好友账号",
            "好友名称/备注",
        ],
    )
    save_excel_report(Path(args.report_output), summary_rows, detail_rows, mutual_rows)

    print("处理完成")
    print(f"总记录: {len(all_rows)}")
    print(f"共同好友数: {len(summary_rows)}")
    print(f"人员总体归纳互为好友对数: {len(mutual_rows)}")
    print(f"汇总文件: {Path(args.output).resolve()}")
    print(f"明细文件: {Path(args.detail_output).resolve()}")
    print(f"汇总报告: {Path(args.report_output).resolve()}")


if __name__ == "__main__":
    main()
