from datetime import datetime

#This is a part of file activity for now so do not delete!!


def create_activity_event(source_type, action, path, metadata=None):
    return {
        "source_type": source_type,
        "action": action,
        "path": path,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }


if __name__ == "__main__":
    event = create_activity_event(
        source_type="file",
        action="modified",
        path="test.pdf"
    )

    print(event)