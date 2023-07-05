import re, csv, pandas as pd, numpy as np

def alipay_format(filepath):

    with open(filepath, "r", encoding="gbk", newline="") as csvfile:
        lines = csvfile.readlines()

        csvdata = []
        # 截取以"---"开头的行中间的所有行
        flag = False
        for line in lines:
            if not flag:
                if line.startswith("----------------------"):
                    flag = True
                continue

            # 再遇到分割符时停止
            if line.startswith("----------------------------"):
                break
            # 去除空白字符
            l = re.sub(r"\s+,", ",", line)
            csvdata.append(l)

        csvreader = csv.DictReader(csvdata)
        fieldnames = ['交易创建时间', '商品名称', '交易对方', '收/支', '金额（元）']
        df_bookkeep = pd.DataFrame(csvreader).loc[:, fieldnames].rename(
            columns={'交易创建时间': '交易时间', '金额（元）': '金额(元)'}
        )

        df_bookkeep['交易时间'] = pd.to_datetime(
            df_bookkeep['交易时间'], format='%Y/%m/%d %H:%M:%S')
        df_bookkeep['金额(元)'] = pd.to_numeric(df_bookkeep['金额(元)'], errors="coerce")
        df_bookkeep['类型'] = np.nan
        df_bookkeep['支付方式'] = '支付宝'
        df_bookkeep['备注'] = np.nan
        df_bookkeep['收/支'] = df_bookkeep['收/支'].replace('不计收支', '/')

    return df_bookkeep