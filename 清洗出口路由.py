from database import engine, get_db
import pandas as pd
import os
from sqlalchemy import create_engine


def process_excel_to_db():
    # 1. 定义文件路径
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接文件路径：当前目录/doc/出口路由.xlsx
    file_path = os.path.join(current_dir, 'doc', '出口路由.xlsx')

    print(f"正在读取文件: {file_path}")

    if not os.path.exists(file_path):
        print("错误: 未找到文件，请检查路径。")
        return

    try:
        # 2. 读取Excel文件
        # sheet_name=None 表示读取所有sheet，返回一个字典 {sheet名: dataframe}
        # header=None 表示源文件没有表头
        xls_dict = pd.read_excel(file_path, sheet_name=None, header=None)
    except Exception as e:
        print(f"读取Excel失败: {e}")
        return

    all_data_frames = []

    # 定义列名
    columns = ['出口路由地址', '路由厂商', '最后记录时间']

    # 3. 遍历每一个 Sheet (选项卡)
    for sheet_name, df in xls_dict.items():
        # 跳过空Sheet
        if df.empty:
            continue

        # 确保只有3列数据（防止Excel中有隐藏列或脏数据）
        df = df.iloc[:, :3]

        # 如果列数不对，打印警告并跳过
        if df.shape[1] != 3:
            print(f"警告: 机器码 {sheet_name} 的数据列数不为3，已跳过。")
            continue

        # 设置表头
        df.columns = columns

        # 添加机器码列（来源为Sheet名称）
        df['机器码'] = sheet_name

        # 调整列顺序，将机器码放在第一列
        df = df[['机器码', '出口路由地址', '路由厂商', '最后记录时间']]

        all_data_frames.append(df)

    # 4. 合并所有数据
    if all_data_frames:
        final_df = pd.concat(all_data_frames, ignore_index=True)
        print(f"数据处理完成，共合并 {len(final_df)} 条数据。")
        print(final_df.head())  # 打印前几行预览

        # 5. 存入数据库
        save_to_database(final_df,engine)
    else:
        print("没有读取到有效数据。")


def save_to_database(df,engine):
    try:
        # name='export_routes_table': 数据库中的表名
        # if_exists='append': 如果表存在则追加数据，'replace'为覆盖，'fail'为报错
        # index=False: 不将pandas的索引列写入数据库
        df.to_sql(name='export_routes_table', con=engine, if_exists='replace', index=False)

        print("成功存入数据库！")
    except Exception as e:
        print(f"数据库写入失败: {e}")


if __name__ == "__main__":
    process_excel_to_db()
