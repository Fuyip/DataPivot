import pandas as pd
import os
import re
import glob
# 引入 DateTime 类型
from sqlalchemy.types import VARCHAR, DateTime

# 导入配置好的 engine
try:
    from database import engine
except ImportError:
    print("错误：无法导入 'database.py'，请确保文件存在且定义了 'engine' 变量。")
    exit()


def process_device_archives(base_dir='YM/设备档案'):
    """
    读取Excel，提取信息，合并数据，并转换时间格式
    """
    sheet_data_collection = {}
    search_path = os.path.join(base_dir, '设备档案-*.xlsx')
    files = glob.glob(search_path)

    print(f"在 '{base_dir}' 下找到 {len(files)} 个文件，开始处理...")

    pattern = re.compile(r"查询ID：(.*?)，关联设备：(.*?)（(.*?)至(.*?)）")

    for file_path in files:
        file_name = os.path.basename(file_path)

        try:
            xls = pd.ExcelFile(file_path)

            for sheet_name in xls.sheet_names:
                if sheet_name == '位置轨迹':
                    continue

                # 读取第一行元数据
                df_meta = pd.read_excel(xls, sheet_name=sheet_name, header=None, nrows=1)
                if df_meta.empty: continue

                meta_text = str(df_meta.iloc[0, 0])
                match = pattern.search(meta_text)

                q_id, device, t_start, t_end = None, None, None, None

                if match:
                    q_id = match.group(1).strip()
                    device = match.group(2).strip()
                    t_start = match.group(3).strip()
                    t_end = match.group(4).strip()

                # 读取正文数据
                df_data = pd.read_excel(xls, sheet_name=sheet_name, header=1)

                # 添加列（此时还是字符串）
                df_data = df_data.assign(
                    查询ID=q_id,
                    关联设备=device,
                    开始时间=t_start,
                    结束时间=t_end
                )

                if sheet_name not in sheet_data_collection:
                    sheet_data_collection[sheet_name] = []
                sheet_data_collection[sheet_name].append(df_data)

        except Exception as e:
            print(f"处理文件 {file_name} 时发生错误: {e}")

    final_dfs = {}
    for sheet_name, df_list in sheet_data_collection.items():
        if df_list:
            merged_df = pd.concat(df_list, ignore_index=True)

            # ====================================================
            # 关键修改 1: 将字符串转换为 datetime 对象
            # ====================================================
            # errors='coerce' 表示如果解析失败（如格式不对或为空），则设为 NaT (数据库中的NULL)
            merged_df['开始时间'] = pd.to_datetime(merged_df['开始时间'], errors='coerce',format='%Y-%m-%d')
            merged_df['结束时间'] = pd.to_datetime(merged_df['结束时间'], errors='coerce',format='%Y-%m-%d')

            table_name = f"YM-{sheet_name}"
            final_dfs[table_name] = merged_df

    return final_dfs


def save_to_database(data_frames):
    if not data_frames:
        return

    try:
        with engine.connect() as conn:
            print("数据库连接测试成功。")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return

    for table_name, df in data_frames.items():
        print(f"正在写入表: {table_name} (共 {len(df)} 行)...")

        try:
            # ====================================================
            # 关键修改 2: 更新 dtype 映射，指定为 DateTime
            # ====================================================
            dtype_dict = {
                '查询ID': VARCHAR(100),
                '关联设备': VARCHAR(100),
                '开始时间': DateTime(),  # 这里指定为 DateTime 类型
                '结束时间': DateTime()  # 这里指定为 DateTime 类型
            }

            df.to_sql(
                name=table_name.lower(),
                con=engine,
                if_exists='replace',
                index=False,
                dtype=dtype_dict
            )
            print(f"  -> {table_name} 写入完成。")

        except Exception as e:
            print(f"  -> 写入表 {table_name} 失败: {e}")


if __name__ == "__main__":
    if os.path.exists(os.path.join('YM', '设备档案')):
        result_tables = process_device_archives()
        save_to_database(result_tables)
        print("\n所有任务执行完毕。")
    else:
        print("错误：未找到目录 'YM/设备档案'。")
