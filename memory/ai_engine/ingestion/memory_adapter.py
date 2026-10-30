
import json

from memory.ai_engine.ingestion.memory_record import MemoryRecord


def _safe_details(memory: dict) -> dict:
    details = memory.get("details")
    return details if isinstance(details, dict) else {}


def _get_source_name(memory: dict) -> str:
    details = _safe_details(memory)
    source_type = memory.get("source_type", "unknown")

    if source_type == "vscode":
        return str(details.get("project") or details.get("file") or "VS Code")
    if source_type == "browser":
        return str(details.get("title") or "Browser")
    if source_type == "file":
        return str(details.get("file_name") or "File")

    return str(source_type)


def _build_content(memory: dict) -> str:
    details = _safe_details(memory)
    source_type = memory.get("source_type", "unknown")
    action = memory.get("action") or "accessed"

    if source_type == "vscode":
        return (
            f"User was {action} "
            f"the file {details.get('file') or 'unknown file'} "
            f"in the project {details.get('project') or 'unknown project'}."
        )

    if source_type == "browser":
        return (
            f"User viewed the webpage "
            f"'{details.get('title') or 'Unknown webpage'}' "
            f"using {details.get('browser') or 'a browser'}."
        )

    if source_type == "file":
        content = details.get("content")
        if isinstance(content, str) and content.strip():
            return content

        return (
            f"User {action} the file "
            f"{details.get('file_name') or 'Unknown file'} "
            f"at {details.get('source_path') or 'an unknown path'}. "
            f"Text content was not extracted; extraction type: "
            f"{details.get('extraction_type') or 'unknown'}."
        )

    return json.dumps(details, ensure_ascii=False, default=str)


def memory_dict_to_record(memory: dict) -> MemoryRecord:
    details = _safe_details(memory)

    metadata = {
        "evidence_id": memory.get("evidence_id"),
        "action": memory.get("action"),
        "duration_seconds": memory.get("duration_seconds"),
        "created_at": memory.get("created_at"),
        "status": memory.get("status"),
        **details,
    }

    return MemoryRecord(
        memory_id=str(memory["memory_id"]),
        source_type=str(memory.get("source_type") or "unknown"),
        source_name=_get_source_name(memory),
        content=_build_content(memory),
        timestamp=str(memory["timestamp"]),
        metadata=metadata,
    )
