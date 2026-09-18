from memory.ai_engine.ingestion.memory_ingestor import MemoryIngestor


ingestor = MemoryIngestor()

result = ingestor.ingest_unprocessed_memories()

print("\n" + "=" * 60)
print("MEMORY INGESTION")
print("=" * 60)

print("Processed memory IDs:")
print(result["processed_memory_ids"])

print("\nChunks added:")
print(result["chunks_added"])

print("\nChromaDB document count:")
print(ingestor.store.count())