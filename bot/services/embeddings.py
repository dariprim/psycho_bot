import logging
from sentence_transformers import SentenceTransformer
from bot.config import EMBEDDING_MODEL_NAME  # добавить в config.py

logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded, dimension: {self.dimension}")

    def get_embedding(self, text: str) -> list:
        if not text:
            return [0.0] * self.dimension
        return self.model.encode(text).tolist()

embedder = EmbeddingModel()