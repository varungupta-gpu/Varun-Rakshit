from pypdf import PdfReader
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import *

# Initialize embedding model (load once)
model = SentenceTransformer('all-MiniLM-L6-v2')


# 1. Load PDFs
def load_pdfs():
    texts = []

    if not os.path.exists(PDF_FOLDER):
        raise FileNotFoundError(f"PDF folder not found: {PDF_FOLDER}")

    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_FOLDER, file)
            reader = PdfReader(path)

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)

    if not texts:
        raise ValueError("No text extracted from PDFs")

    return texts


# 2. Chunking
def chunk_text(texts, chunk_size=500, overlap=100):
    chunks = []

    for text in texts:
        words = text.split()

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

    if not chunks:
        raise ValueError("No chunks created")

    return chunks


# 3. Embedding (FAST + BATCHED)
def embed_chunks(chunks):
    embeddings = model.encode(
        chunks,
        batch_size=32,
        show_progress_bar=True
    )

    embeddings = np.array(embeddings)

    if embeddings.shape[0] == 0:
        raise ValueError("Embeddings generation failed")

    return embeddings


# 4. Build FAISS index
def build_faiss_index(embeddings):
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    return index


# 5. Save index + chunks
def save_artifacts(index, chunks):
    os.makedirs(BASE_DIR, exist_ok=True)

    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"FAISS index saved at: {FAISS_INDEX_PATH}")
    print(f"Chunks saved at: {CHUNKS_PATH}")


# 6. Main pipeline
def main():
    print("Loading PDFs...")
    texts = load_pdfs()

    print("Chunking...")
    chunks = chunk_text(texts)

    print("Creating embeddings (local, free)...")
    embeddings = embed_chunks(chunks)

    print("Building FAISS index...")
    index = build_faiss_index(embeddings)

    print("Saving artifacts...")
    save_artifacts(index, chunks)

    print("DONE: RAG index built successfully (NO API COST 🚀)")


if __name__ == "__main__":
    main()