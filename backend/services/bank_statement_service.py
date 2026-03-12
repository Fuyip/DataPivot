"""
银行流水处理服务
基于现有脚本重构，实现数据清洗和导入功能
"""
import os
import re
import zipfile
import tarfile
from typing import Dict, Optional, Callable
from pathlib import Path
import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from backend.services.case_service import get_case_database_url

# 导入 tools 目录下的 bank_config
import sys
from pathlib import Path
tools_dir = Path(__file__).parent.parent.parent / "tools"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from bank_config import NAME_DICT, REG_STR, REG_TIME_STR


class BankStatementProcessor:
    """银行流水处理器（基于现有脚本重构）"""

    def __init__(self, case_id: int, database_name: str, task_id: str, template_id: Optional[int] = None, db_session: Optional[object] = None):
        self.case_id = case_id
        self.database_name = database_name
        self.task_id = task_id
        self.template_id = template_id
        self.engine: Optional[Engine] = None

        # 动态加载规则配置
        if template_id and db_session:
            from backend.services.import_rule_service import load_template_config
            try:
                config = load_template_config(db_session, template_id)
                self.NAME_DICT = config['NAME_DICT']
                self.REG_STR = config['REG_STR']
                self.REG_TIME_STR = config['REG_TIME_STR']
                logger.info(f"已从模板加载规则配置: template_id={template_id}")
            except Exception as e:
                logger.warning(f"加载模板配置失败，使用默认配置: {e}")
                # 回退到硬编码配置
                self.NAME_DICT = NAME_DICT
                self.REG_STR = REG_STR
                self.REG_TIME_STR = REG_TIME_STR
        else:
            # 向后兼容：使用硬编码配置
            self.NAME_DICT = NAME_DICT
            self.REG_STR = REG_STR
            self.REG_TIME_STR = REG_TIME_STR
            logger.info("使用默认硬编码规则配置")

        # 统计信息
        self.statistics = {
            "人员信息": 0,
            "账户信息": 0,
            "子账户信息": 0,
            "强制措施信息": 0,
            "交易明细": 0,
            "失败信息": 0
        }
        self.error_files = []
        self.total_records = 0
        self.success_records = 0
        self.error_records = 0

    def _normalize_datetime_series(self, series: pd.Series) -> pd.Series:
        """将非法日期值归一化为 NaT，入库时会写入 NULL。"""
        cleaned = series.astype(str).str.replace(self.REG_TIME_STR, '', regex=True).str.strip()
        cleaned = cleaned.mask(cleaned.str.lower().isin(['', 'nan', 'nat', 'none']))
        cleaned = cleaned.mask(cleaned.str.fullmatch(r'0+'))
        cleaned = cleaned.mask(cleaned.str.len() < 8)

        normalized = pd.to_datetime(cleaned, errors='coerce')
        return normalized.where(normalized.notna(), np.nan)

    def connect_database(self):
        """连接案件数据库"""
        db_url = get_case_database_url(self.database_name)
        self.engine = create_engine(db_url, pool_pre_ping=True)
        logger.info(f"已连接到案件数据库: {self.database_name}")

    def extract_archives(self, directory: Path, progress_callback: Optional[Callable] = None):
        """
        解压所有压缩文件（递归）

        Args:
            directory: 目录路径
            progress_callback: 进度回调函数
        """
        logger.info(f"开始解压文件: {directory}")

        if progress_callback:
            progress_callback("正在解压文件...")

        # 第一轮解压
        self._extract_all_in_directory(directory)

        # 第二轮解压（处理嵌套压缩包）
        self._extract_all_in_directory(directory)

        logger.info("文件解压完成")

    def _extract_all_in_directory(self, directory: Path):
        """解压目录中的所有压缩文件"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                try:
                    if zipfile.is_zipfile(file_path):
                        with zipfile.ZipFile(file_path, 'r') as zip_ref:
                            # 处理中文文件名编码问题
                            for member in zip_ref.namelist():
                                # 跳过目录条目
                                if member.endswith('/'):
                                    continue

                                member_name = member

                                # 尝试修复文件名编码
                                # zipfile 默认用 cp437 解码,但实际可能是 UTF-8 或 GBK
                                try:
                                    # 先转回字节
                                    member_bytes = member.encode('cp437')

                                    # 尝试用 UTF-8 解码(优先)
                                    try:
                                        member_name = member_bytes.decode('utf-8')
                                    except:
                                        # 如果 UTF-8 失败,尝试 GB18030
                                        try:
                                            member_name = member_bytes.decode('gb18030')
                                        except:
                                            # 都失败就用原始名称
                                            member_name = member
                                except:
                                    # 如果转换失败,使用原始文件名
                                    member_name = member

                                # 提取文件
                                source = zip_ref.open(member)
                                target_path = Path(root) / member_name
                                target_path.parent.mkdir(parents=True, exist_ok=True)

                                with open(target_path, 'wb') as target:
                                    target.write(source.read())
                        file_path.unlink()  # 删除压缩包
                        logger.debug(f"已解压ZIP文件: {file}")
                    elif tarfile.is_tarfile(file_path):
                        with tarfile.open(file_path, 'r') as tar_ref:
                            tar_ref.extractall(root)
                        file_path.unlink()
                        logger.debug(f"已解压TAR文件: {file}")
                except Exception as e:
                    logger.error(f"解压文件失败 {file_path}: {e}")

    def count_files(self, directory: Path) -> Dict[str, int]:
        """
        统计各类型文件数量

        Args:
            directory: 目录路径

        Returns:
            Dict[str, int]: 各类型文件数量
        """
        file_counts = {
            "人员信息": 0,
            "账户信息": 0,
            "子账户信息": 0,
            "强制措施信息": 0,
            "交易明细": 0,
            "失败信息": 0
        }

        patterns = [
            ("人员信息", lambda f: "人员信息" in f and f.endswith(".csv")),
            ("账户信息", lambda f: "账户信息" in f and "子账户信息" not in f and f.endswith(".csv")),
            ("子账户信息", lambda f: "子账户信息" in f and f.endswith(".csv")),
            ("强制措施信息", lambda f: "强制措施信息" in f and f.endswith(".csv")),
            ("交易明细", lambda f: "交易明细" in f and f.endswith(".csv")),
            ("失败信息", lambda f: "任务信息(失败)" in f and f.endswith(".csv"))
        ]

        for root, dirs, files in os.walk(directory):
            for filename in files:
                for data_type, pattern_func in patterns:
                    if pattern_func(filename):
                        file_counts[data_type] += 1

        logger.info(f"文件统计完成: {file_counts}")
        return file_counts

    def truncate_tmp_tables(self):
        """清空临时表"""
        tmp_tables = [
            'bank_people_info_tmp',
            'bank_account_info_tmp',
            'bank_sub_account_info_tmp',
            'bank_coercive_action_info_tmp',
            'bank_all_statements_tmp',
            'bank_apply_fail_tmp'
        ]

        with self.engine.connect() as conn:
            for table in tmp_tables:
                conn.execute(text(f'TRUNCATE TABLE {table}'))
            conn.commit()

        logger.info("临时表清空完成")

    def extract_first_number(self, string):
        """从字符串中提取第一个数字"""
        match = re.search(r'\d+', str(string))
        return match.group() if match else None

    def process_dataframe(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        根据配置处理DataFrame（复用现有脚本逻辑）

        Args:
            df: 原始DataFrame
            data_type: 数据类型（如'人员信息'、'账户信息'等）

        Returns:
            处理后的DataFrame
        """
        dfn = pd.DataFrame()

        for field_name, (column_name, field_type) in self.NAME_DICT[data_type].items():
            if field_name == 'source' or field_type in ['none', 'source']:
                continue

            # 基础清洗：去除特殊字符
            dfn[field_name] = df[column_name].astype(str).str.replace(self.REG_STR, '', regex=True)

            # 根据字段类型进行特殊处理
            if field_type == 'str':
                continue
            elif field_type == 'float':
                dfn[field_name] = dfn[field_name].mask(dfn[field_name] == "", np.nan)
            elif field_type == 'datetime':
                dfn[field_name] = self._normalize_datetime_series(df[column_name])
            elif field_type == 'card_no':
                dfn[field_name] = dfn[field_name].apply(self.extract_first_number)
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

    def process_files(self, directory: Path, progress_callback: Optional[Callable] = None):
        """
        处理所有CSV文件

        Args:
            directory: 目录路径
            progress_callback: 进度回调函数
        """
        file_configs = [
            ('人员信息', 'bank_people_info_tmp', lambda f: '人员信息' in f and f.endswith('.csv')),
            ('账户信息', 'bank_account_info_tmp', lambda f: '账户信息' in f and '子账户信息' not in f and f.endswith('.csv')),
            ('子账户信息', 'bank_sub_account_info_tmp', lambda f: '子账户信息' in f and f.endswith('.csv')),
            ('强制措施信息', 'bank_coercive_action_info_tmp', lambda f: '强制措施信息' in f and f.endswith('.csv')),
            ('交易明细', 'bank_all_statements_tmp', lambda f: '交易明细' in f and f.endswith('.csv')),
            ('失败信息', 'bank_apply_fail_tmp', lambda f: '任务信息(失败)' in f and f.endswith('.csv'))
        ]

        file_counts = self.count_files(directory)
        total_files = sum(file_counts.values())
        processed = 0

        logger.info(f"开始处理文件，总计: {total_files}")

        if total_files == 0:
            return

        for root, dirs, files in os.walk(directory):
            for filename in files:
                for data_type, table_name, pattern_func in file_configs:
                    if pattern_func(filename):
                        try:
                            self._process_single_file(
                                Path(root) / filename,
                                data_type,
                                table_name
                            )

                        except Exception as e:
                            logger.error(f"处理文件失败 {filename}: {e}")
                            self.error_files.append(filename)
                            self.error_records += 1
                        finally:
                            processed += 1
                            if progress_callback:
                                progress = 30 + (processed / total_files * 60)  # 30-90%
                                progress_callback(
                                    f"正在处理: {filename}",
                                    progress,
                                    processed,
                                    total_files
                                )

        logger.info(f"文件处理完成，成功: {processed}, 失败: {len(self.error_files)}")

    def _process_single_file(self, file_path: Path, data_type: str, table_name: str):
        """处理单个CSV文件"""
        try:
            # 读取CSV
            with open(file_path, encoding='gbk', errors='ignore') as f:
                df = pd.read_csv(f, low_memory=False, on_bad_lines='skip')

            # 处理数据
            dfn = self.process_dataframe(df, data_type)

            # 插入数据库
            if not dfn.empty:
                dfn.to_sql(name=table_name, con=self.engine,
                          if_exists='append', index=False)

                record_count = len(dfn)
                self.statistics[data_type] += record_count
                self.total_records += record_count
                self.success_records += record_count

                logger.debug(f"文件处理成功: {file_path.name}, 记录数: {record_count}")

        except Exception as e:
            logger.error(f"处理文件 {file_path.name} 失败: {e}")
            raise

    def transfer_to_final_tables(self, progress_callback: Optional[Callable] = None):
        """从临时表转移到正式表"""
        if progress_callback:
            progress_callback("正在转移数据到正式表...", 90)

        # 账号转换（仅交易明细）
        self._account_card_conversion()

        # 转移数据
        tables = [
            'bank_people_info',
            'bank_account_info',
            'bank_sub_account_info',
            'bank_coercive_action_info',
            'bank_all_statements',
            'bank_apply_fail'
        ]

        for table in tables:
            self._transfer_table(table)

        logger.info("数据转移完成")

    def _account_card_conversion(self):
        """账号卡号转换"""
        logger.info("开始账号卡号转换...")
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

        with self.engine.connect() as conn:
            result = conn.execute(sql)
            conn.commit()
            logger.info(f"账号卡号转换完成，操作行数: {result.rowcount}")

    def _transfer_table(self, table_name: str):
        """转移单个表的数据。"""

        with self.engine.connect() as conn:
            # 获取总记录数
            count_sql = text(f"SELECT COUNT(*) FROM {table_name}_tmp")
            total = conn.execute(count_sql).scalar()

            if total == 0:
                logger.info(f"{table_name} 无数据需要转移")
                return

            sql = text(f"""
                INSERT IGNORE INTO {table_name}
                SELECT * FROM {table_name}_tmp
            """)
            result = conn.execute(sql)
            conn.commit()
            logger.info(f"{table_name} 转移完成，操作行数: {result.rowcount}")

    def _execute_insert_select(self, conn, insert_sql: str):
        """整表执行 INSERT ... SELECT 语句。"""
        result = conn.execute(text(insert_sql))
        conn.commit()
        logger.debug(f"INSERT SELECT 执行完成，操作行数: {result.rowcount}")

    def execute_post_processing_sql(self, progress_callback: Optional[Callable] = None):
        """
        执行后处理SQL脚本
        在数据导入完成后，执行一系列SQL脚本生成分析表
        """
        if progress_callback:
            progress_callback("执行后处理SQL脚本...", 95)

        sql_scripts = [
            ("生成bank_all_statements_lastest", "/Users/yipf/DataPivot项目/DataPivot/sql/生成bank_all_statements_lastest.sql"),
            ("生成involved_bankcard_details", "/Users/yipf/DataPivot项目/DataPivot/sql/生成involved_bankcard_details.sql"),
            ("生成bank_statements及turn", "/Users/yipf/DataPivot项目/DataPivot/sql/生成bank_statements及turn.sql"),
            ("生成bank_all_statements_turn", "/Users/yipf/DataPivot项目/DataPivot/sql/生成bank_all_statements_turn.sql")
        ]

        for script_name, script_path in sql_scripts:
            try:
                logger.info(f"开始执行SQL脚本: {script_name}")

                # 读取SQL文件
                with open(script_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # 分割多个SQL语句（按分号分割）
                sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

                # 执行每个SQL语句
                with self.engine.connect() as conn:
                    for sql_stmt in sql_statements:
                        # 判断是否是大数据量的INSERT语句
                        if sql_stmt.upper().startswith('INSERT') and 'SELECT' in sql_stmt.upper():
                            self._execute_insert_select(conn, sql_stmt)
                        else:
                            # 直接执行（TRUNCATE、DELETE等）
                            conn.execute(text(sql_stmt))
                            conn.commit()

                logger.info(f"SQL脚本执行成功: {script_name}")

            except Exception as e:
                logger.error(f"执行SQL脚本失败 {script_name}: {e}")
                raise Exception(f"执行后处理SQL脚本失败: {script_name}, 错误: {str(e)}")

        logger.info("所有后处理SQL脚本执行完成")

    def get_statistics(self) -> Dict:
        """获取处理统计信息"""
        return {
            "statistics": self.statistics,
            "total_records": self.total_records,
            "success_records": self.success_records,
            "error_records": self.error_records,
            "error_files": self.error_files
        }

    def cleanup(self):
        """清理资源"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
