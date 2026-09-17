from memory.relevance.relevance_processor import RelevanceProcessor


evidence = [
    {
        "id": 1,
        "source_type": "vscode",
        "action": "editing",
        "details": {
            "project": "Adaptive-AI-Memory-Operating-System",
            "file": "activity_manager.py"
        }
    },
    {
        "id": 2,
        "source_type": "browser",
        "action": "viewed",
        "details": {
            "browser": "Brave",
            "title": "FastAPI Documentation"
        }
    },
    {
        "id": 3,
        "source_type": "browser",
        "action": "viewed",
        "details": {
            "browser": "Brave",
            "title": "Sidemen YouTube"
        }
    }
]


processor = RelevanceProcessor()

response = processor.process(evidence)

print("\nLLM RESPONSE:")
print(response)