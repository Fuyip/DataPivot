import pandas as pd
import os
import sys
from sqlalchemy import text

# ---------------------------------------------------------
# 1. 配置与初始化
# ---------------------------------------------------------
DATA_DIR = 'data/云搜人员基本信息'

# 尝试导入数据库连接引擎
try:
    sys.path.append(os.getcwd())
    from database import engine

    print("✅ 成功连接数据库引擎。")
except ImportError:
    print("❌ 错误：未找到 'database.py' 或无法导入 'engine' 对象。")
    exit(1)


# ---------------------------------------------------------
# 2. 核心处理函数
# ---------------------------------------------------------
def parse_personnel_sheet(df):
    """
    解析【人员电子档案】这种特殊的 Key-Value 布局表格。
    将网格状分布的 "标签: 内容" 转换为单行 DataFrame。
    """
    # 策略：将 DataFrame 的表头（被误读的第一行）和内容全部展平处理
    # 构建一个包含所有数据的列表
    content = []

    # 1. 还原表头到数据行中
    # 如果列名是 'Unnamed: ...' (Pandas 自动生成的)，则视为 NaN
    headers = [str(c) if 'Unnamed' not in str(c) else pd.NA for c in df.columns]
    content.append(headers)

    # 2. 加入剩余的数据行
    content.extend(df.values.tolist())

    data_dict = {}

    # 3. 遍历网格，寻找 "Key:" 和其右侧的 "Value"
    for row in content:
        # 遍历该行的每一个单元格 (除了最后一个，因为要取 i+1)
        for i in range(len(row) - 1):
            key = row[i]
            val = row[i + 1]

            # 判断 key 是否为字符串且以冒号结尾 (识别 Label)
            if isinstance(key, str):
                key = key.strip()
                # 兼容中文冒号和英文冒号
                if key.endswith(':') or key.endswith('：'):
                    # 清洗 Key：去掉末尾的冒号
                    real_key = key[:-1].strip()

                    # 清洗 Value：处理 NaN 和空值
                    if pd.isna(val) or str(val).lower() == 'nan':
                        real_val = None
                    else:
                        real_val = str(val).strip()

                    data_dict[real_key] = real_val

    # 返回单行 DataFrame
    return pd.DataFrame([data_dict])


# ---------------------------------------------------------
# 3. 主程序
# ---------------------------------------------------------
def main():
    if not os.path.exists(DATA_DIR):
        print(f"❌ 目录不存在: {DATA_DIR}")
        return

    # 扫描文件
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.xls', '.xlsx'))]
    print(f"📂 找到 {len(files)} 个 Excel 文件，开始处理...")

    # 用于按 Sheet 名称分类收集所有文件的数据
    # 结构: { 'Sheet名称': [DataFrame1, DataFrame2, ...] }
    all_sheets_data = {}

    # --- 第一步：读取并清洗数据 ---
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        print(f"   正在读取: {filename}")

        try:
            # 【关键点1】dtype=str
            # 强制所有列读取为字符串，防止身份证号变成科学计数法
            xls_dict = pd.read_excel(filepath, sheet_name=None, dtype=str)
        except Exception as e:
            print(f"   ⚠️ 读取失败 {filename}: {e}")
            continue

        for sheet_name, df in xls_dict.items():
            # 【关键点2】特殊表格处理
            if '人员电子档案' in sheet_name:
                try:
                    processed_df = parse_personnel_sheet(df)
                except Exception as e:
                    print(f"   ⚠️ 解析特殊 Sheet '{sheet_name}' 出错: {e}")
                    continue
            else:
                # 普通表格
                processed_df = df

            # 归类收集
            if sheet_name not in all_sheets_data:
                all_sheets_data[sheet_name] = []

            # 即使是空表也保留（用于后续创建表结构）
            all_sheets_data[sheet_name].append(processed_df)

    # --- 第二步：合并、去重与入库 ---
    print("\n💾 开始写入数据库...")

    for sheet_name, df_list in all_sheets_data.items():
        if not df_list:
            continue

        # 1. 合并该 Sheet 下所有文件的数据
        merged_df = pd.concat(df_list, ignore_index=True, sort=False)

        # 2. 【关键点3】数据去重
        rows_before = len(merged_df)
        merged_df.drop_duplicates(inplace=True)
        rows_after = len(merged_df)

        if rows_before > rows_after:
            print(f"   ✂️ 表 [{sheet_name}] 已去除 {rows_before - rows_after} 条重复数据")

        # 清理表名
        table_name = sheet_name.strip()
        print(f"   -> 处理表 [{table_name}]，最终写入 {len(merged_df)} 行")

        try:
            # 3. 【关键点4】写入数据库 (删除重建)
            # if_exists='replace': 如果表存在，先 DROP 再 CREATE
            merged_df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

            # 4. 【关键点5】添加主键 id
            # 因为 to_sql(index=False) 不会创建主键，我们需要手动修改表结构
            # 但如果源数据已包含 id 列，则跳过新增，避免重复列报错
            with engine.begin() as conn:
                has_id_sql = text("""
                    SELECT 1
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = :table_name
                      AND COLUMN_NAME = 'id'
                    LIMIT 1;
                """)
                has_id = conn.execute(has_id_sql, {"table_name": table_name}).scalar() is not None

                if not has_id:
                    add_pk_sql = text(f"""
                        ALTER TABLE `{table_name}`
                        ADD COLUMN `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
                    """)
                    conn.execute(add_pk_sql)
                else:
                    print(f"      ℹ️ 表 {table_name} 已存在 id 列，跳过新增主键列。")

        except Exception as e:
            print(f"      ❌ 写入/修改表 {table_name} 失败: {e}")

    print("\n✨ 所有任务执行完毕。")


if __name__ == '__main__':
    main()
