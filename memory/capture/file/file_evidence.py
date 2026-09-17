from memory.capture.common.activity_evidence import create_activity_evidence


def create_file_evidence(snapshot):
    """
    Convert a file activity snapshot into common activity evidence.
    """

    return create_activity_evidence(
        source_type="file",
        timestamp=snapshot["timestamp"],
        action=snapshot["action"],
        duration_seconds=None,
        details={
            "source_path": snapshot["source_path"],
            "file_name": snapshot["file_name"],
            "file_type": snapshot["file_type"],
            "file_size": snapshot["file_size"],
            "content": snapshot["content"],
            "extraction_type": snapshot["extraction_type"],
            "chunk_number": snapshot["chunk_number"]
        }
    )


if __name__ == "__main__":

    test_snapshot = {
        "source_type": "file",
        "action": "modified",
        "source_path": "memory/tests/test_data/test.py",
        "timestamp": "2026-09-16T22:00:00",
        "file_name": "test.py",
        "file_type": ".py",
        "file_size": 100,
        "content": 'print("hello")',
        "extraction_type": "text",
        "chunk_number": 0
    }

    evidence = create_file_evidence(test_snapshot)

    print("File Activity Evidence:")
    print(evidence)