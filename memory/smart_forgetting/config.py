
from pathlib import Path

# Project root: Adaptive-AI-Memory-Operating-System/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Trained Random Forest bundle stored in the project root
MODEL_PATH = PROJECT_ROOT / "smart_forgetting_rf.joblib"

# Existing activity and memory database
MEMORY_DB_PATH = (
    PROJECT_ROOT / "memory" / "database" / "memory.db"
)

# Independent database for Smart Forgetting recommendations
RECOMMENDATIONS_DB_PATH = (
    Path(__file__).resolve().parent / "recommendations.db"
)

# Prediction settings
CONFIDENCE_THRESHOLD = 0.70
MODEL_LABELS = ("keep", "review")

# Local LLM fallback
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3.5:4b"

# Safety: recommendations only; never delete files automatically
AUTOMATIC_DELETION_ENABLED = False
