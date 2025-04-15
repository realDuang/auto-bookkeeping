import numpy as np
import pandas as pd


def extract_time_features(transaction_time: str) -> np.ndarray:
    """从交易时间中提取时间特征"""
    try:
        dt = pd.to_datetime(transaction_time)

        # 基础时间特征
        hour = dt.hour / 24.0
        day_of_week = dt.dayofweek / 6.0
        month = (dt.month - 1) / 11.0

        # 消费场景特征
        is_weekend = 1.0 if dt.dayofweek >= 5 else 0.0
        is_morning = 1.0 if 5 <= dt.hour < 12 else 0.0
        is_afternoon = 1.0 if 12 <= dt.hour < 18 else 0.0
        is_evening = 1.0 if 18 <= dt.hour < 22 else 0.0
        is_night = 1.0 if dt.hour >= 22 or dt.hour < 5 else 0.0

        # 工资日特征
        is_salary_day = 1.0 if dt.day in [10, 15, 20, 25, 30, 31, 1] else 0.0

        return np.array([hour, day_of_week, month, is_weekend,
                         is_morning, is_afternoon, is_evening, is_night,
                         is_salary_day])
    except:
        # 解析失败返回默认值
        return np.zeros(9)


def extract_account_features(account: str) -> np.ndarray:
    """从账户信息中提取特征"""
    # 支付方式特征
    is_credit_card = 1.0 if account and (
        '信用卡' in account or 'credit' in account.lower()) else 0.0
    is_debit_card = 1.0 if account and (
        '储蓄卡' in account or '借记卡' in account.lower()) else 0.0
    is_alipay = 1.0 if account and (
        '支付宝' in account or 'alipay' in account.lower()) else 0.0
    is_wechat = 1.0 if account and (
        '微信' in account or 'wechat' in account.lower()) else 0.0

    return np.array([is_credit_card, is_debit_card, is_alipay, is_wechat])


def extract_amount_features(amount: float) -> np.ndarray:
    """从交易金额中提取特征"""
    if amount is None:
        return np.zeros(4)

    # 金额标准化
    normalized_amount = min(1.0, amount / 10000.0)

    # 金额级别
    is_small = 1.0 if amount < 50 else 0.0
    is_medium = 1.0 if 50 <= amount < 500 else 0.0
    is_large = 1.0 if amount >= 500 else 0.0

    return np.array([normalized_amount, is_small, is_medium, is_large])
