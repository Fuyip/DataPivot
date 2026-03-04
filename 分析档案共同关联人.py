import argparse
import itertools
import json
import os
from collections import defaultdict

import pandas as pd
from sqlalchemy import text

from database import engine


PERSON_COL_CANDIDATES = [
    "姓名", "name", "人员姓名", "嫌疑人姓名", "旅客姓名", "入住人姓名",
    "身份证号", "身份证号码", "公民身份号码", "证件号码", "证件号", "护照号",
    "手机号", "手机号码", "联系电话", "电话",
]

NAME_COL_CANDIDATES = ["旅客中文名", "姓名", "人员姓名", "嫌疑人姓名", "旅客姓名", "入住人姓名", "中文名", "name"]

TYPE_KEYWORDS = {
    "同乘车": ["乘车", "车次", "列车", "航班", "机票", "动车", "火车", "铁路"],
    "同住宿": ["住宿", "酒店", "宾馆", "旅店", "入住", "同住", "民宿"],
    "同出入境": ["出入境", "口岸", "边检", "入境", "出境", "签证"],
}

EVENT_KEYWORDS = {
    "同乘车": ["车次", "航班", "班次", "出发", "到达", "日期", "时间", "座位", "站", "港"],
    "同住宿": ["酒店", "宾馆", "旅店", "民宿", "房间", "入住", "离店", "日期", "地址", "时间"],
    "同出入境": ["口岸", "边检", "入境", "出境", "日期", "时间", "证件类型", "签证"],
}

COMMON_EVENT_HINTS = ["时间", "日期", "地点", "地址", "编号", "单号", "记录号", "号", "类型"]

EXCLUDE_COLS = {"id", "ID", "序号", "主键"}
EXCLUDED_TABLES = {"档案_最高学历学位"}


def norm_str(v):
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in {"", "nan", "none", "null"}:
        return ""
    return s


def normalize_col_name(c):
    return str(c).strip().lower().replace(" ", "").replace("_", "")


def detect_relation_type(table_name):
    for relation_type, kws in TYPE_KEYWORDS.items():
        if any(k in table_name for k in kws):
            return relation_type
    return "其他关联"


def pick_person_cols(columns):
    cols = list(columns)
    normalized = {c: normalize_col_name(c) for c in cols}
    picked = []
    for cand in PERSON_COL_CANDIDATES:
        cand_norm = normalize_col_name(cand)
        for c, cn in normalized.items():
            if cn == cand_norm and c not in picked:
                picked.append(c)
    for c in cols:
        if c not in picked and any(k in c for k in ["姓名", "证件", "身份证", "手机", "电话", "护照"]):
            picked.append(c)
    return picked[:4]


def pick_primary_person_col(columns):
    person_cols = pick_person_cols(columns)
    if not person_cols:
        return None
    # 优先使用证件类字段作为唯一标识（支持“旅客证件号码”等带前缀字段）
    hard_priority_contains = ["身份证号", "身份证号码", "公民身份号码", "证件号码", "证件号", "护照号", "证件"]
    for kw in hard_priority_contains:
        for c in person_cols:
            if kw in c:
                return c

    priority = ["身份证号", "身份证号码", "公民身份号码", "证件号码", "证件号", "护照号", "手机号", "手机号码", "姓名", "name"]
    for p in priority:
        for c in person_cols:
            if normalize_col_name(c) == normalize_col_name(p):
                return c
    return person_cols[0]


def pick_name_col(columns):
    cols = list(columns)
    normalized = {c: normalize_col_name(c) for c in cols}
    for cand in NAME_COL_CANDIDATES:
        cand_norm = normalize_col_name(cand)
        for c, cn in normalized.items():
            if cn == cand_norm:
                return c
    # 兼容“旅客中文名”等变体
    for c in cols:
        if "中文名" in c:
            return c
    for c in cols:
        if "姓名" in c or normalize_col_name(c) == "name":
            return c
    return None


def pick_event_cols(columns, relation_type):
    cols = [c for c in columns if c not in EXCLUDE_COLS]
    person_cols = set(pick_person_cols(cols))
    candidate_cols = [c for c in cols if c not in person_cols]

    kws = EVENT_KEYWORDS.get(relation_type, [])
    event_cols = [c for c in candidate_cols if any(k in c for k in kws)]
    if len(event_cols) < 2:
        backup = [c for c in candidate_cols if any(k in c for k in COMMON_EVENT_HINTS)]
        event_cols.extend([c for c in backup if c not in event_cols])

    if len(event_cols) < 2:
        event_cols = candidate_cols[:4]

    return event_cols[:6]


def fetch_archive_tables():
    sql = text(
        """
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME LIKE '档案\\_%'
        ORDER BY TABLE_NAME
        """
    )
    with engine.connect() as conn:
        tables = [r[0] for r in conn.execute(sql).fetchall()]
    return [t for t in tables if t not in EXCLUDED_TABLES]


def fetch_table_columns(table_name):
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
        return [r[0] for r in conn.execute(sql, {"table_name": table_name}).fetchall()]


def quote_col(col):
    if col is None:
        raise ValueError("column name is None")
    return f"`{col.replace('`', '``')}`"


