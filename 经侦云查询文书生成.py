import pandas as pd
import win32com
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote
from docxtpl import DocxTemplate
import os
from loguru import logger
from sqlalchemy.sql import text
import re
import json
from configparser import ConfigParser
import cpca
import fitz
from win32com import client
from cpca import drawer
import folium
import aspose.words as aw
import win32com.client
import shutil
# 读取配置
conf = ConfigParser()
conf.read(r'.\config.ini', encoding='utf-8')

# 设置日志
logger.add(r"logs\划拨文书生成.log", format="{time} {level} {message}", level="INFO")

# 配置 MySQL
MYSQL_HOST = conf['database']['MYSQL_HOST']
MYSQL_PORT = conf['database']['MYSQL_PORT']
MYSQL_USER = conf['database']['MYSQL_USER']
MYSQL_PASSWORD = conf['database']['MYSQL_PASSWORD']
MYSQL_DB = conf['database']['MYSQL_DB']

# 创建数据库引擎
engine = create_engine(
    f'mysql+pymysql://{MYSQL_USER}:{urlquote(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4'
)
connection= engine.connect()

#设置文件位置
dir=r'.\files'

sql_dir=conf['path']['sql_dir']
dz_dir=conf['path']['dz_dir']
output_dir=conf['path']['output_dir']
wsh=int(conf['diaozheng']['wsh_start'])
max_num = int(conf['shenying']['max_num'])
jpg_max_num=int(conf['shenying']['jpg_max_num'])

df_wsh_list=pd.DataFrame({
    'bank_name':[],
    'wsh':[]
})



def pdf2img(pdf_path, img_path,filename):
    pdfDoc = fitz.open(pdf_path)
    i=0
    for page in pdfDoc.pages():
        i+=1
        # 将页面转换为图片
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=72
        # pix = page.get_pixmap()
        zoom_x = 1.5
        zoom_y = 1.5
        # (1.33333333-->1056x816)   (2-->1584x1224)  (3-->3572x2526)
        # x和y的值越大越清晰，图片越大，但处理也越耗时间，这里取决于你想要图片的清晰度
        # 默认为1.333333，一般日常使用3就够了，不能设置太大，太大容易使电脑死机
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix=mat, dpi=None, colorspace='rgb', alpha=False)
        if i==1:
            # 保存图片
            pix.save(f"{img_path}/{filename}.jpg") #只保存第一页
    pdfDoc.close()
    os.remove(f'{img_path}/{filename}.pdf')
    os.remove(f'{img_path}/{filename}.docx')

def doc2pdf2img(fn,wsh,cnt):
    # word = client.Dispatch("Word.Application")  # 打开word应用程序
    word = win32com.client.Dispatch("Kwps.Application")
    # for file in files:
    doc = word.Documents.Open(fn)  # 打开word文件

    doc.SaveAs("{}.pdf".format(fn[:-5]), 17)  # 另存为后缀为".pdf"的文件，其中参数17表示为pdf
    doc.Close()  # 关闭原来word文件
    word.Quit()
    pdf2img(f'{output_dir}/{wsh}/{wsh}_{cnt}.pdf',f"{output_dir}/{wsh}",f"{wsh}_{cnt}")


with open(f'{sql_dir}/待调取银行卡.sql','r',encoding='utf-8') as file:
    sql_dd_yhk=text(file.read())
df_dd_yhk=pd.read_sql(sql_dd_yhk,con=connection)

with open(f'{sql_dir}/调证银行列表.sql','r',encoding='utf-8') as file:
    sql_bank_list=text(file.read())
df_bank_list=pd.read_sql(sql_bank_list,con=connection)


