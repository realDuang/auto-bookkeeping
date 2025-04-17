import os
import uuid
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from models.embedding import EnhancedEmbeddingFunction
from models.algorithm import get_predicted_category
from utils.utils import load_config
from utils.extract_features import extract_time_features, extract_amount_features, extract_transaction_fields

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.abspath('')), '..', 'config', 'settings.json')
EMBEDDING_MODEL = "moka-ai/m3e-base"
CHROMADB_PATH = os.path.join(os.path.dirname(
    os.path.abspath('')), '..', 'models', 'lib', 'chromadb')
DATASET_COLLECTION_NAME = "bookkeeping-vector-db"


class BookkeepingVectorDB:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BookkeepingVectorDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if BookkeepingVectorDB._initialized:
            return

        # 加载配置
        self.config = load_config(CONFIG_PATH)

        # 将配置值设置到字典中
        self.CONFIG_PATH = CONFIG_PATH
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.CHROMADB_PATH = CHROMADB_PATH

        self.dataset_config = self.config.get("dataset", {})
        self.similarity_threshold = self.config.get(
            "model", {}).get("similarity_threshold")
        self.excluded_categories = self.config.get(
            "model", {}).get("excluded_categories", [])

        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.db_client = PersistentClient(path=CHROMADB_PATH)
        self.embed_fn = EnhancedEmbeddingFunction(self.embedding_model)

        # 获取或创建集合
        self.collection = self.db_client.get_or_create_collection(
            name=DATASET_COLLECTION_NAME,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"}
        )

        BookkeepingVectorDB._initialized = True

    def initialize_from_dataset(self) -> None:
        self.clear_database()
        self.add_data_from_csv()

    def add_data_from_csv(self) -> None:
        dataset_path = self.dataset_config.get("path")
        dataset_filename = self.dataset_config.get("filename")
        dataset_file_path = os.path.join(os.path.dirname(
            os.path.abspath('')), '..', dataset_path, dataset_filename)

        try:
            # 读取数据集
            try:
                df = pd.read_csv(dataset_file_path, on_bad_lines='warn')
            except TypeError:
                # 如果失败，使用旧版本参数
                df = pd.read_csv(dataset_file_path,
                                 error_bad_lines=False, warn_bad_lines=True)
            print(f"成功加载数据集，共 {len(df)} 条记录。注意：某些行可能因格式问题被跳过。")

            if self.excluded_categories.__len__() > 0:
                print(
                    f"注意：数据集中有 {self.excluded_categories.__len__()} 个分类将被排除：{self.excluded_categories}")

            # 批量添加记录
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i+batch_size]
                self._add_batch(batch_df)
                print(f"已处理 {min(i+batch_size, len(df))}/{len(df)} 条记录")

        except Exception as e:
            print(f"数据库处理数据失败: {e}")

    def _add_batch(self, df: pd.DataFrame) -> None:
        documents = []
        metadatas = []
        ids = []

        for _, row in df.iterrows():
            fields = extract_transaction_fields(row)

            # 跳过没有类型的记录
            if not fields['category']:
                continue

            # 跳过在排除列表中的类别
            if fields['category'] in self.excluded_categories:
                continue

            time_period = extract_time_features(fields['pay_time'])

            [normalized_amount, amount_size] = extract_amount_features(
                fields['amount'])

            # 创建元数据
            metadata = {
                "type": fields['category'],
                "merchant": fields['merchant'],
                "product": fields['product'],
                "pay_type": fields['pay_type'],
                "pay_time": fields['pay_time'],
                "amount": normalized_amount,
                "i_o": fields['i_o'],
                "remark": fields['remark'],
                "time_period": time_period,
                "amount_size": amount_size
            }
            metadatas.append(metadata)

            document = f"{fields['merchant']}:{fields['product']}"
            documents.append(document)

            ids.append(str(uuid.uuid4()))

        # 批量添加到集合
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def search_similar(self, row: pd.Series, top_k: int) -> List[Dict[str, Any]]:
        """
        搜索相似记录
        """

        fields = extract_transaction_fields(row)
        merchant = fields['merchant']
        product = fields['product']

        query = f"{merchant}:{product}"

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )

        # 格式化结果
        formatted_results = []
        if results['distances'] and results['distances'][0]:
            for i in range(len(results['distances'][0])):
                formatted_results.append({
                    "category": results['metadatas'][0][i]['type'],
                    "document": results['documents'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # 转换距离为相似度
                })

        return formatted_results

    def predict_category(self, row: pd.Series, threshold: float = None, top_k: int = 10) -> Dict[str, Any]:
        """
        预测结果，包含类别和置信度
        """
        if threshold is None:
            threshold = self.similarity_threshold

        results = self.search_similar(row, top_k)

        if not results:
            return {
                "category": None,
                "confidence": 0.0,
                "source": DATASET_COLLECTION_NAME
            }

        categories = [result['category'] for result in results]
        similarities = np.array([result['similarity'] for result in results])

        # 预测类别
        best_category, best_confidence = get_predicted_category(
            categories, similarities, threshold)

        if best_confidence >= threshold:
            return {
                "category": best_category,
                "confidence": best_confidence,
                "source": DATASET_COLLECTION_NAME
            }
        else:
            return {
                "category": None,
                "confidence": best_confidence,
                "source": DATASET_COLLECTION_NAME
            }

    def get_all_categories(self) -> List[str]:
        """
        获取所有类别

        Returns:
            类别列表
        """
        results = self.collection.get(include=["metadatas"])

        categories = set()
        for metadata in results['metadatas']:
            if metadata and 'type' in metadata:
                categories.add(metadata['type'])

        return list(categories)

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息

        Returns:
            统计信息字典
        """
        # 获取所有记录
        results = self.collection.get(include=["metadatas"])

        # 计算每个类别的记录数
        category_counts = {}
        for metadata in results['metadatas']:
            if metadata and 'type' in metadata:
                category = metadata['type']
                category_counts[category] = category_counts.get(
                    category, 0) + 1

        return {
            "total_records": len(results['ids']),
            "category_counts": category_counts
        }

    def _extract_text_features(self, merchant: str, product: str) -> np.ndarray:
        """
        提取商户和商品名称的文本特征
        """
        # 商户和商品的独立嵌入
        merchant_embedding = self.embedding_model.encode(
            merchant, normalize_embeddings=True)
        product_embedding = self.embedding_model.encode(
            product, normalize_embeddings=True)

        # 合并文本特征
        combined_text = f"{merchant}:{product}"
        combined_embedding = self.embedding_model.encode(
            combined_text, normalize_embeddings=True)

        # 可以选择性地降维或选择最重要的维度
        return np.concatenate([
            merchant_embedding,
            product_embedding,
            combined_embedding
        ])

    def clear_database(self) -> None:
        try:
            # 删除现有集合
            self.db_client.delete_collection(DATASET_COLLECTION_NAME)

            # 重新创建空集合
            self.collection = self.db_client.get_or_create_collection(
                name=DATASET_COLLECTION_NAME,
                embedding_function=self.embed_fn,
                metadata={"hnsw:space": "cosine"}
            )

            print("数据库已成功清空")
        except Exception as e:
            print(f"清空数据库失败: {e}")
            raise Exception(f"清空数据库过程中发生错误: {e}")
