from memory.ai_engine.ingestion.memory_record import MemoryRecord


def memory_dict_to_record(memory: dict) -> MemoryRecord:
    details = memory.get("details", {})

    return MemoryRecord(
        memory_id=str(memory["memory_id"]),
        source_type=memory["source_type"],
        source_name=_get_source_name(memory),
        content=_build_content(memory),
        timestamp=memory["timestamp"],
        metadata={
            "evidence_id": memory.get("evidence_id"),
            "action": memory.get("action"),
            "duration_seconds": memory.get("duration_seconds"),
            "created_at": memory.get("created_at"),
            "status": memory.get("status"),
            **details
        }
    )


def _get_source_name(memory: dict) -> str:
    details = memory.get("details", {})

    if memory["source_type"] == "vscode":
        return details.get("project", details.get("file", "VS Code"))

    if memory["source_type"] == "browser":
        return details.get("title", "Browser")

    if memory["source_type"] == "file":
        return details.get("file_name", "File")

    return memory["source_type"]


def _build_content(memory: dict) -> str:
    details = memory.get("details", {})
    source_type = memory["source_type"]

    if source_type == "vscode":
        return (
            f"User was {memory.get('action', 'using')} "
            f"the file {details.get('file', '')} "
            f"in the project {details.get('project', '')}."
        )

    if source_type == "browser":
        return (
            f"User viewed the webpage "
            f"'{details.get('title', '')}' "
            f"using {details.get('browser', 'a browser')}."
        )

    if source_type == "file":
        return details.get(
            "content",
            f"User {memory.get('action', 'accessed')} "
            f"the file {details.get('file_name', '')}."
        )

    return str(details)