import pandas as pd
import os
import re
from sqlalchemy import text
from sqlalchemy.types import String, Integer
from database import engine

# 1. 配置
data_dir = 'data/云搜人员综合信息'
table_name = 'combined_personnel_info'


# --- 智能读取函数 ---
def smart_read(filepath):
    encodings = ['gb18030', 'utf-8', 'gbk']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except:
            continue
    try:
        return pd.read_excel(filepath)
    except:
        pass
    try:
        dfs = pd.read_html(filepath)
        if dfs: return dfs[0]
    except:
        pass
    raise ValueError("无法识别文件格式")


# ==========================================
# 第一步：读取并处理文件
# ==========================================
all_files = []
print(f"开始扫描目录: {data_dir}")

for filename in os.listdir(data_dir):
    if filename.endswith(('.csv', '.xls', '.xlsx')):
        file_path = os.path.join(data_dir, filename)
        try:
            # 1. 解析文件名
            name_no_ext = os.path.splitext(filename)[0]
            name_cleaned = re.sub(r'\s*\(\d+\)$', '', name_no_ext)

            parts = name_cleaned.split('-')
            if len(parts) >= 2:
                source_id = parts[-1].strip()
                source_name = parts[-2].strip()
            else:
                source_id = None
                source_name = None

            # 2. 读取数据
            df_temp = smart_read(file_path)

            # 3. 统一列名格式
            df_temp.columns = df_temp.columns.str.strip()

            # 4. 写入来源信息
            df_temp['来源姓名'] = source_name
            df_temp['来源身份证'] = source_id

            all_files.append(df_temp)
            print(f"读取成功: {filename}")

        except Exception as e:
            print(f"读取失败: {filename}, 原因: {e}")

if not all_files:
    print("未找到任何数据文件。")
    exit()

# 合并所有数据
final_df = pd.concat(all_files, ignore_index=True)

# ==========================================
# 第二步：内存级去重
# ==========================================
# 删除完全重复的行（防止文件本身被复制了一份导致的内容完全重复）
print(f"原始数据行数: {len(final_df)}")
final_df.drop_duplicates(inplace=True)
print(f"去除文件级重复后行数: {len(final_df)}")

# ==========================================
# 第三步：数据库逻辑 (清空表并重新导入)
# ==========================================
print("将清空表并重新导入所有数据...")
write_mode = 'replace'

# ==========================================
# 第四步：数据类型清洗
# ==========================================
if not final_df.empty:
    columns = final_df.columns
    dtype_mapping = {}

    # 按照需求：F-U (索引5-20) 为 Int
    int_col_indices = list(range(5, 21))
    valid_int_indices = [i for i in int_col_indices if i < len(columns)]

    for i, col in enumerate(columns):
        if col in ['来源姓名', '来源身份证']:
            final_df[col] = final_df[col].astype(str).replace('nan', '')
            dtype_mapping[col] = String(255)
            continue

        if i in valid_int_indices:
            # 转整数
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).astype(int)
            dtype_mapping[col] = Integer()
        else:
            # 转字符串
            final_df[col] = final_df[col].astype(str).replace('nan', '')
            dtype_mapping[col] = String(255)

    print(f"正在写入 {len(final_df)} 条新数据 (模式: {write_mode})...")

    final_df.to_sql(
        name=table_name,
        con=engine,
        if_exists=write_mode,
        index=False,
        dtype=dtype_mapping
    )

    # ==========================================
    # 第五步：后期处理 (添加主键 ID 和 联合索引)
    # ==========================================
    print("正在优化表结构 (添加主键 ID 和 联合索引)...")
    try:
        with engine.connect() as conn:
            # 1. 添加自增主键
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"))
            # 2. 【新增】添加联合索引：加快 (身份证号码 + 来源身份证) 的查重速度
            conn.execute(text(f"ALTER TABLE {table_name} ADD INDEX idx_sfz_source (身份证号码, 来源身份证)"))
            conn.commit()
        print("表结构优化完成！")
    except Exception as e:
        print(f"结构优化失败: {e}")

    print("全部完成！")

else:
    print("没有数据需要写入。")