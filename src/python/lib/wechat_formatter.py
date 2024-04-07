import csv
import pandas as pd
import numpy as np

def wechat_format(filepath):
    with open(filepath, "r", encoding="utf-8-sig", newline="") as csvfile:
        lines = csvfile.readlines()
        csvdata = []
        start = False
        for line in lines:
            if not start:
                if line.startswith("----------------------"):
                    start = True
                continue
            csvdata.append(line.strip())

        csvreader = csv.DictReader(csvdata)
        fieldnames = ['交易时间', '商品', '交易对方', '收/支', '金额(元)']
        df_bookkeep = pd.DataFrame(csvreader).loc[:, fieldnames].rename(columns={'商品': '商品名称'})

        df_bookkeep['交易时间'] = pd.to_datetime(df_bookkeep['交易时间'], format='%Y-%m-%d %H:%M:%S')
        df_bookkeep['金额(元)'] = pd.to_numeric(df_bookkeep['金额(元)'].str.replace('¥', ''), errors="coerce")
        df_bookkeep['类型'] = np.nan
        df_bookkeep['支付方式'] = '微信支付'
        df_bookkeep['备注'] = np.nan

    return df_bookkeep
