
import requests

from memory.smart_forgetting.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)
from memory.smart_forgetting.model import SmartForgettingModel


class SmartForgettingRecommender:
    def __init__(self):
        self.model = SmartForgettingModel()

    
      
    def _llm_fallback(self, features: dict) -> dict:
        import json

        system_prompt = """
You are the reasoning component of a privacy-preserving Smart Forgetting
system. Your job is to help users identify files worth REVIEWING, not to
decide that files should be deleted.

CLASSIFICATIONS
- keep: Evidence suggests the file should be retained.
- review: There is a reasonable basis for the user to inspect the file.

IMPORTANT DISTINCTION
"review" never means "delete". A review recommendation is only a suggestion.

REASONING GUIDELINES

1. RECENCY AND USAGE
- Recent access or frequent use supports keeping a file.
- Long inactivity can support review, but inactivity alone is not proof
  that a file is unnecessary.
- Rarely used files can still be important.

2. FILE TYPE AND PURPOSE
- Source code, configuration, databases, project assets, documents,
  certificates, keys, and backups may be important even if rarely used.
- Installers, temporary files, caches, and generated artifacts may merit
  review, but their type alone is not enough to conclude they are disposable.
- Large size alone is not a reason to review a file.

3. PROJECT AND PERSONAL VALUE
- Files related to active projects, unique work, personal records, or
  irreplaceable content should generally be kept when evidence supports this.
- Unknown project relevance means uncertainty, not irrelevance.

4. EVIDENCE QUALITY
- Distinguish observed facts from inferred purpose.
- Missing activity history means usage is unknown, not that the file was
  never used.
- Do not invent file contents, access history, backups, or replacements.
- If evidence is weak or conflicting, prefer keep unless there is a
  specific, explainable reason to review.

5. DUPLICATES
- A duplicate should only support review if a verified equivalent or
  replacement is known to exist.
- Never assume two similarly named files are interchangeable.

6. SAFETY
- Never recommend reviewing protected operating-system or application
  files for cleanup.
- Never suggest deleting any file.
- Treat credentials, encryption keys, security configuration, and databases
  as potentially sensitive or critical.

OUTPUT
Return valid JSON only, with exactly these keys:
{
  "label": "keep" or "review",
  "reason": "One concise, evidence-based sentence for the user"
}

The reason must explain the actual evidence behind the decision.
Do not mention confidence scores or claim that a file is safe to delete.
"""

        user_prompt = (
            "Evaluate this file using only the supplied metadata.\n"
            "If evidence is insufficient, do not invent missing facts.\n\n"
            f"FILE METADATA:\n"
            f"{json.dumps(features, ensure_ascii=False, default=str)}"
        )

        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                "model": OLLAMA_MODEL,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1},
                },
                timeout=90,
            )
            response.raise_for_status()

            api_result = response.json()

            # Qwen may return generated content in either field.
            result = str(api_result.get("response") or "").strip()

            if not result:
                result = str(api_result.get("thinking") or "").strip()

            if not result:
                raise ValueError("Ollama returned no generated content.")

            # Parse the model output as JSON.
            parsed = json.loads(result)

            if not isinstance(parsed, dict):
                raise ValueError("Ollama output was not a JSON object.")

            label = str(parsed.get("label", "review")).strip().lower()

            if label not in {"keep", "review"}:
                label = "review"

            reason = str(parsed.get("reason", "")).strip()

            if not reason:
                reason = (
                "Insufficient evidence to explain the recommendation; "
                "manual review is recommended."
                )

            return {
            "label": label,
            "reason": reason,
            "source": "ollama",
            }

        except Exception as exc:
            print(
            f"[Smart Forgetting] Ollama fallback failed: "
            f"{type(exc).__name__}: {exc}"
            )

            return {
            "label": "review",
            "reason": (
                "The prediction could not be reliably verified by the "
                "reasoning model; manual review is recommended."
            ),
            "source": "fallback_error",
            }

    def recommend(self, features: dict) -> dict:
        prediction = self.model.predict(features)

        if prediction["needs_llm_fallback"]:
            result = self._llm_fallback(features)
            result["confidence"] = prediction["confidence"]
            return result

        label = prediction["label"]

        if label == "review":
            reason = (
                "File characteristics suggest it may be worth reviewing."
            )
        else:
            reason = "Current file characteristics suggest retaining it."

        return {
            "label": label,
            "reason": reason,
            "confidence": prediction["confidence"],
            "source": "random_forest",
        }
