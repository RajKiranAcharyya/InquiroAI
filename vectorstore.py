import uuid

import chromadb
import numpy as np


class ChromaStore:
    def __init__(self):
        self.client = chromadb.EphemeralClient()
        collection_name = f"inquiro_{uuid.uuid4().hex}"
        self.collection = self.client.create_collection(
            collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, embeddings, chunks):
        self.collection.add(
            ids=[str(index) for index in range(len(chunks))],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=np.asarray(embeddings).tolist(),
            metadatas=[
                {"file": chunk["file"], "source": chunk["source"]}
                for chunk in chunks
            ],
        )

    def search(self, query_embedding, top_k):
        result_count = min(top_k, self.collection.count())
        if result_count == 0:
            return []

        query = np.asarray(query_embedding).reshape(1, -1).tolist()
        results = self.collection.query(
            query_embeddings=query,
            n_results=result_count,
        )
        return [
            {
                "text": text,
                "file": metadata["file"],
                "source": metadata["source"],
                "distance": distance,
            }
            for text, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