def load_rows(table_name, select_cols):
    cols_sql = ", ".join(quote_col(c) for c in select_cols)
    sql = f"SELECT {cols_sql} FROM `{table_name}`"
    return pd.read_sql(sql, engine)


def build_person_label(row, person_cols):
    parts = []
    for c in person_cols:
        v = norm_str(row.get(c, ""))
        if v:
            parts.append(f"{c}:{v}")
    return " | ".join(parts[:3]) if parts else ""


def event_key_from_row(row, event_cols):
    values = []
    for c in event_cols:
        v = norm_str(row.get(c, ""))
        if v:
            values.append(f"{c}={v}")
    if len(values) < 1:
        return ""
    return " ; ".join(values)


def analyze_table(table_name):
    relation_type = detect_relation_type(table_name)
    columns = fetch_table_columns(table_name)
    if not columns:
        return [], [], {"table_name": table_name, "status": "skip", "reason": "empty_columns"}

    primary_person_col = pick_primary_person_col(columns)
    name_col = pick_name_col(columns)
    person_cols = pick_person_cols(columns)
    event_cols = pick_event_cols(columns, relation_type)

    if not primary_person_col:
        return [], [], {"table_name": table_name, "status": "skip", "reason": "no_person_col"}
    if not event_cols:
        return [], [], {"table_name": table_name, "status": "skip", "reason": "no_event_col"}

    select_cols = [c for c in [primary_person_col, name_col] + person_cols + event_cols if c]
    select_cols = list(dict.fromkeys(select_cols))
    df = load_rows(table_name, select_cols)
    if df.empty:
        return [], [], {"table_name": table_name, "status": "skip", "reason": "empty_table"}

    df = df.fillna("")
    df["__person_id__"] = df[primary_person_col].map(norm_str)
    if name_col:
        df["__person_name__"] = df[name_col].map(norm_str)
    else:
        df["__person_name__"] = ""
    df["__person_key__"] = df["__person_id__"]
    df.loc[df["__person_key__"] == "", "__person_key__"] = df.loc[df["__person_key__"] == "", "__person_name__"]
    df["__person_name__"] = df.apply(
        lambda r: r["__person_name__"] if norm_str(r["__person_name__"]) else r["__person_key__"], axis=1
    )
    df["__person_label__"] = df.apply(lambda r: build_person_label(r, person_cols), axis=1)
    df["__event_key__"] = df.apply(lambda r: event_key_from_row(r, event_cols), axis=1)
    df = df[(df["__person_key__"] != "") & (df["__event_key__"] != "")]
    if df.empty:
        return [], [], {"table_name": table_name, "status": "skip", "reason": "no_valid_rows"}

    grouped_indices = df.groupby("__event_key__", dropna=False).groups
    if not grouped_indices:
        return [], [], {"table_name": table_name, "status": "ok", "groups": 0, "pairs": 0}

    event_details = []
    pair_records = []
    group_count = 0

    for event_key, idx in grouped_indices.items():
        sub = df.loc[idx, ["__person_key__", "__person_name__"]].copy()
        participants_map = {}
        for _, r in sub.iterrows():
            pkey = norm_str(r["__person_key__"])
            pname = norm_str(r["__person_name__"]) or pkey
            if not pkey:
                continue
            if pkey not in participants_map:
                participants_map[pkey] = pname
            elif participants_map[pkey] == pkey and pname != pkey:
                participants_map[pkey] = pname

        participants = sorted(participants_map.items(), key=lambda x: x[0])
        if len(participants) < 2:
            continue
        group_count += 1

        event_details.append(
            {
                "relation_type": relation_type,
                "table_name": table_name,
                "event_key": event_key,
                "person_count": len(participants),
                "participants": json.dumps(
                    [{"person_key": k, "person_name": n} for k, n in participants],
                    ensure_ascii=False,
                ),
            }
        )
        for (a_key, a_name), (b_key, b_name) in itertools.combinations(participants, 2):
            p1_key, p2_key = sorted([a_key, b_key])
            if p1_key == a_key:
                p1_name, p2_name = a_name, b_name
            else:
                p1_name, p2_name = b_name, a_name
            pair_records.append(
                {
                    "person_a_key": p1_key,
                    "person_a_name": p1_name,
                    "person_b_key": p2_key,
                    "person_b_name": p2_name,
                    "relation_type": relation_type,
                    "table_name": table_name,
                    "event_key": event_key,
                }
            )

    return pair_records, event_details, {
        "table_name": table_name,
        "status": "ok",
        "rows_loaded": int(len(df)),
        "groups": int(group_count),
        "pairs": int(len(pair_records)),
        "person_col": primary_person_col,
        "name_col": name_col or "",
        "event_cols": ",".join(event_cols),
    }


