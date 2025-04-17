import numpy as np
import pandas as pd
from typing import Dict


def extract_transaction_fields(row: pd.Series) -> Dict[str, str]:
    """
    从DataFrame行中提取交易相关字段
    """
    fields = {}
    fields['merchant'] = str(row['交易对方']) if not pd.isna(row['交易对方']) else ""
    fields['product'] = str(row['商品名称']) if not pd.isna(row['商品名称']) else ""
    fields['category'] = str(row['类型']) if not pd.isna(row['类型']) else ""
    fields['pay_type'] = str(row['支付方式']) if not pd.isna(row['支付方式']) else ""
    fields['pay_time'] = str(row['交易时间']) if not pd.isna(row['交易时间']) else ""
    fields['amount'] = str(row['金额(元)']) if not pd.isna(row['金额(元)']) else ""
    fields['i_o'] = str(row['收/支']) if not pd.isna(row['收/支']) else ""
    fields['remark'] = str(row['备注']) if not pd.isna(row['备注']) else ""

    return fields


def extract_time_features(time_str: str) -> str:
    """
    从交易时间中提取时间特征
    """
    if not time_str:
        return "unknown"

    try:
        dt = pd.to_datetime(time_str)
        hour = dt.hour

        if 21 <= hour < 7:
            return "night"
        elif 7 <= hour < 11:
            return "morning"
        elif 11 <= hour < 14:
            return "noon"
        elif 14 <= hour < 17:
            return "afternoon"
        else:
            return "evening"
    except Exception:
        return "unknown"


def extract_amount_features(amount_str: str) -> tuple:
    """从交易金额中提取特征"""
    try:
        amount = float(amount_str.replace(',', '')) if amount_str else 0.0
    except (ValueError, AttributeError):
        return 0.0, "unknown"

    normalized_amount = round(amount, 2)

    # 金额级别
    if amount < 30:
        amount_size = "small"
    elif 30 <= amount < 200:
        amount_size = "medium"
    elif amount >= 200:
        amount_size = "large"
    else:
        amount_size = "unknown"

    return normalized_amount, amount_size
