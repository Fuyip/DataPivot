import os
import pandas as pd
# 从你的 database.py 文件中导入 engine
# 确保 database.py 在同一目录下，或者在 python path 中
from database import engine


def process_and_save_files():
    # 1. 设定文件目录
    target_dir = os.path.join("YM", "路由档案")

    # 用于存储所有读取的数据帧
    all_dataframes = []

    # 检查目录是否存在
    if not os.path.exists(target_dir):
        print(f"错误：目录 '{target_dir}' 不存在。")
        return

    # 2. 遍历目录下的所有文件
    files = [f for f in os.listdir(target_dir) if f.endswith('.csv')]

    print(f"发现 {len(files)} 个CSV文件，开始处理...")

    for filename in files:
        file_path = os.path.join(target_dir, filename)

        # 去掉文件后缀 .csv
        name_without_ext = os.path.splitext(filename)[0]

        try:
            # 3. 解析文件名关键逻辑
            # 格式：{设备名称}-{MAC}-{StartY}-{StartM}-{StartD}-{EndY}-{EndM}-{EndD}
            # 后面的7个部分（MAC + 3个开始时间 + 3个结束时间）是固定的
            # 所以我们限制从右边分割 7 次
            parts = name_without_ext.rsplit('-', 7)

            if len(parts) != 8:
                print(f"跳过文件（命名格式不匹配）: {filename}")
                continue

            # 解包变量
            device_name = parts[0]  # 剩下的左边部分全都是设备名称（包含其中的横杠）
            mac_addr = parts[1]
            start_year, start_month, start_day = parts[2], parts[3], parts[4]
            end_year, end_month, end_day = parts[5], parts[6], parts[7]

            # 组合日期字符串
            start_date = f"{start_year}-{start_month}-{start_day}"
            end_date = f"{end_year}-{end_month}-{end_day}"

            # 4. 读取CSV文件
            # 尝试常见的编码格式，中文环境常用 gbk 或 utf-8
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='gbk')

            # 5. (可选) 将文件名中的元数据添加到表格中
            # 通常合并文件时，最好保留来源信息，如果不需要可以注释掉这几行
            df['设备名称'] = device_name
            df['设备MAC'] = mac_addr
            df['记录开始日期'] = pd.to_datetime(start_date)
            df['记录结束日期'] = pd.to_datetime(end_date)

            all_dataframes.append(df)
            print(f"已处理: {filename}")

        except Exception as e:
            print(f"处理文件 {filename} 时发生错误: {e}")

    # 6. 合并并存入数据库
    if all_dataframes:
        # 合并所有数据
        merged_df = pd.concat(all_dataframes, ignore_index=True)

        print(f"正在将 {len(merged_df)} 条数据存入数据库...")

        try:
            # 存入数据库
            # if_exists='append': 如果表存在则追加数据
            # if_exists='replace': 如果表存在则删除重建（根据需求修改）
            # index=False: 不将pandas的索引列存入数据库
            merged_df.to_sql(
                name='YM-路由设备',
                con=engine,
                if_exists='replace',
                index=False
            )
            print("处理完成！数据已成功存入表 'YM-路由设备'。")
        except Exception as db_err:
            print(f"数据库写入错误: {db_err}")
    else:
        print("没有可合并的有效数据。")


if __name__ == "__main__":
    process_and_save_files()
