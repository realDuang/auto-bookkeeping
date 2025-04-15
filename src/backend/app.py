from flask import Flask, request, jsonify, send_file
from services.file_parser import parse_file, merge_bills
from services.ai_processor import process_with_ai, train_model
from models.vector_db import BookkeepingVectorDB
import os
import pandas as pd
import tempfile

app = Flask(__name__)

# 允许较大的上传文件
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    上传账单文件并进行处理
    文件将被解析为统一格式，并使用AI进行分类
    """
    if 'file' not in request.files:
        return jsonify({'error': '请求中未包含文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 解析上传的文件
    bill_data = parse_file(file)
    
    # 使用AI处理账单数据
    processed_data = process_with_ai(bill_data)
    
    return jsonify(processed_data), 200

@app.route('/merge', methods=['POST'])
def merge_files():
    """
    合并多个账单文件
    支持同时上传多个支付宝和微信支付的账单文件
    """
    if 'files' not in request.files:
        return jsonify({'error': '请求中未包含文件'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 解析所有上传的文件
    bill_data_list = []
    for file in files:
        bill_data = parse_file(file)
        if isinstance(bill_data, list):
            bill_data_list.append(bill_data)
    
    # 合并所有账单
    merged_df = merge_bills(bill_data_list)
    
    if merged_df.empty:
        return jsonify({'error': '无法解析任何账单文件或所有文件格式不正确'}), 400
    
    # 使用AI处理合并后的账单数据
    processed_data = process_with_ai(merged_df)
    
    return jsonify(processed_data), 200

@app.route('/train', methods=['POST'])
def train():
    """
    训练向量数据库模型
    可以上传一个已标记类别的数据集进行训练
    """
    dataset_path = None
    
    # 检查是否上传了数据集文件
    if 'dataset' in request.files and request.files['dataset'].filename != '':
        file = request.files['dataset']
        fd, dataset_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        file.save(dataset_path)
    
    # 训练模型
    result = train_model(dataset_path)
    
    # 清理临时文件
    if dataset_path and os.path.exists(dataset_path):
        os.remove(dataset_path)
    
    return jsonify(result), 200 if result['success'] else 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """
    获取向量数据库中的所有类别
    """
    vector_db = BookkeepingVectorDB()
    categories = vector_db.get_all_categories()
    return jsonify({'categories': categories}), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    获取向量数据库统计信息
    """
    vector_db = BookkeepingVectorDB()
    stats = vector_db.get_collection_stats()
    return jsonify(stats), 200

@app.route('/predict', methods=['POST'])
def predict_category():
    """
    预测交易类别
    根据商户名称和商品名称预测类别
    """
    data = request.json
    if not data or 'merchant' not in data or 'product' not in data:
        return jsonify({'error': '请求数据不完整，需要提供merchant和product字段'}), 400
    
    vector_db = BookkeepingVectorDB()
    prediction = vector_db.predict_category(data['merchant'], data['product'])
    
    return jsonify(prediction), 200

@app.route('/export', methods=['POST'])
def export_data():
    """
    导出处理后的账单数据为CSV文件
    """
    data = request.json
    if not data or 'processed_data' not in data:
        return jsonify({'error': '请求数据不完整，需要提供processed_data字段'}), 400
    
    try:
        df = pd.DataFrame(data['processed_data'])
        
        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        
        # 保存为CSV
        df.to_csv(temp_path, encoding='utf-8-sig', index=False)
        
        # 发送文件
        return send_file(
            temp_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='processed_bill.csv',
            # 文件发送后删除
            attachment_filename='processed_bill.csv'
        )
    except Exception as e:
        return jsonify({'error': f'导出数据失败: {str(e)}'}), 500

@app.route('/status', methods=['GET'])
def status():
    """
    获取服务状态
    """
    return jsonify({
        'status': 'running',
        'version': '1.0.0'
    }), 200

# 添加跨域支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10087)