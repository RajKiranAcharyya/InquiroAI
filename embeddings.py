from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Load the pre-trained SentenceTransformer model
        self.model = SentenceTransformer(model_name)
        
    def embed_texts(self, texts):
        """
        Generate dense vector embeddings for a list of texts.
        
        Args:
            texts (list of str): List of text strings to embed.
        
        Returns:
            tensor: Embeddings as a PyTorch tensor.
        """
        return self.model.encode(texts, convert_to_tensor=True)





# from sentence_transformers import SentenceTransformer

# class Embedder:
#     def __init__(self, model_name="all-MiniLM-L6-v2"):
#         self.model = SentenceTransformer(model_name)
        
#     def embed_texts(self, texts):
#         """Generate embeddings for a list of texts"""
#         return self.model.encode(texts, convert_to_tensor=True)
