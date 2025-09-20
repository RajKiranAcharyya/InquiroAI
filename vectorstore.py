import faiss
import numpy as np

class FAISSStore:
    def __init__(self, dimension):
        self.dimension = dimension
        # Using a simple flat L2 index
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []

    def add_texts(self, embeddings, texts):
        """
        Add embeddings and their associated texts to the FAISS index.

        embeddings: PyTorch tensor or numpy array, shape (n, dimension)
        texts: List of strings
        """
        np_embeddings = embeddings.cpu().detach().numpy()
        self.index.add(np_embeddings)
        self.texts.extend(texts)

    def search(self, query_embedding, top_k=5):
        """
        Search for top_k nearest texts to the query embedding.

        query_embedding: PyTorch tensor or numpy array, shape (1, dimension)
        top_k: How many results to return
        """
        np_query = query_embedding.cpu().detach().numpy()
        distances, indices = self.index.search(np_query, top_k)
        results = [self.texts[i] for i in indices[0] if i < len(self.texts)]
        return results








# import faiss
# import numpy as np

# class FAISSStore:
#     def __init__(self, dimension):
#         self.dimension = dimension
#         self.index = faiss.IndexFlatL2(dimension)
#         self.texts = []
        
#     def add_texts(self, embeddings, texts):
#         self.index.add(embeddings.cpu().detach().numpy())
#         self.texts.extend(texts)
        
#     def search(self, query_embedding, top_k=5):
#         D, I = self.index.search(query_embedding.cpu().detach().numpy(), top_k)
#         results = [self.texts[i] for i in I[0] if i < len(self.texts)]
#         return results
