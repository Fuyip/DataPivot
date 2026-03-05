import os
import sys
import pandas as pd


DATA_DIR = os.path.join("doc", "wca")
EXCLUDED_FILE = "王朝安.xlsx"
TABLE_NAME = "29-微信好友"

SOURCE_COLUMNS = ["C1", "C2", "C3", "C4", "C5", "C6", "C8"]
TARGET_MAPPING = {
    "C1": "好友类型",
    "C2": "好友微信号",
    "C3": "好友id",
    "C4": "微信群号",
    "C5": "好友备注",
    "C6": "添加好友来源",
    "C8": "信息来源",
}


try:
    sys.path.append(os.getcwd())
    from database import engine
except Exception as exc:
    print(f"❌ 无法导入 database.py 中的 engine: {exc}")
    raise SystemExit(1)


def _normalize_c_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    按固定位置提取: C1~C8 对应原始表格第2~第9列（0-based: 1~8）。
    """
    if df.shape[1] < 9:
        return pd.DataFrame()

    by_index = df.iloc[:, 1:9].copy()
    by_index.columns = [f"C{i}" for i in range(1, 9)]
    return by_index


def _extract_from_sheet(df: pd.DataFrame, wechat_owner: str) -> pd.DataFrame:
    normalized = _normalize_c_columns(df)
    if normalized.empty:
        return pd.DataFrame()

    for col in SOURCE_COLUMNS:
        if col not in normalized.columns:
            normalized[col] = None

    # 先绑定索引，避免先赋常量列再对齐时被填成 NaN
    out = pd.DataFrame(index=normalized.index)
    out["主体微信号"] = wechat_owner
    for src, target in TARGET_MAPPING.items():
        out[target] = normalized[src]

    out = out.replace({pd.NA: None})
    out = out.where(pd.notna(out), None)

    non_owner_cols = [c for c in out.columns if c != "主体微信号"]
    out = out.dropna(how="all", subset=non_owner_cols)
    return out


def _parse_owner_from_filename(filename: str) -> str:
    """
    主体微信号取文件名（不含扩展名）。
    例: zengzhihao764.xlsx -> zengzhihao764
    """
    stem = os.path.splitext(filename)[0].strip()
    return stem


def main():
    if not os.path.isdir(DATA_DIR):
        print(f"❌ 目录不存在: {DATA_DIR}")
        return

    files = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.lower().endswith(".xlsx") and f != EXCLUDED_FILE
    )

    if not files:
        print("⚠️ 未找到可导入的 xlsx 文件。")
        return

    print(f"📂 待处理文件数: {len(files)} (已排除: {EXCLUDED_FILE})")
    all_rows = []

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        owner_wechat = _parse_owner_from_filename(filename)
        print(f"   正在处理: {filename}")

        try:
            sheets = pd.read_excel(filepath, sheet_name=None, dtype=str, header=None)
        except Exception as exc:
            print(f"   ⚠️ 读取失败: {filename}, 原因: {exc}")
            continue

        before_count = len(all_rows)
        for sheet_name, df in sheets.items():
            extracted = _extract_from_sheet(df, owner_wechat)
            if not extracted.empty:
                all_rows.append(extracted)
            else:
                print(f"      - 跳过 sheet [{sheet_name}]：缺少有效列或无有效数据")

        added = sum(len(x) for x in all_rows[before_count:])
        print(f"      + 提取行数: {added}")

    if not all_rows:
        print("⚠️ 未提取到任何可写入数据。")
        return

    final_df = pd.concat(all_rows, ignore_index=True)
    final_df = final_df.where(pd.notna(final_df), None)

    print(f"💾 准备写入 {len(final_df)} 行到表 [{TABLE_NAME}] ...")
    try:
        final_df.to_sql(name=TABLE_NAME, con=engine, if_exists="replace", index=False)
        print("✅ 导入完成。")
    except Exception as exc:
        print(f"❌ 写入数据库失败: {exc}")


if __name__ == "__main__":
    main()
