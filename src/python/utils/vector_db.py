import os
import json
import uuid
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from chromadb import Documents, EmbeddingFunction, Embeddings, PersistentClient
from sentence_transformers import SentenceTransformer

CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.abspath('')), '..', 'config', 'settings.json')
EMBEDDING_MODEL = "moka-ai/m3e-base"
CHROMADB_PATH = os.path.join(os.path.dirname(
    os.path.abspath('')), '..', 'lib', 'chromadb')
DATASET_COLLECTION_NAME = "bookkeeping-vector-db"


class EnhancedEmbeddingFunction(EmbeddingFunction):
    """
    增强的嵌入函数，将输入文本转换为嵌入向量
    """

    def __init__(self, model):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        # 预处理文本
        processed_input = [self._preprocess_text(text) for text in input]
        # 生成嵌入并归一化
        batch_embeddings = self.model.encode(
            processed_input, normalize_embeddings=True)
        return batch_embeddings.tolist()

    def _preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):
            return str(text)

        # 移除多余空格
        text = ' '.join(text.split())

        # 这里可以添加更多预处理步骤，如:
        # - 移除特殊字符
        # - 标准化商户名称
        # - 分词等

        return text


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

    def initialize_from_dataset(self) -> None:
        dataset_path = self.config.get("dataset", {}).get("path")
        dataset_filename = self.config.get("dataset", {}).get("filename")
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

    def search_similar(self, merchant: str, product: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索相似记录

        Args:
            merchant: 交易对方
            product: 商品名称
            top_k: 返回结果数量

        Returns:
            相似记录列表
        """
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

    def predict_category(self, merchant: str, product: str) -> Dict[str, Any]:
        """
        预测交易类别

        Args:
            merchant: 交易对方
            product: 商品名称

        Returns:
            预测结果，包含类别和置信度
        """
        threshold = self.config.get(
            "output", {}).get("similarity_threshold")
        results = self.search_similar(merchant, product, top_k=1)

        if results and results[0]['similarity'] >= threshold:
            return {
                "category": results[0]['category'],
                "confidence": results[0]['similarity'],
                "source": DATASET_COLLECTION_NAME
            }
        else:
            return {
                "category": None,
                "confidence": 0.0,
                "source": "unknown"
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