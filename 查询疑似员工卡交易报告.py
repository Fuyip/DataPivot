"""
疑似员工卡交易报告生成脚本

功能：查询与疑似员工卡(c15q)有交易往来的银行流水记录
输入：数据库中的 case_card 和 bank_all_statements 表
输出：Excel报告，包含交易明细和卡类型标签

使用方法：
    python 查询疑似员工卡交易报告.py
"""
import os
import pandas as pd
from datetime import datetime
from database import engine

# SQL查询
SQL_QUERY = """
SELECT
    t3.card_no AS `卡号`,
    t3.source AS `卡名`,
    sd2.d_label AS `卡类型`,
    t2.trade_date AS `交易时间`,
    t2.trade_money AS `交易金额`,
    t2.trade_balance AS `交易余额`,
    t2.dict_trade_tag AS `交易方向`,
    t1.card_no AS `对手卡号`,
    t1.source AS `对手卡名`,
    sd1.d_label AS `对手卡标签`,
    t1.bank_name AS `对手卡归属`,
    t2.transaction_outlet_name AS `交易网点`,
    t2.remark AS `交易备注`
FROM (
    SELECT *
    FROM case_card
    WHERE card_type='c15q'
) t1
INNER JOIN (
    SELECT *
    FROM bank_all_statements
) t2 ON t2.rival_card_no=t1.card_no
LEFT JOIN (
    SELECT *
    FROM case_card
) t3 ON t3.card_no=t2.card_no
LEFT JOIN xinglian.sys_dict sd1 ON sd1.d_value=t1.card_type
LEFT JOIN xinglian.sys_dict sd2 ON sd2.d_value=t3.card_type
"""


def main():
    """主函数"""
    try:
        print("开始执行查询...")
        start_time = datetime.now()

        # 执行SQL查询
        df = pd.read_sql(SQL_QUERY, con=engine)

        # 处理数据
        df = df.fillna('')  # 将NULL值替换为空字符串

        # 格式化数值列
        if '交易金额' in df.columns:
            df['交易金额'] = pd.to_numeric(df['交易金额'], errors='coerce').round(2)
        if '交易余额' in df.columns:
            df['交易余额'] = pd.to_numeric(df['交易余额'], errors='coerce').round(2)

        # 确保输出目录存在
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)

        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d')
        output_path = os.path.join(output_dir, f'疑似员工卡交易报告_{timestamp}.xlsx')

        # 生成Excel报告
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='交易明细', index=False)

        # 计算执行时间
        elapsed_time = (datetime.now() - start_time).total_seconds()

        # 输出成功信息
        print(f"\n报告生成成功！")
        print(f"文件路径: {output_path}")
        print(f"记录数量: {len(df)}")
        print(f"执行时间: {elapsed_time:.2f}秒")

    except Exception as e:
        print(f"\n错误: 报告生成失败")
        print(f"错误详情: {str(e)}")
        raise


if __name__ == '__main__':
    main()
