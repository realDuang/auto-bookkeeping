import os
import json
import uuid
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from models.EnhancedEmbedding import EnhancedEmbeddingFunction

# 相对路径调整，适应Flask结构
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, '..', '..', 'config', 'settings.json')
EMBEDDING_MODEL = "moka-ai/m3e-base"
CHROMADB_PATH = os.path.join(BASE_DIR, '..', '..', 'lib', 'chromadb')
DATASET_COLLECTION_NAME = "bookkeeping-vector-db"


class BookkeepingVectorDB:
    _instance = None
    _initialized = False

    def __new__(cls, config_path: str = CONFIG_PATH):
        if cls._instance is None:
            cls._instance = super(BookkeepingVectorDB, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = CONFIG_PATH):
        if BookkeepingVectorDB._initialized:
            return

        # 加载配置
        self.config = self._load_config(config_path)
        # 将配置值设置到字典中
        self.config["CONFIG_PATH"] = CONFIG_PATH
        self.config["EMBEDDING_MODEL"] = EMBEDDING_MODEL
        self.config["CHROMADB_PATH"] = CHROMADB_PATH
        self.config["similarity_threshold"] = self.config.get(
            "output", {}).get("similarity_threshold")

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

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            raise Exception(f"无法加载配置文件，请检查文件路径和格式是否正确: {e}")

    def initialize_from_dataset(self, dataset_file_path: str = None) -> None:
        """
        从数据集初始化向量数据库

        Args:
            dataset_file_path: 数据集文件路径，如果为None则使用配置文件中的路径
        """
        if dataset_file_path is None:
            dataset_path = self.config.get("dataset", {}).get("path")
            dataset_filename = self.config.get("dataset", {}).get("filename")
            dataset_file_path = os.path.join(
                BASE_DIR, '..', '..', dataset_path, dataset_filename)

        try:
            # 读取数据集
            try:
                df = pd.read_csv(dataset_file_path, on_bad_lines='warn')
            except TypeError:
                # 如果失败，使用旧版本参数
                df = pd.read_csv(dataset_file_path,
                                 error_bad_lines=False, warn_bad_lines=True)
            print(f"成功加载数据集，共 {len(df)} 条记录。注意：某些行可能因格式问题被跳过。")

            # 批量添加记录
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i+batch_size]
                self._add_batch(batch_df)
                print(f"已处理 {min(i+batch_size, len(df))}/{len(df)} 条记录")

            print("向量数据库初始化完成")
        except Exception as e:
            print(f"初始化数据库失败: {e}")

    def _add_batch(self, df: pd.DataFrame) -> None:
        """
        批量添加记录到向量数据库

        Args:
            df: 包含记录的DataFrame
        """
        documents = []
        metadatas = []
        ids = []

        for _, row in df.iterrows():
            # 确保必要的列存在
            if '交易对方' in df.columns and '商品名称' in df.columns and '类型' in df.columns:
                merchant = str(row['交易对方']) if not pd.isna(row['交易对方']) else ""
                product = str(row['商品名称']) if not pd.isna(row['商品名称']) else ""
                category = str(row['类型']) if not pd.isna(row['类型']) else ""

                # 跳过没有类型的记录
                if not category:
                    continue

                # 创建文档文本（商户:商品格式）
                document = f"{merchant}:{product}"
                documents.append(document)

                # 创建元数据
                metadata = {
                    "type": category,
                    "merchant": merchant,
                    "product": product
                }
                metadatas.append(metadata)

                # 生成唯一ID
                ids.append(str(uuid.uuid4()))

        # 批量添加到集合
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

    def add_record(self, merchant: str, product: str, category: str) -> None:
        """
        添加单条记录到向量数据库

        Args:
            merchant: 商户名称
            product: 商品名称
            category: 类别
        """
        document = f"{merchant}:{product}"
        metadata = {
            "type": category,
            "merchant": merchant,
            "product": product
        }

        self.collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )

        print(f"成功添加记录: {merchant}:{product} -> {category}")

    def search_similar(self, merchant: str, product: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似记录

        Args:
            merchant: 商户名称
            product: 商品名称
            top_k: 返回结果数量

        Returns:
            相似记录列表
        """
        # 创建查询文本
        query_text = f"{merchant}:{product}"

        # 执行查询
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )

        # 格式化结果
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "document": results['documents'][0][i],
                    "category": results['metadatas'][0][i]['type'],
                    "similarity": 1 - results['distances'][0][i]  # 转换距离为相似度
                })

        return formatted_results

    def predict_category(self, merchant: str, product: str) -> Dict[str, Any]:
        """
        预测交易类别

        Args:
            merchant: 商户名称
            product: 商品名称

        Returns:
            预测结果字典，包含类别、置信度和来源
        """
        # 获取相似记录
        similar_records = self.search_similar(merchant, product, top_k=3)

        # 如果没有找到相似记录，返回空结果
        if not similar_records:
            return {
                "category": None,
                "confidence": 0.0,
                "source": "vector_db"
            }

        # 使用相似度最高的记录作为预测结果
        best_match = similar_records[0]

        # 如果相似度低于阈值，返回空结果
        threshold = float(self.config.get("similarity_threshold", 0.7))
        if best_match['similarity'] < threshold:
            return {
                "category": None,
                "confidence": best_match['similarity'],
                "source": "vector_db"
            }

        # 返回预测结果
        return {
            "category": best_match['category'],
            "confidence": best_match['similarity'],
            "source": "vector_db"
        }

    def get_all_categories(self) -> List[str]:
        """
        获取所有类别

        Returns:
            类别列表
        """
        # 获取所有记录
        results = self.collection.get(include=["metadatas"])

        # 提取所有类别并去重
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
        """提取商户和商品名称的文本特征"""
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
