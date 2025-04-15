from chromadb import Documents, EmbeddingFunction, Embeddings


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
