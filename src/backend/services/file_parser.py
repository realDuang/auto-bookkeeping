import os
import pandas as pd
import tempfile
from utils.formatter.alipay_formatter import alipay_format
from utils.formatter.wechat_formatter import wechat_format

def parse_file(file):
    """
    解析上传的文件并转换为统一格式
    
    Args:
        file: 上传的文件对象
        
    Returns:
        格式化后的DataFrame
    """
    # 创建临时文件
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    os.close(fd)
    
    try:
        # 保存上传的文件
        file.save(temp_path)
        
        # 尝试识别文件类型并格式化
        try:
            # 首先尝试作为支付宝账单解析
            df = alipay_format(temp_path)
            if df.shape[0] > 0:
                return df.to_dict(orient='records')
        except:
            pass
        
        try:
            # 如果不是支付宝账单，尝试作为微信账单解析
            df = wechat_format(temp_path)
            if df.shape[0] > 0:
                return df.to_dict(orient='records')
        except:
            pass
        
        # 如果无法识别文件格式，返回错误
        return {'error': '不支持的文件格式或文件内容错误'}
    
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

def merge_bills(bills):
    """
    合并多个账单
    
    Args:
        bills: 账单列表，每个账单是一个DataFrame
        
    Returns:
        合并后的DataFrame
    """
    # 转换列表成DataFrame
    dfs = [pd.DataFrame(bill) if isinstance(bill, list) else bill for bill in bills if bill]
    
    if not dfs:
        return pd.DataFrame()
    
    # 合并所有账单
    merged_df = pd.concat(dfs, sort=True)
    
    # 确保交易时间字段是日期时间格式
    if '交易时间' in merged_df.columns:
        merged_df['交易时间'] = pd.to_datetime(merged_df['交易时间'])
    
    # 按时间排序
    merged_df = merged_df.sort_values(by='交易时间', ascending=True)
    
    # 整理列顺序
    column_order = ['交易时间', '类型', '金额(元)', '收/支', '支付方式', '交易对方', '商品名称', '备注']
    merged_df = merged_df.reindex(columns=column_order)
    
    # 过滤掉不计入收支的记录
    merged_df = merged_df[merged_df['收/支'] != '/']
    
    return merged_df
