import numpy as np
from typing import List


def get_predicted_category(categories: List[str], similarities: List[float], threshold: float) -> tuple:
    """
    预测交易类别算法:
    1. 如果最高相似度低于阈值，直接返回最高相似度的类别
    2. 如果有多个相似度高于阈值的结果:
    - 只有一种类型时，直接返回该类型和最高相似度
    - 有多种类型时，进行投票，返回出现次数最多的类型，置信度为该类型占比
    """

    if not categories or len(categories) == 0:
        return None, 0.0

    similarities_array = np.array(similarities)

    # 获取最高相似度及其索引
    max_sim_idx = np.argmax(similarities_array)
    max_similarity = similarities_array[max_sim_idx]

    # 如果最高相似度都低于阈值，返回最高的类别和相似度
    if max_similarity < threshold:
        return categories[max_sim_idx], float(max_similarity)

    # 过滤掉相似度低于阈值的结果
    filtered_indices = similarities_array >= threshold
    filtered_categories = [categories[i]
                           for i in range(len(categories)) if filtered_indices[i]]

    # 如果过滤后的类别都相同，返回该类别与最高相似度
    if len(set(filtered_categories)) == 1:
        return filtered_categories[0], float(max_similarity)

    # 统计各类别出现次数，找出出现次数最多的类别
    category_counts = {}
    for category in filtered_categories:
        category_counts[category] = category_counts.get(category, 0) + 1

    most_common_category = max(category_counts, key=category_counts.get)
    most_common_count = category_counts[most_common_category]

    # 计算置信度为该类别占所有过滤后结果的比例
    confidence = most_common_count / len(filtered_categories)

    return most_common_category, float(confidence)
