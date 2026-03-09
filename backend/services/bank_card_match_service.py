from typing import List, Dict
import pandas as pd
from io import BytesIO
from sqlalchemy import text
from database import get_system_db


class BankCardMatchService:
    """银行卡归属匹配服务"""

    @staticmethod
    def match_single_card(card_no: str) -> Dict:
        """匹配单个银行卡"""
        # 复用现有的匹配逻辑
        from backend.services.case_card_service import CaseCardService
        return CaseCardService.match_bank_name(card_no)

    @staticmethod
    def batch_match(card_numbers: List[str]) -> List[Dict]:
        """批量匹配银行卡（优化版 - 真正的批量查询）"""
        if not card_numbers:
            return []

        # 清理卡号
        clean_cards = [card.strip() for card in card_numbers if card.strip()]
        if not clean_cards:
            return []

        # 限制最多100个
        if len(clean_cards) > 100:
            clean_cards = clean_cards[:100]

        db = next(get_system_db())
        try:
            # 先获取所有可能的 bin 长度和卡长度组合
            results_dict = {}

            # 按卡号长度分组，提高查询效率
            cards_by_length = {}
            for card_no in clean_cards:
                length = len(card_no)
                if length not in cards_by_length:
                    cards_by_length[length] = []
                cards_by_length[length].append(card_no)

            # 对每个长度组进行批量查询
            for card_len, cards in cards_by_length.items():
                # 获取该长度对应的所有 bin 规则
                bin_sql = text("""
                    SELECT bin, bin_len, bank_name
                    FROM bank_bin
                    WHERE card_len = :card_len
                    ORDER BY bin_len DESC
                """)

                bin_rules = db.execute(bin_sql, {"card_len": card_len}).fetchall()

                # 为每个卡号匹配
                for card_no in cards:
                    matched = False
                    for bin_code, bin_len, bank_name in bin_rules:
                        if card_no.startswith(bin_code):
                            # 找到匹配的 BIN，查询对应的银行名称
                            bank_sql = text("""
                                SELECT to_bank
                                FROM sy_bank
                                WHERE from_bank = :bank_name AND sys = 'jz'
                                LIMIT 1
                            """)
                            result = db.execute(bank_sql, {"bank_name": bank_name}).fetchone()

                            if result and result[0]:
                                results_dict[card_no] = {
                                    "card_no": card_no,
                                    "bank_name": result[0],
                                    "matched": True
                                }
                            else:
                                results_dict[card_no] = {
                                    "card_no": card_no,
                                    "bank_name": bank_name,
                                    "matched": True
                                }
                            matched = True
                            break

                    if not matched:
                        results_dict[card_no] = {
                            "card_no": card_no,
                            "bank_name": None,
                            "matched": False
                        }

            # 按原始顺序返回结果
            return [results_dict[card_no] for card_no in clean_cards if card_no in results_dict]
        finally:
            db.close()

    @staticmethod
    def export_to_excel(match_results: List[Dict]) -> BytesIO:
        """导出匹配结果为Excel"""
        df = pd.DataFrame(match_results)

        # 重命名列
        df.columns = ['银行卡号', '银行名称', '是否匹配']

        # 转换匹配状态为中文
        df['是否匹配'] = df['是否匹配'].map({True: '是', False: '否'})

        # 导出到Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='银行卡匹配结果')

        output.seek(0)
        return output
