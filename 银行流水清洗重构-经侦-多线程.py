"""
银行流水数据清洗处理脚本
功能：解压、读取、清洗、导入银行流水数据到数据库
"""
import os
import re
import time
import shutil
import zipfile
import tarfile
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser

import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy.sql import text

from database import engine
from bank_config import NAME_DICT, REG_STR, REG_TIME_STR


# ==================== 配置初始化 ====================
conf = ConfigParser()
conf.read(r'.\config.ini', encoding='utf-8')

# 文件路径配置
BASE_DIR = os.path.join(os.getcwd(), 'bank_statements')
RAW_DIR = os.path.join(BASE_DIR, 'raw')
PROCESSING_DIR = os.path.join(BASE_DIR, 'processing')
PROCESSED_DIR = os.path.join(BASE_DIR, 'processed')
ERROR_DIR = os.path.join(BASE_DIR, 'error_files')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 确保目录存在
for directory in [RAW_DIR, PROCESSING_DIR, PROCESSED_DIR, ERROR_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# 日志配置
log_file = os.path.join(LOG_DIR, f"银行流水清洗_{time.strftime('%Y%m%d_%H%M%S')}.log")
logger.add(log_file, format="{time} {level} {message}", level="INFO")

# 使用配置文件中的路径或默认使用processing目录
dir_path = conf['path'].get('statements', PROCESSING_DIR) if conf.has_option('path', 'statements') else PROCESSING_DIR

# 全局计数器
filesnum = [0, 0, 0, 0, 0, 0]  # 各类型文件总数
fcount = [0, 0, 0, 0, 0, 0]    # 各类型文件已处理数
successnum = 0                  # 成功处理的交易明细数
error_cnt = 0                   # 错误文件计数


# ==================== 工具函数 ====================
def extract_first_number(string):
    """从字符串中提取第一个数字"""
    match = re.search(r'\d+', str(string))
    return match.group() if match else None


def extract_archive(file_path, extract_dir):
    """解压单个压缩文件"""
    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        elif tarfile.is_tarfile(file_path):
            with tarfile.open(file_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
            return True
    except Exception as e:
        logger.error(f"解压文件失败 {file_path}: {e}")
    return False


def extract_all_nested_archives(extract_dir):
    """递归解压嵌套的压缩文件"""
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if extract_archive(file_path, root):
                os.remove(file_path)


def extract_all_archives(directory):
    """解压目录下所有压缩文件"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if extract_archive(file_path, root):
                    os.remove(file_path)
                    extract_all_nested_archives(os.path.splitext(file_path)[0])
            except Exception as e:
                logger.error(f"解压文件出错 {file_path}: {e}")


def copy_to_error_folder(filepath, filename):
    """将错误文件复制到error_files文件夹"""
    global error_cnt
    src_path = os.path.join(filepath, filename)
    dst_path = os.path.join(ERROR_DIR, f'err_{error_cnt}_{filename}')
    shutil.copy(src_path, dst_path)
    error_cnt += 1


# ==================== 数据处理函数 ====================
def process_dataframe(df, data_type):
    """
    根据配置处理DataFrame

    Args:
        df: 原始DataFrame
        data_type: 数据类型（如'人员信息'、'账户信息'等）

    Returns:
        处理后的DataFrame
    """
    dfn = pd.DataFrame()

    for field_name, (column_name, field_type) in NAME_DICT[data_type].items():
        if field_name == 'source' or field_type in ['none', 'source']:
            continue

        # 基础清洗：去除特殊字符
        dfn[field_name] = df[column_name].astype(str).str.replace(REG_STR, '', regex=True)

        # 根据字段类型进行特殊处理
        if field_type == 'str':
            continue
        elif field_type == 'float':
            dfn[field_name] = dfn[field_name].mask(dfn[field_name] == "", np.nan)
        elif field_type == 'datetime':
            dfn[field_name] = dfn[field_name].astype(str).str.replace(REG_TIME_STR, '', regex=True)
            dfn[field_name] = dfn[field_name].mask(dfn[field_name] == "", np.nan)
        elif field_type == 'card_no':
            dfn[field_name] = dfn[field_name].apply(extract_first_number)
        elif field_type == 'tag':
            dfn[field_name] = dfn[field_name].str.replace(
                r'进|转入|入|C|贷', 'in', regex=True
            ).str.replace(
                r'出|转出|出|D|借', 'out', regex=True
            )

    # 删除所有列都为空的行
    dfn = dfn.dropna(how='all')

    # 交易明细特殊处理
    if data_type == '交易明细':
        dfn['dict_trade_tag'] = dfn['dict_trade_tag'].fillna('').astype(str)
        if not dfn.empty:
            # 如果card_no为空，使用card_account
            dfn['card_no'] = np.where(
                (dfn['card_no'].isnull() | (dfn['card_no'] == '')),
                dfn['card_account'],
                dfn['card_no']
            )
            # 只保留收付标志为in或out的记录
            dfn = dfn[dfn['dict_trade_tag'].isin(['in', 'out'])]

    return dfn


def insert_to_sql_tmp(filename, filepath, fcount_idx, filesnum_idx, data_type, table_name):
    """
    读取CSV文件并插入到临时表

    Args:
        filename: 文件名
        filepath: 文件路径
        fcount_idx: 当前处理文件索引
        filesnum_idx: 文件总数
        data_type: 数据类型
        table_name: 目标表名
    """
    dir_str = os.path.join(filepath, filename)
    logger.info(f"导入文件-{dir_str} {fcount_idx} OF {filesnum_idx}")

    try:
        # 读取CSV文件
        with open(os.path.join(filepath, filename), encoding='gbk', errors='ignore') as f:
            df = pd.read_csv(f, low_memory=False, on_bad_lines='skip')

        # 处理数据
        dfn = process_dataframe(df, data_type)

        # 插入数据库
        if not dfn.empty:
            dfn.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    except Exception as e:
        logger.error(f"处理文件 {filename} 时发生异常: {e}")
        copy_to_error_folder(filepath, filename)


def process_file(filename, filepath, fcount_idx, filesnum_idx, data_type, table_name):
    """多线程处理单个文件的包装函数"""
    insert_to_sql_tmp(filename, filepath, fcount_idx, filesnum_idx, data_type, table_name)


def process_files_in_parallel(file_list, filepath, fcount_idx, filesnum_idx, data_type, table_name):
    """并行处理文件列表"""
    with ThreadPoolExecutor(max_workers=25000) as executor:
        futures = [
            executor.submit(process_file, filename, filepath, fcount_idx, filesnum_idx, data_type, table_name)
            for filename in file_list
        ]
        for future in futures:
            future.result()


# ==================== 数据库操作函数 ====================
def account_and_card_number_conversion():
    """账号卡号转换"""
    logger.info("开始对返回账号转换...")
    sql = text("""
        UPDATE bank_all_statements_tmp bas
        INNER JOIN (
            SELECT *
            FROM bank_account_info
            WHERE tradingAccountNum <> transactionCardNum
        ) t1 ON t1.tradingAccountNum = bas.card_no
        SET bas.card_no = t1.transactionCardNum,
            bas.is_card_no_change = 1
    """)

    with engine.connect() as conn:
        res_obj = conn.execute(sql)
        conn.commit()
        logger.info(f"对帐卡号转换完成!操作行数{res_obj.rowcount}!")


def ignore_insert_to_sql(table_name):
    """
    从临时表转移数据到正式表（去重）

    Args:
        table_name: 目标表名
    """
    # 交易明细表需要先进行账号转换
    if table_name == 'bank_all_statements':
        account_and_card_number_conversion()
        time.sleep(20)

    # 构建SQL
    if table_name == 'bank_all_statements' and 'error_files' in dir_path:
        sql = text(f"""
            INSERT IGNORE INTO {table_name}
            SELECT * FROM {table_name}_tmp
            WHERE is_card_no_change = 1
        """)
    else:
        sql = text(f"""
            INSERT IGNORE INTO {table_name}
            SELECT * FROM {table_name}_tmp
        """)

    logger.info(f"开始对{table_name}转移去重...")
    with engine.connect() as conn:
        res_obj = conn.execute(sql)
        conn.commit()
        logger.info(f"对{table_name}转移去重完成!操作行数{res_obj.rowcount}!")


def truncate_tmp_tables():
    """清空所有临时表"""
    tmp_tables = [
        'bank_people_info_tmp',
        'bank_account_info_tmp',
        'bank_sub_account_info_tmp',
        'bank_coercive_action_info_tmp',
        'bank_apply_fail_tmp'
    ]

    # 交易明细临时表根据条件清空
    if successnum == 0 and 'error_files' not in dir_path:
        tmp_tables.append('bank_all_statements_tmp')

    with engine.connect() as conn:
        for table in tmp_tables:
            conn.execute(text(f'TRUNCATE TABLE {table}'))
        conn.commit()

    logger.info("临时表清空完成")


def count_files():
    """统计各类型文件数量"""
    file_patterns = [
        ('人员信息', 0, lambda f: '人员信息' in f and f.endswith('.csv')),
        ('账户信息', 1, lambda f: '账户信息' in f and '子账户信息' not in f and f.endswith('.csv')),
        ('子账户信息', 2, lambda f: '子账户信息' in f and f.endswith('.csv')),
        ('强制措施信息', 3, lambda f: '强制措施信息' in f and f.endswith('.csv')),
        ('交易明细', 4, lambda f: '交易明细' in f and f.endswith('.csv')),
        ('失败信息', 5, lambda f: '任务信息(失败)' in f and f.endswith('.csv'))
    ]

    for filepath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            for name, idx, pattern_func in file_patterns:
                if pattern_func(filename):
                    filesnum[idx] += 1

    logger.info(f"文件统计完成: {dict(zip(['人员', '账户', '子账户', '强制措施', '交易明细', '失败'], filesnum))}")


# ==================== 主流程 ====================
def move_files_to_processing():
    """将raw目录中的文件移动到processing目录"""
    moved_count = 0
    for filename in os.listdir(RAW_DIR):
        src = os.path.join(RAW_DIR, filename)
        if os.path.isfile(src):
            dst = os.path.join(PROCESSING_DIR, filename)
            shutil.move(src, dst)
            moved_count += 1
            logger.info(f"移动文件: {filename} -> processing/")
    return moved_count


def move_processed_files():
    """将processing目录中已处理的文件移动到processed目录"""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    archive_dir = os.path.join(PROCESSED_DIR, timestamp)
    os.makedirs(archive_dir, exist_ok=True)

    moved_count = 0
    for filename in os.listdir(PROCESSING_DIR):
        src = os.path.join(PROCESSING_DIR, filename)
        if os.path.isfile(src):
            dst = os.path.join(archive_dir, filename)
            shutil.move(src, dst)
            moved_count += 1

    if moved_count > 0:
        logger.info(f"已将 {moved_count} 个文件归档到: {archive_dir}")
    return moved_count


def main():
    """主处理流程"""
    logger.info("=" * 50)
    logger.info("银行流水清洗程序启动")
    logger.info("=" * 50)

    # 1. 移动raw目录文件到processing目录
    logger.info("检查raw目录...")
    moved = move_files_to_processing()
    if moved > 0:
        logger.info(f"已移动 {moved} 个文件到processing目录")
    else:
        logger.info("raw目录无新文件")

    # 2. 解压文件
    logger.info("开始解压文件...")
    for _ in range(2):
        extract_all_archives(dir_path)
    logger.info("文件解压完成")

    # 2. 统计文件数量
    count_files()

    # 3. 清空临时表
    truncate_tmp_tables()

    # 4. 处理文件
    file_configs = [
        ('人员信息', 0, 'bank_people_info_tmp', lambda f: '人员信息' in f and f.endswith('.csv')),
        ('账户信息', 1, 'bank_account_info_tmp', lambda f: '账户信息' in f and '子账户信息' not in f and f.endswith('.csv')),
        ('子账户信息', 2, 'bank_sub_account_info_tmp', lambda f: '子账户信息' in f and f.endswith('.csv')),
        ('强制措施信息', 3, 'bank_coercive_action_info_tmp', lambda f: '强制措施信息' in f and f.endswith('.csv')),
        ('交易明细', 4, 'bank_all_statements_tmp', lambda f: '交易明细' in f and f.endswith('.csv')),
        ('失败信息', 5, 'bank_apply_fail_tmp', lambda f: '任务信息(失败)' in f and f.endswith('.csv'))
    ]

    logger.info("开始处理文件...")
    for filepath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            for data_type, idx, table_name, pattern_func in file_configs:
                if pattern_func(filename):
                    fcount[idx] += 1

                    # 交易明细跳过已处理的文件
                    if data_type == '交易明细' and fcount[idx] < successnum:
                        continue

                    process_files_in_parallel(
                        [filename], filepath, fcount[idx], filesnum[idx], data_type, table_name
                    )

    # 5. 数据转移到正式表
    logger.info("开始数据转移...")
    tables = [
        'bank_people_info',
        'bank_account_info',
        'bank_sub_account_info',
        'bank_coercive_action_info',
        'bank_all_statements',
        'bank_apply_fail'
    ]

    for table in tables:
        ignore_insert_to_sql(table)

    # 6. 归档已处理文件
    logger.info("归档已处理文件...")
    move_processed_files()

    logger.info("=" * 50)
    logger.info("银行流水清洗程序完成")
    logger.info(f"错误文件数: {error_cnt}")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
