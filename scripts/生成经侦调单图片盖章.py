import pandas as pd
from re import sub
import uuid
import time
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote
import mariadb
from loguru import logger
import configparser
from sqlalchemy.sql import text
from configparser import ConfigParser
import matplotlib.pyplot as plt
import numpy as np
from pylab import mpl
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
overlay_image_path = r'./img/z.png'

con_config = configparser.ConfigParser()

logger.add("logs\冻结银行列表截图.log", format="{time} {level} {message}", filter="", level="INFO")
MYSQL_HOST = '172.16.10.101'
MYSQL_PORT = '3306'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Network@2024'
MYSQL_DB = 'hbjt'
engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{urlquote(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8')

path='冻结银行截图'

conn=engine.connect()
sql_dir=r'C:\Users\fuyip\Documents\Navicat\MySQL\Servers\172.16.10.101\hbjt'

def creat_jt(df,bank_name):

    fig, ax = plt.subplots(figsize=(17, 13))  # 设置画布大小为宽7英寸，高10英寸
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')

    table.set_fontsize(50)

    for (row, col), cell in table.get_celld().items():
        cell.set_height(0.04)
        if col == 0:
            cell.set_width(0.1)
        if col == 1:
            cell.set_width(0.1)  # 设置第二列单元格宽度
        if col == 2:
            cell.set_width(0.2)
        if col == 3:
            cell.set_width(0.2)
        if col == 4:
            cell.set_width(0.2)
        if col == 5:
            cell.set_width(0.1)
        if col == 6:
            cell.set_width(0.1)
        if col == 7:
            cell.set_width(0.1)
        if col == 8:
            cell.set_width(0.1)
        if col == 9:
            cell.set_width(0.2)

    # plt.axes([0.8, 0, 0.2, 0.2])
    # # Load and overlay the image
    # overlay_img = plt.imread(overlay_image_path)
    # overlay_height = 5  # 设置叠加图片的高度
    # overlay_width = 5  # 设置叠加图片的宽度
    # ax.imshow(overlay_img, aspect='auto', extent=[7 - overlay_width, 7, 10 - overlay_height, 10])
    #
    # plt.axis("off")
    #

    plt.axes([0.68, 0.45, 0.2, 0.2])  # 右上方
    bgimg = plt.imread(overlay_image_path)
    plt.imshow(bgimg, alpha=0.8)
    plt.axis("off")

    plt.subplots_adjust(left=0.2, right=0.8, bottom=0.2, top=0.8)  # 调整子图布局
    plt.savefig(f'{path}/{bank_name}.jpg', dpi=60)
    logger.info(f'{path}/{bank_name}.jpg生成')

if __name__ == '__main__':


    if not os.path.exists(path):
        os.makedirs(path)
    with open(f'{sql_dir}/111.sql', 'r', encoding='utf-8') as file:
        sql_cl = file.read()

    dd_all_outdir=f'{path}/所有调单'
    if not os.path.exists(dd_all_outdir):
        os.makedirs(dd_all_outdir)


    data_sql=pd.read_sql(text(sql_cl),con=conn)
    print(data_sql)

    dfs = {}
    for bank_name in data_sql['选择银行'].unique():
        bank_data = data_sql[data_sql['选择银行'] == bank_name]
        if len(bank_data) > 40:
            k=len(bank_data)
            cnt=0
            while 1:
                dfs[f"{bank_name}_part_{cnt + 1}"]=bank_data[cnt*40:(cnt+1)*40]
                cnt+=1
                k=k-40
                if k<=0: break
            # num_chunks = (len(bank_data) - 1) // 40 + 1
            # chunked_data = np.array_split(bank_data, num_chunks)
            # for i, chunk in enumerate(chunked_data):
            #     dfs[f"{bank_name}_part_{i + 1}"] = chunk
        else:
            dfs[bank_name] = bank_data

    # 打印每个银行的数据
    for key, value in dfs.items():
        df=pd.DataFrame(value)
        print(f"键: {key}")
        print(value)
        df.to_csv(f'csv/{key}.csv', index=False)
        print(df)
        print()
        creat_jt(df,key)