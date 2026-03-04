import pymysql
import re
import pandas as pd
from loguru import logger
import gc
import xlsxwriter
from configparser import ConfigParser

logger.add("logs\银行分类拆分.log", format="{time} {level} {message}", filter="", level="INFO")
filepath=r'E:\银行卡拆分'

conf = ConfigParser()  # 需要实例化一个ConfigParser对象
conf.read(r'.\config.ini', encoding='utf-8')  # 需要添加上config.ini的路径，不需要open打开，直接给文件路径就读取，也可以指定encoding='utf-8'

MYSQL_HOST=conf['database']['MYSQL_HOST']
MYSQL_PORT=conf['database']['MYSQL_PORT']
MYSQL_USER=conf['database']['MYSQL_USER']
MYSQL_PASSWORD=conf['database']['MYSQL_PASSWORD']
MYSQL_DB=conf['database']['MYSQL_DB']
XLS_FILE=conf['path']['xls_file']

class MysqlSave:

    def __init__(self):
        self.content = pymysql.Connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            db=MYSQL_DB,
            charset='utf8',
        )
        self.cursor = self.content.cursor()

    def search_and_save(self, sql, csv_file):
        """
        导出为csv的函数
        :param sql: 要执行的mysql指令
        :param csv_file: 导出的csv文件名
        :return:
        """

        # 执行sql语句
        self.cursor.execute(sql)

        # 拿到表头
        des = self.cursor.description
        title = [each[0] for each in des]

        # 拿到数据库查询的内容
        result_list = []
        for each in self.cursor.fetchall():
            result_list.append(list(each))

        # 保存成dataframe
        df_dealed = pd.DataFrame(result_list, columns=title)
        # 保存成csv 这个编码是为了防止中文没法保存，index=None的意思是没有行号
        pd.set_option('display.float_format', lambda x: '%.2f' % x)

        writer = pd.ExcelWriter(csv_file, engine='xlsxwriter')
        workbook = writer.book
        worksheet = workbook.add_worksheet('Bank_statements')
        writer.sheets['Bank_statements'] = worksheet

        format = workbook.add_format({'bg_color': '#5EA374'})

        r_row=0
        for row in df_dealed.itertuples():
            r_row = r_row + 1
            if (getattr(row, '收付标志') == '出'):
                worksheet.set_row(r_row, cell_format=format)  # set the color of the first row to green

        '''
        for i in df_dealed.index:
            data=df_dealed[i].copy()
            if(data[7]=='出'):
                worksheet.set_row(i+1, cell_format=format)  # set the color of the first row to green
        '''
        df_dealed.to_excel(writer, sheet_name='Bank_statements', index=False)
        writer._save()


        #df_dealed.to_excel(csv_file,index=None)#, index=None, encoding='utf_8_sig')


