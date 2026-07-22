import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from app.pipeline.RAG.physio.config import *


# =========================================================
# GLOBALS (lazy-loaded)
# =========================================================

model = None
index = None
chunks = None


# =========================================================
# MODEL LOADER
# =========================================================

def get_model():

    global model
    if model is None:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return model

# =========================================================
# VECTOR STORE LOADER
# =========================================================

def load_vector_store():

    global index
    global chunks

    # Already loaded
    if index is not None and chunks is not None:
        return index, chunks

    # -----------------------------------------------------
    # Ensure files exist
    # -----------------------------------------------------

    if not os.path.exists(FAISS_INDEX_PATH):

        print(f"FAISS index missing. Creating dummy at {FAISS_INDEX_PATH}")

        dummy_index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)

        embeddings = np.random.random((10, EMBEDDING_DIMENSION)).astype("float32")

        dummy_index.add(embeddings)

        faiss.write_index(dummy_index,FAISS_INDEX_PATH)

        if not os.path.exists(CHUNKS_PATH):

            dummy_chunks = [f"Placeholder medical advise {i}"for i in range(10)]

            with open(CHUNKS_PATH, "wb") as f:
                pickle.dump(dummy_chunks, f)

    # -----------------------------------------------------
    # Load FAISS
    # -----------------------------------------------------

    print("Loading FAISS index...")

    index = faiss.read_index(FAISS_INDEX_PATH)

    # -----------------------------------------------------
    # Load chunks
    # -----------------------------------------------------

    print("Loading chunks...")

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


# =========================================================
# RETRIEVAL
# =========================================================

def retrieve(query, k=TOP_K):

    model = get_model()
    index, chunks = load_vector_store()

    # -----------------------------------------------------
    # Query embedding
    # -----------------------------------------------------

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding)

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    _, indices = index.search(query_embedding,k)
    # -----------------------------------------------------
    # Fetch chunks
    # -----------------------------------------------------
    results = [chunks[i]for i in indices[0]]

    return results