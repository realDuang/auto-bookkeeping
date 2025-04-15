import pandas as pd
from models.vector_db import BookkeepingVectorDB

def process_with_ai(bill_data):
    """
    使用AI处理账单数据，进行分类和预测
    
    Args:
        bill_data: 账单数据，可以是DataFrame或字典列表
        
    Returns:
        处理后的账单数据，包含分类结果
    """
    # 如果输入是空的，返回空结果
    if not bill_data:
        return {'error': '没有提供账单数据'}
    
    # 如果输入是错误信息，直接返回
    if isinstance(bill_data, dict) and 'error' in bill_data:
        return bill_data
    
    # 将输入转换为DataFrame
    df = pd.DataFrame(bill_data) if isinstance(bill_data, list) else bill_data
    
    # 初始化向量数据库
    vector_db = BookkeepingVectorDB()
    
    # 对每一条未分类的交易记录进行分类
    processed_data = []
    for _, row in df.iterrows():
        record_dict = row.to_dict()
        
        # 如果记录已经有分类信息且不为空，保留原分类
        if '类型' in record_dict and record_dict['类型'] and not pd.isna(record_dict['类型']):
            processed_data.append(record_dict)
            continue
            
        # 提取商户和商品信息
        merchant = str(row['交易对方']) if '交易对方' in row and not pd.isna(row['交易对方']) else ""
        product = str(row['商品名称']) if '商品名称' in row and not pd.isna(row['商品名称']) else ""
        
        # 使用向量数据库预测类别
        prediction = vector_db.predict_category(merchant, product)
        
        # 更新记录的分类信息
        record_dict['类型'] = prediction['category'] if prediction['category'] else "未分类"
        record_dict['分类置信度'] = prediction['confidence']
        
        processed_data.append(record_dict)
    
    # 计算统计信息
    stats = calculate_stats(processed_data)
    
    return {
        'processed_data': processed_data,
        'stats': stats
    }

def calculate_stats(data):
    """
    计算账单数据的统计信息
    
    Args:
        data: 处理后的账单数据
        
    Returns:
        统计信息字典
    """
    df = pd.DataFrame(data)
    
    # 确保金额列是数值型
    if '金额(元)' in df.columns:
        df['金额(元)'] = pd.to_numeric(df['金额(元)'], errors='coerce')
    
    # 计算总支出和总收入
    total_expense = df[df['收/支'] == '支出']['金额(元)'].sum()
    total_income = df[df['收/支'] == '收入']['金额(元)'].sum()
    
    # 按类别统计
    category_stats = {}
    if '类型' in df.columns:
        for category in df['类型'].unique():
            if pd.isna(category):
                continue
                
            cat_df = df[df['类型'] == category]
            cat_expense = cat_df[cat_df['收/支'] == '支出']['金额(元)'].sum()
            cat_income = cat_df[cat_df['收/支'] == '收入']['金额(元)'].sum()
            cat_count = len(cat_df)
            
            category_stats[category] = {
                'expense': float(cat_expense),
                'income': float(cat_income),
                'count': int(cat_count)
            }
    
    # 按月份统计
    monthly_stats = {}
    if '交易时间' in df.columns:
        df['月份'] = pd.to_datetime(df['交易时间']).dt.strftime('%Y-%m')
        for month in df['月份'].unique():
            month_df = df[df['月份'] == month]
            month_expense = month_df[month_df['收/支'] == '支出']['金额(元)'].sum()
            month_income = month_df[month_df['收/支'] == '收入']['金额(元)'].sum()
            
            monthly_stats[month] = {
                'expense': float(month_expense),
                'income': float(month_income)
            }
    
    return {
        'total_expense': float(total_expense),
        'total_income': float(total_income),
        'category_stats': category_stats,
        'monthly_stats': monthly_stats,
        'record_count': len(df)
    }

def train_model(dataset_path=None):
    """
    使用数据集训练向量数据库模型
    
    Args:
        dataset_path: 数据集文件路径，如果为None则使用配置中的默认路径
        
    Returns:
        训练结果信息
    """
    try:
        # 初始化向量数据库
        vector_db = BookkeepingVectorDB()
        
        # 从数据集初始化
        vector_db.initialize_from_dataset(dataset_path)
        
        # 获取数据库统计信息
        stats = vector_db.get_collection_stats()
        
        return {
            'success': True,
            'message': '模型训练成功',
            'stats': {
                'total_records': stats['total_records'],
                'category_counts': stats['category_counts']
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'模型训练失败: {str(e)}'
        }
