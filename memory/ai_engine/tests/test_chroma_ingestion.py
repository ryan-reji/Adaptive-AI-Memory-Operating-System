from memory.ai_engine.ingestion.document_processor import process_pdf
from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore


PDF_PATH = "memory/ai_engine/tests/test_data/research_paper.pdf"


# 1. Process PDF
chunks = process_pdf(PDF_PATH)

print("Chunks created:", len(chunks))


# 2. Generate embeddings
embedder = Embedder()

texts = [
    chunk["content"]
    for chunk in chunks
]

embeddings = embedder.encode(texts)

print("Embeddings generated:", len(embeddings))


# 3. Store in ChromaDB
store = ChromaStore()

ids = [
    chunk["chunk_id"]
    for chunk in chunks
]

metadatas = [
    {
        "source": chunk["source"],
        "page": chunk["page"]
    }
    for chunk in chunks
]

store.add_documents(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas
)

print("Documents stored:", store.count())