def build_reports(pair_rows, event_rows, table_logs):
    pair_df = pd.DataFrame(pair_rows)
    event_df = pd.DataFrame(event_rows)
    log_df = pd.DataFrame(table_logs)

    if pair_df.empty:
        summary_df = pd.DataFrame(columns=["关联人姓名", "关联的人员数量", "关联的信息来源", "关联的具体信息"])
        pair_summary_df = pd.DataFrame(
            columns=["person_a_name", "person_b_name", "共同事件数", "关联类型", "来源表", "示例事件"]
        )
        return pair_summary_df, event_df, summary_df, log_df

    pair_summary_df = (
        pair_df.groupby(["person_a_key", "person_a_name", "person_b_key", "person_b_name"], dropna=False)
        .agg(
            共同事件数=("event_key", "count"),
            关联类型=("relation_type", lambda x: "、".join(sorted(set(x)))),
            来源表=("table_name", lambda x: "、".join(sorted(set(x)))),
            示例事件=("event_key", "first"),
        )
        .reset_index()
        .sort_values(["共同事件数", "person_a_name", "person_b_name"], ascending=[False, True, True])
    )
    pair_summary_df = pair_summary_df[
        ["person_a_name", "person_b_name", "共同事件数", "关联类型", "来源表", "示例事件"]
    ]

    # 主报告按“关联的具体信息(event_key)”分组，列出同一事件下的全部关联人员
    event_group = defaultdict(lambda: {"names": set(), "sources": set(), "detail": ""})
    if not event_df.empty:
        for _, r in event_df.iterrows():
            relation_type = norm_str(r.get("relation_type", ""))
            table_name = norm_str(r.get("table_name", ""))
            event_key = norm_str(r.get("event_key", ""))
            participants_raw = r.get("participants", "[]")
            source = f"{relation_type}:{table_name}" if relation_type else table_name
            if not event_key:
                continue
            group_key = event_key
            event_group[group_key]["detail"] = event_key
            if source:
                event_group[group_key]["sources"].add(source)
            try:
                participants = json.loads(participants_raw) if participants_raw else []
            except Exception:
                participants = []
            for p in participants:
                name = norm_str(p.get("person_name", "")) or norm_str(p.get("person_key", ""))
                if name:
                    event_group[group_key]["names"].add(name)

    summary_rows = []
    for _, s in event_group.items():
        names = sorted(s["names"])
        summary_rows.append(
            {
                "关联人姓名": "、".join(names),
                "关联的人员数量": len(names),
                "关联的信息来源": "、".join(sorted(s["sources"])),
                "关联的具体信息": s["detail"],
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(["关联的人员数量", "关联的具体信息"], ascending=[False, True])

    if not event_df.empty:
        event_df = event_df.sort_values(["person_count", "relation_type"], ascending=[False, True])

    return pair_summary_df, event_df, summary_df, log_df


def write_report(out_path, pair_summary_df, event_df, summary_df, log_df):
    out_dir = os.path.dirname(out_path) or "."
    os.makedirs(out_dir, exist_ok=True)

    try:
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            summary_df.to_excel(writer, index=False, sheet_name="共同关联人报告")
            pair_summary_df.to_excel(writer, index=False, sheet_name="共同关联对")
            event_df.to_excel(writer, index=False, sheet_name="共同事件明细")
            log_df.to_excel(writer, index=False, sheet_name="处理日志")
        return out_path
    except Exception:
        # 无 Excel 依赖时兜底导出 CSV
        base = os.path.splitext(out_path)[0]
        summary_df.to_csv(f"{base}_共同关联人报告.csv", index=False, encoding="utf-8-sig")
        pair_summary_df.to_csv(f"{base}_共同关联对.csv", index=False, encoding="utf-8-sig")
        event_df.to_csv(f"{base}_共同事件明细.csv", index=False, encoding="utf-8-sig")
        log_df.to_csv(f"{base}_处理日志.csv", index=False, encoding="utf-8-sig")
        return f"{base}_*.csv"


def main():
    parser = argparse.ArgumentParser(description="分析数据库中档案_表的同乘车/同住宿/同出入境关联人")
    parser.add_argument(
        "--output",
        default="data/档案共同关联人报告.xlsx",
        help="输出报告路径，默认: data/档案共同关联人报告.xlsx",
    )
    args = parser.parse_args()

    tables = fetch_archive_tables()
    if not tables:
        print("未找到以 '档案_' 开头的表。")
        return

    print(f"找到 {len(tables)} 张档案表，开始分析...")
    pair_rows = []
    event_rows = []
    table_logs = []

    for t in tables:
        print(f"  -> 处理: {t}")
        try:
            pairs, events, log = analyze_table(t)
            pair_rows.extend(pairs)
            event_rows.extend(events)
            table_logs.append(log)
            if log.get("status") == "ok":
                print(f"     事件组: {log.get('groups', 0)}，关联对: {log.get('pairs', 0)}")
            else:
                print(f"     跳过: {log.get('reason')}")
        except Exception as e:
            table_logs.append({"table_name": t, "status": "error", "reason": f"{type(e).__name__}: {e}"})
            print(f"     失败: {e}")

    pair_summary_df, event_df, summary_df, log_df = build_reports(pair_rows, event_rows, table_logs)
    output_file = write_report(args.output, pair_summary_df, event_df, summary_df, log_df)
    print(f"分析完成，报告已输出: {output_file}")


if __name__ == "__main__":
    main()
