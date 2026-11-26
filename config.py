import os

from dotenv import load_dotenv

load_dotenv()


EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K = 4
TEMPERATURE = 0.2
REFUSAL_SENTENCE = "I could not find this in the documents."
GROQ_MODEL_ID = os.getenv("GROQ_MODEL_ID", "openai/gpt-oss-120b")