if __name__ == '__main__':
    pd.set_option('display.precision', 2)
    #print(pd.get_option('display.precision'))
    base_num=2000
    cnt=-1
    pattern = re.compile("[^0-9]+")
    con = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
    cnt_sql=()

    while 1:
        cnt = cnt + 1
        sql = f'''SELECT
        t1.*,
        CASE WHEN t2.id IS NOT NULL THEN "是" ELSE "否" END,
        t2.`关联类型`
        FROM ( 
        SELECT
cc1.card_no
FROM
case_card cc1
INNER JOIN(
SELECT
card_no
FROM
bank_all_statements_lastest
GROUP BY
card_no

)tt ON tt.card_no=cc1.card_no
WHERE cc1.card_type='c15q'
        LIMIT {cnt*base_num},{base_num}
        )cc
        INNER JOIN(
        SELECT * FROM bank_all_statements
        )t1 ON t1.card_no=cc.card_no
        LEFT JOIN(
        SELECT
        uid,
        id,
        GROUP_CONCAT(`type`) AS `关联类型`
        FROM
        involved_bankcard_details
        group by id
        )t2 ON t2.id=t1.id
        
        ORDER BY t1.card_no ASC,t1.trade_date DESC'''

        data_sql = pd.read_sql(
            sql, con)


        logger.info('开始读取需要拆分银行卡 {} to {}...'.format(cnt*base_num,(cnt+1)*base_num) )
        #data_sql = pd.read_sql('SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END FROM case_card cc INNER JOIN( SELECT * FROM bank_all_statements)t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT card_no FROM case_card where card_type NOT IN("csf","cxj","clv2q"))t2 ON t2.card_no=t1.rival_card_no WHERE card_type IN("c02","c06") ORDER BY t1.card_no ASC,t1.trade_date DESC',con)
        #只拆分最新
        #data_sql = pd.read_sql('SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT card_no FROM card_to_sys_logs WHERE add_date=( SELECT MAX(add_date) FROM card_to_sys_logs) LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(cnt * base_num,base_num), con)
        #按月份拆分
        #data_sql = pd.read_sql('SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT card_no FROM card_to_sys_logs WHERE YEAR(add_date)=2024 AND MONTH(add_date)>=4 LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(cnt * base_num,base_num), con)
        # 拆分全部（无赌客）
        #data_sql=pd.read_sql('SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT card_no FROM case_card WHERE card_type NOT IN("c30","c31","csf","cxj","clv2q") LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(cnt*base_num,base_num),con)
        #拆分已冻结
        # data_sql = pd.read_sql(
        #     'SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT card_no FROM card_freeze_situation LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(
        #         cnt * base_num, base_num), con)
        #拆分赌客
        # data_sql = pd.read_sql(
        #     'SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT card_no FROM case_card WHERE card_type IN("c31") LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(
        #         cnt * base_num, base_num), con)
        # 拆分代理
        #拆分代理
        #data_sql=pd.read_sql('SELECT t1.*, CASE WHEN t2.card_no IS NOT NULL THEN "是" ELSE "否" END,sd.d_label AS `关联卡类型` FROM ( SELECT DISTINCT transactionCardNum AS card_no FROM bank_account_info WHERE IdNum IN("232103197008207024","532628199710172313","430124199501274219","14262319750101231X","500381199103281612","532131199005140712","430281198901143654") LIMIT {},{} )cc LEFT JOIN( SELECT * FROM bank_all_statements )t1 ON t1.card_no=cc.card_no LEFT JOIN( SELECT * FROM case_card WHERE card_type NOT IN("csf","cxj","clv2q") )t2 ON t2.card_no=t1.rival_card_no LEFT JOIN sys_dict sd ON sd.d_value=t2.card_type ORDER BY t1.card_no ASC,t1.trade_date DESC'.format(i*base_num,(i+1)*base_num),con)


        logger.info('读取需要拆分银行卡完成!')
        data_sql.columns=['id','案件名称','交易卡号','交易账号','交易方户名','交易时间','交易金额','交易余额','收付标志','交易对手帐卡号','现金标志','对手户名','对手身份证','对手开户银行','摘要说明','交易币种','交易网点名','交易发生地','交易是否成功','传票号','IP地址','MAC地址','对手交易余额','交易流水号','日志号','凭证种类','凭证号','交易柜员号','备注','商户名称','商户号','交易类型','交易结果','是否可能最新','是否修改过帐卡号','交易方证件号码','交易方证件类型','是否可能关联','关联类型']
        k=0
        if len(data_sql) == 0: break;

        cn=data_sql['交易卡号'][0]
        data_sql['交易卡号']=data_sql['交易卡号']

        for i in range(len(data_sql)):
            cni = data_sql['交易卡号'][i]
            if(cn!=cni or i==len(data_sql)-1):
                cn=pattern.sub('n',str(cn))
                xls_file=XLS_FILE.format(cn)
                cn=cni
                df_dealed=data_sql.loc[k:i-1].copy()
                k=i
                writer = pd.ExcelWriter(xls_file, engine='xlsxwriter')
                workbook = writer.book
                worksheet = workbook.add_worksheet('Bank_statements')
                writer.sheets['Bank_statements'] = worksheet
                format = workbook.add_format({'bg_color': '#5EA374'})
                format2 = workbook.add_format({'bg_color': '#F6FC14'})
                r_row = 0
                for row in df_dealed.itertuples():
                    r_row = r_row + 1
                    if (getattr(row,'是否可能关联') == '是'):
                        worksheet.set_row(r_row, cell_format=format2)  # set the color of the first row to yellow
                    elif (getattr(row, '收付标志') == 'out'):
                        worksheet.set_row(r_row, cell_format=format)  # set the color of the first row to green

                df_dealed.to_excel(writer, sheet_name='Bank_statements', index=False)
                writer._save()
                del df_dealed,writer
                logger.info("银行卡{}拆分完成!".format(data_sql['交易卡号'][i]))


        gc.collect()
        data_sql = pd.DataFrame()

        del data_sql
