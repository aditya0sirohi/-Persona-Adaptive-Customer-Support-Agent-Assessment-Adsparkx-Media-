
import os
from typing import List, Tuple
import faiss
from sentence_transformers import SentenceTransformer

KB_FOLDER = os.path.join(os.path.dirname(__file__), 'kb')
CHUNK_SIZE = 5  # lines per chunk (simple split)
TOP_K = 3

index = None
documents = []  # List of chunk texts
sources = []    # List of source file names for each chunk
embedding_model = None

def load_kb_files() -> List[Tuple[str, str]]:
    files = [f for f in os.listdir(KB_FOLDER) if f.endswith('.txt')]
    kb_data = []
    for fname in files:
        with open(os.path.join(KB_FOLDER, fname), encoding='utf-8') as f:
            text = f.read()
            kb_data.append((fname, text))
    return kb_data

def create_chunks(kb_data: List[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
    chunk_texts = []
    chunk_sources = []
    for fname, text in kb_data:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for i in range(0, len(lines), CHUNK_SIZE):
            chunk = '\n'.join(lines[i:i+CHUNK_SIZE])
            chunk_texts.append(chunk)
            chunk_sources.append(fname)
    return chunk_texts, chunk_sources

def create_embeddings(chunks: List[str]) -> List[List[float]]:
    return embedding_model.encode(chunks, show_progress_bar=False)

def build_faiss_index(embeddings):
    dim = len(embeddings[0])
    idx = faiss.IndexFlatL2(dim)
    idx.add(embeddings)
    return idx

# Initialize on import
def _init():
    global index, documents, sources, embedding_model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    kb_data = load_kb_files()
    documents, sources = create_chunks(kb_data)
    embeddings = create_embeddings(documents)
    index = build_faiss_index(embeddings)

_init()

def retrieve_context(query: str) -> tuple[list[str], list[str]]:
    query_emb = embedding_model.encode([query])
    D, I = index.search(query_emb, TOP_K)
    chunk_texts = [documents[i] for i in I[0]]
    source_names = [sources[i] for i in I[0]]
    return chunk_texts, source_names
