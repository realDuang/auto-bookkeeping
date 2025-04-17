import json
from typing import Dict, Any


def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        raise Exception(f"无法加载配置文件，请检查文件路径和格式是否正确: {e}")
