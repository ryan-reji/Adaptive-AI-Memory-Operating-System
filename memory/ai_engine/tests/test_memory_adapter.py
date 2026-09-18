from memory.memory_creation.memory_loader import get_unprocessed_memories
from memory.ai_engine.ingestion.memory_adapter import memory_dict_to_record


memories = get_unprocessed_memories()

print("Unprocessed memories:", len(memories))

for memory in memories[:5]:
    record = memory_dict_to_record(memory)

    print("\n" + "=" * 60)
    print(record)