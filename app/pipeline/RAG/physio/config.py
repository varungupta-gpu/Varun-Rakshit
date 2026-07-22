import os

# Base directory (current folder: rag/physio)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 📂 Data paths
PDF_FOLDER = os.path.join(BASE_DIR, "docs")

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "vector_store.faiss")
CHUNKS_PATH = os.path.join(BASE_DIR, "chunks.pkl")


# 🔎 Retrieval settings
TOP_K = 3


# 🧠 Embedding settings (SentenceTransformer)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


# ⚙️ Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100