# 对所有银行遍历
for i in range(0,len(df_bank_list)):
    j=0
    # 对选中银行进行拆分调单
    while j*max_num<df_bank_list.iloc[i]['card_cnt']:

        df_card_list = pd.DataFrame({
            '账/卡号类型': [],
            '被查账/卡号': [],
            '选择银行': [],
            '查询种类': [],
            '时间标识': [],
            '开始时间': [],
            '结束时间': []
        })
        df_card_list=pd.DataFrame()



        # 分配文书号
        new_row = pd.Series([df_bank_list.iloc[i]['bank_name'],wsh], index=df_wsh_list.columns)

        # 创建以文书号命名文件夹
        if not os.path.exists(f'{output_dir}/{wsh}'):
            os.makedirs(f'{output_dir}/{wsh}')
        df_qp=df_dd_yhk.loc[df_dd_yhk['bank_name'] == df_bank_list.iloc[i]['bank_name']].iloc[j*max_num:(j+1)*max_num,:]

        # df_dd_yhk.loc[df_dd_yhk['bank_name'] == df_bank_list.iloc[i]['bank_name']].iloc[j*max_num:(j+1)*max_num,:].to_excel(f'{output_dir}/{wsh}/{wsh}.xlsx',index=False)
        df_card_list['被查账/卡号'] = df_qp['card_no']
        df_card_list['选择银行']=df_bank_list.iloc[i]['bank_name']

        df_card_list['账/卡号类型'] = conf['diaozheng']['card_type']
        df_card_list['查询种类'] = conf['diaozheng']['search_type']
        df_card_list['时间标识'] = conf['diaozheng']['time_sign']
        df_card_list['开始时间'] = conf['diaozheng']['min_time']
        df_card_list['结束时间'] = conf['diaozheng']['max_time']
        order=['账/卡号类型',
            '被查账/卡号',
            '选择银行',
            '查询种类',
            '时间标识',
            '开始时间',
            '结束时间']
        df_card_list=df_card_list[order]
        df_card_list.to_excel(f'{output_dir}/{wsh}/{wsh}.xls',index=False,engine='xlsxwriter')

        logger.info(f'文书：{wsh}生成！')
        df_wsh_list=df_wsh_list._append(new_row, ignore_index=True)

        tp_gr = DocxTemplate(f'{dz_dir}/协助查询财产通知书模板.docx')
        min_time_cn=conf['diaozheng']['min_time'].split('/')
        max_time_cn = conf['diaozheng']['max_time'].split('/')
        dict = {
            'wsh': wsh,
            'bank_name': df_bank_list.iloc[i]['bank_name'],
            'card_no': df_qp.iloc[0]['card_no'],
            'card_cnt': len(df_qp),
            'min_time': min_time_cn[0]+'年'+min_time_cn[1]+'月'+min_time_cn[2]+'日' if min_time_cn[0]!='' else '',
            'max_time': max_time_cn[0]+'年'+max_time_cn[1]+'月'+max_time_cn[2]+'日' if max_time_cn[0]!='' else ''

        }
        tp_gr.render(dict)
        tp_gr.save(f'{output_dir}/{wsh}/{wsh}_1.docx')
        doc2pdf2img(f'{output_dir}/{wsh}/{wsh}_1.docx', wsh, 1)
        logger.info(f'{output_dir}/{wsh}/{wsh}_1.jpg 已保存')

        m=0
        while m * jpg_max_num < len(df_qp):
            dict_list= {}
            dict_list['labels']=['银行卡号','银行']
            dict_list['card_list']=[]
            for item in df_qp.loc[:,['card_no','bank_name']].iloc[m*jpg_max_num:(m+1)*jpg_max_num,:].values.tolist():
                dict_t = {}
                dict_t['cols'] = item
                # print(dict_t)
                dict_list['card_list'].append(dict_t)
            tp_card_list=DocxTemplate(f'{dz_dir}/查询银行卡列表图片.docx')
            tp_card_list.render(dict_list)
            tp_card_list.save(f'{output_dir}/{wsh}/{wsh}_{m+2}.docx')
            doc2pdf2img(f'{output_dir}/{wsh}/{wsh}_{m+2}.docx', wsh,m+2)
            logger.info(f'{output_dir}/{wsh}/{wsh}_{m+2}.jpg 已保存')
            m+=1

        shutil.copy(os.path.join(f'{dz_dir}\固定附件', '1.jpg'), os.path.join(f'{output_dir}/{wsh}', f'{wsh}_{m+2}.jpg'))
        shutil.copy(os.path.join(f'{dz_dir}\固定附件', '2.jpg'),
                    os.path.join(f'{output_dir}/{wsh}', f'{wsh}_{m + 3}.jpg'))


        j += 1  # 记录拆分part
        wsh+=1 # 文书号自增



df_wsh_list.to_excel('wsh_list.xlsx',index=False)

# print(df_bank_list)




