from functools import lru_cache

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts):
    return get_embedding_model().encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
