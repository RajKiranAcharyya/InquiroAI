import torch
from embeddings import Embedder
from vectorstore import FAISSStore
from transformers import pipeline
from transformers import AutoTokenizer

class AcademicQAEngine:
    def __init__(self, documents):
        self.embedder = Embedder()
        self.chunk_size = 300  # words approx per chunk
        self.text_chunks = self.chunk_documents(documents)
        chunk_embeddings = self.embedder.embed_texts(self.text_chunks)
        
        self.vector_store = FAISSStore(dimension=chunk_embeddings.shape[1])
        self.vector_store.add_texts(chunk_embeddings, self.text_chunks)
        
        # Hugging Face pipeline for generative QA
        self.generator = pipeline('text2text-generation', model='google/flan-t5-base')
        
        # Tokenizer and max tokens for input bounding
        self.tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
        self.max_tokens = 512  # model max input tokens limit

    def chunk_documents(self, documents):
        chunks = []
        for doc in documents:
            words = doc.split()
            for i in range(0, len(words), self.chunk_size):
                chunk = " ".join(words[i : i + self.chunk_size])
                chunks.append(chunk)
        return chunks

    def truncate_to_max_tokens(self, text):
        tokens = self.tokenizer.tokenize(text)
        if len(tokens) > self.max_tokens:
            tokens = tokens[: self.max_tokens]
        return self.tokenizer.convert_tokens_to_string(tokens)

    def answer_question(self, question):
        question_embedding = self.embedder.embed_texts([question])
        relevant_texts = self.vector_store.search(question_embedding, top_k=3)  # Limit to top 3 chunks
        context = " ".join(relevant_texts)
        context = self.truncate_to_max_tokens(context)

        prompt = f"Answer the question based on the context:\nContext: {context}\nQuestion: {question}\nAnswer:"
        result = self.generator(prompt, max_length=200)
        return result[0]['generated_text'].strip()










# import torch
# from embeddings import Embedder
# from vectorstore import FAISSStore
# from transformers import pipeline
# from transformers import AutoTokenizer

# class AcademicQAEngine:
#     def __init__(self, documents):
#         self.embedder = Embedder()
#         self.chunk_size = 300  # words approx
#         self.text_chunks = self.chunk_documents(documents)
#         chunk_embeddings = self.embedder.embed_texts(self.text_chunks)
        
#         self.vector_store = FAISSStore(dimension=chunk_embeddings.shape[1])
#         self.vector_store.add_texts(chunk_embeddings, self.text_chunks)
        
#         # Hugging Face pipeline for generative QA
#         self.generator = pipeline('text2text-generation', model='google/flan-t5-base')
        
#         # Initialize tokenizer and max tokens as instance variables
#         self.tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')
#         self.max_tokens = 512  # max input tokens supported by the model

#     def chunk_documents(self, documents):
#         chunks = []
#         for doc in documents:
#             words = doc.split()
#             for i in range(0, len(words), self.chunk_size):
#                 chunk = " ".join(words[i:i+self.chunk_size])
#                 chunks.append(chunk)
#         return chunks

#     def truncate_to_max_tokens(self, text):
#         tokens = self.tokenizer.tokenize(text)
#         # if len(tokens) > self.max_tokens:
#         tokens = tokens[:self.max_tokens]
#         return self.tokenizer.convert_tokens_to_string(tokens)

#     def answer_question(self, question):
#         question_embedding = self.embedder.embed_texts([question])
#         relevant_texts = self.vector_store.search(question_embedding, top_k=3)  # reduce top_k to 3
#         context = " ".join(relevant_texts)
#         context = self.truncate_to_max_tokens(context)

#         prompt = f"Answer the question based on the context:\nContext: {context}\nQuestion: {question}\nAnswer:"
#         result = self.generator(prompt, max_length=200)
#         return result[0]['generated_text'].strip()
