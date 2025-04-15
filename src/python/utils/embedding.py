import re
from chromadb import Documents, EmbeddingFunction, Embeddings


class EnhancedEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        processed_input = [self._preprocess_text(text) for text in input]

        batch_embeddings = self.model.encode(
            processed_input, normalize_embeddings=True)
        return batch_embeddings.tolist()

    def _preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):
            return str(text)

        # 移除多余空格
        text = ' '.join(text.split())
        # 移除长度大于9的无意义连续数字
        text = re.sub(r'\d{9,}', '', text)

        # 这里可以添加更多预处理步骤，如:
        # - 移除特殊字符
        # - 标准化商户名称

        return text
