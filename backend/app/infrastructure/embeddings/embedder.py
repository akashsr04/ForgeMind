import hashlib
import math
from typing import List
import numpy as np
from app.core.logging import logger
from app.core.config import get_settings

settings = get_settings()

_MODEL_INSTANCE = None
_FALLBACK_ACTIVE = False


def _deterministic_dense_projection(text: str, dim: int = 384) -> List[float]:
    """
    Deterministic dense feature vector for zero-network environments.
    Computes an n-gram hash projection into unit sphere.
    Clearly labeled as deterministic feature extraction, not neural embeddings.
    """
    vec = np.zeros(dim, dtype=np.float32)
    words = text.lower().split()
    if not words:
        return vec.tolist()

    for idx, word in enumerate(words):
        # 1-gram hash
        h1 = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % dim
        vec[h1] += 1.0

        # Bigram hash
        if idx > 0:
            bi = f"{words[idx-1]}_{word}"
            h2 = int(hashlib.sha256(bi.encode("utf-8")).hexdigest(), 16) % dim
            vec[h2] += 1.5

    # L2 normalize
    norm = np.linalg.norm(vec)
    if norm > 1e-6:
        vec /= norm
    return vec.tolist()


class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self.dim = 384
        self.is_neural = False
        self._initialize_model()

    def _initialize_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.dim = self.model.get_sentence_embedding_dimension()
            self.is_neural = True
            logger.info(f"SentenceTransformer successfully loaded with dimension {self.dim}")
        except Exception as e:
            logger.warning(
                f"SentenceTransformer unavailable ({e}). Falling back to deterministic "
                f"unit-sphere n-gram projection (dim={self.dim}). This allows full local execution "
                f"without downloading neural weights or paying API costs."
            )
            self.model = None
            self.is_neural = False

    def embed_text(self, text: str) -> List[float]:
        if self.is_neural and self.model:
            emb = self.model.encode(text, convert_to_numpy=True)
            return emb.tolist()
        return _deterministic_dense_projection(text, dim=self.dim)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self.is_neural and self.model:
            embs = self.model.encode(texts, convert_to_numpy=True)
            return embs.tolist()
        return [_deterministic_dense_projection(t, dim=self.dim) for t in texts]


_embedding_service_instance = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
