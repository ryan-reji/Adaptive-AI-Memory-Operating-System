from datetime import datetime


def create_snapshot(activity, extraction_result):
    metadata = extraction_result.get("metadata", {})

    return {
        "source_type": activity["source_type"],
        "action": activity["action"],
        "source_path": activity["path"],
        "timestamp": activity["timestamp"],

        "file_name": metadata.get("file_name"),
        "file_type": metadata.get("extension"),
        "file_size": metadata.get("file_size"),

        "content": extraction_result.get("content"),
        "extraction_type": extraction_result.get("extraction_type"),
        "chunk_number": extraction_result.get("chunk_number", 0),

        "created_at": datetime.now().isoformat()
    }


if __name__ == "__main__":

    activity = {
        "source_type": "file",
        "action": "modified",
        "path": "memory/tests/test_data/test.py",
        "timestamp": datetime.now().isoformat()
    }

    extraction_result = {
        "content": 'print("hello world")',
        "metadata": {
            "file_name": "test.py",
            "extension": ".py",
            "file_size": 20
        },
        "extraction_type": "text",
        "chunk_number": 0
    }

    snapshot = create_snapshot(
        activity,
        extraction_result
    )

    print("Activity Snapshot:")
    print(snapshot)