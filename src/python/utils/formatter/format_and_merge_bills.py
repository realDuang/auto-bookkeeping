import os
import pandas as pd
from utils.formatter.wechat_formatter import wechat_format
from utils.formatter.alipay_formatter import alipay_format


def format_and_merge_bills(wechat_bill_files, alipay_bill_files):
    """
    格式化并合并微信和支付宝账单文件

    参数:
        wechat_bill_files: 微信账单文件列表
        alipay_bill_files: 支付宝账单文件列表

    返回:
        merged_bill_df: 合并后的账单DataFrame
    """
    # 处理微信账单文件
    wechat_bills = []
    for bill_path in wechat_bill_files:
        if os.path.exists(bill_path):
            try:
                bill_df = wechat_format(bill_path)
                wechat_bills.append(bill_df)
            except Exception as e:
                print(f"处理微信账单文件出错 {bill_path}: {str(e)}")

    # 处理支付宝账单文件
    alipay_bills = []
    for bill_path in alipay_bill_files:
        if os.path.exists(bill_path):
            try:
                bill_df = alipay_format(bill_path)
                alipay_bills.append(bill_df)
            except Exception as e:
                print(f"处理支付宝账单文件出错 {bill_path}: {str(e)}")

    # 合并所有微信账单
    wechat_bill_df = pd.DataFrame()
    if wechat_bills:
        wechat_bill_df = pd.concat(wechat_bills, ignore_index=True)

    # 合并所有支付宝账单
    alipay_bill_df = pd.DataFrame()
    if alipay_bills:
        alipay_bill_df = pd.concat(alipay_bills, ignore_index=True)

    # 按时间顺序合并账单
    merged_bill_df = pd.concat([alipay_bill_df, wechat_bill_df],
                               sort=True).sort_values(by='交易时间', ascending=True)

    # 整理列顺序
    column_order = ['交易时间', '类型', '金额(元)', '收/支', '支付方式', '交易对方', '商品名称', '备注']
    merged_bill_df = merged_bill_df.reindex(columns=column_order)

    # 过滤掉不计入收支的记录
    merged_bill_df = merged_bill_df[merged_bill_df['收/支'] != '/']

    return merged_bill_df
