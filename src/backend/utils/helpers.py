def parse_bill_data(bill_data):
    # 解析账单数据的辅助函数
    parsed_data = {}
    # 假设账单数据是以某种格式提供的，进行解析
    # 这里可以添加具体的解析逻辑
    return parsed_data

def format_currency(amount):
    # 格式化货币的辅助函数
    return "${:,.2f}".format(amount)

def validate_file_extension(filename, allowed_extensions):
    # 验证文件扩展名的辅助函数
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_response(success, message, data=None):
    # 生成统一响应格式的辅助函数
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    return response