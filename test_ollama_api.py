import requests
import traceback

print("Testing Ollama API...", flush=True)

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3.5:4b",
            "prompt": 'Return JSON only: {"label":"keep","reason":"test"}',
            "stream": False,
            "format": "json"
        },
        timeout=90
    )
    print("HTTP:", response.status_code, flush=True)
    print("BODY:", repr(response.text[:2000]), flush=True)

except Exception as exc:
    print(type(exc).__name__, str(exc), flush=True)
    traceback.print_exc()
