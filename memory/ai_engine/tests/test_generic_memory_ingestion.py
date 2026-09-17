from memory.ai_engine.ingestion.memory_record import MemoryRecord
from memory.ai_engine.ingestion.memory_processor import process_memory
from memory.ai_engine.embeddings.embedder import Embedder
from memory.ai_engine.vector_store.chroma_store import ChromaStore


record = MemoryRecord(
    memory_id="mem_vscode_001",
    source_type="vscode",
    source_name="Adaptive-AI-Memory-Operating-System",
    content=(
        "The user worked on the RAG pipeline. "
        "They created a local LLM client using Ollama. "
        "They tested Qwen3.5 for local response generation."
    ),
    timestamp="2026-09-17T11:30:00",
    metadata={
        "language": "python"
    }
)

# 1. Convert memory into chunks
chunks = process_memory(record)

print("Chunks created:", len(chunks))

# 2. Generate embeddings
embedder = Embedder()

texts = [chunk["content"] for chunk in chunks]
embeddings = embedder.encode(texts)

print("Embeddings generated:", len(embeddings))

# 3. Store in ChromaDB
store = ChromaStore()

ids = [chunk["chunk_id"] for chunk in chunks]

metadatas = [
    {
        "memory_id": chunk["memory_id"],
        "source_type": chunk["source_type"],
        "source_name": chunk["source_name"],
        "timestamp": chunk["timestamp"],
        **chunk["metadata"]
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