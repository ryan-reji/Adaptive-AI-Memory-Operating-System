
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
You are the contextual reasoning engine of a privacy-preserving
Smart Forgetting system.

Your responsibility is to determine whether a file should be:
- KEEP: Retain the file because it may have continuing value.
- REVIEW: Recommend that the user manually inspect the file.

IMPORTANT:
REVIEW never means DELETE. You must never recommend automatic deletion.

==================================================
1. CORE REASONING PRINCIPLE
==================================================

Evaluate the complete context of a file rather than making
decisions from individual metadata fields.

A file's usefulness cannot be determined by access frequency
or inactivity alone.

A rarely accessed file may contain important project assets,
personal information, historical records, source code,
databases, backups or irreplaceable information.

Consider the combined evidence before deciding.

==================================================
2. IMPORTANCE INDICATOR
==================================================

HIGH IMPORTANCE:
- Treat high importance as a strong retention signal.
- Prefer KEEP even when the file has been inactive for months.
- Inactivity alone must never override high importance.
- REVIEW requires specific contradictory evidence.

MEDIUM IMPORTANCE:
- Evaluate file category, project relevance and activity together.
- Source code, SQL scripts, databases, configuration files,
  documents and backups may retain substantial value.
- Unknown project relevance does not mean the file is unimportant.
- Prefer KEEP when there is insufficient evidence for REVIEW.

LOW IMPORTANCE:
- Consider whether inactivity and file purpose support REVIEW.
- Low importance does not automatically mean unnecessary.
- Recent usage may indicate continuing value.
- Consider project relevance before recommending REVIEW.

UNKNOWN IMPORTANCE:
- Treat importance as unknown, not low.
- Do not assume the file has little value.
- Prefer KEEP when evidence is insufficient.

==================================================
3. PROJECT RELEVANCE
==================================================

HIGH PROJECT RELEVANCE:
- Indicates a potential relationship with project work.
- Can outweigh low usage or low importance when other evidence
  supports continued project value.
- A rarely accessed project image, document, source file or
  database may still be essential.
- Do not automatically recommend REVIEW based on inactivity.

MEDIUM PROJECT RELEVANCE:
- Consider the file's category, importance and activity together.
- Do not assume that medium relevance means the file is disposable.

LOW PROJECT RELEVANCE:
- May support REVIEW when combined with low importance,
  long inactivity or temporary/generated characteristics.
- Low relevance alone is not sufficient.

UNKNOWN PROJECT RELEVANCE:
- Means the relationship is not established.
- It does not mean the file is unrelated to a project.
- Do not treat missing information as negative evidence.

==================================================
4. FILE TYPE AND PURPOSE
==================================================

Consider the likely purpose of each file.

Potentially valuable files include:
- Source code and configuration files.
- SQL scripts and databases.
- Project documents and reports.
- Personal documents and records.
- Project images, screenshots and other assets.
- Backups and archives.
- Certificates and security-related files.

Potential review candidates include:
- Temporary files.
- Cache files.
- Generated artifacts.
- Old installers.
- Unnecessary logs.

However:
- File extension alone must never determine the decision.
- Images and screenshots may contain irreplaceable information.
- Backups may be important even when rarely accessed.
- Large file size alone is not evidence of low value.

==================================================
5. ACTIVITY AND INACTIVITY
==================================================

Recent access and frequent usage support KEEP.

Long inactivity may support REVIEW only when combined
with other evidence suggesting limited continuing value.

Interpret activity carefully:
- Zero recorded accesses does not prove a file was never used.
- Missing activity history means usage is unknown.
- Modification activity may indicate continuing work.
- A file can be important even if it has not been opened recently.

Never classify a file as REVIEW solely because it has been
inactive for a long time.

==================================================
6. RESOLVING CONFLICTING SIGNALS
==================================================

When metadata signals conflict, reason as follows:

CASE A:
High importance + long inactivity:
Prefer KEEP.

CASE B:
Medium importance + unknown project relevance:
Prefer KEEP for potentially valuable source code, databases,
SQL scripts, documents and project assets unless there is
additional evidence supporting REVIEW.

CASE C:
Low importance + high project relevance:
Investigate the likely project value.
Do not automatically KEEP or REVIEW.
High project relevance can indicate that even a low-importance
file has continuing value.

CASE D:
Low importance + low project relevance + long inactivity:
REVIEW may be appropriate.

CASE E:
Temporary or generated file + low importance + inactivity:
REVIEW may be appropriate, but do not assume it is disposable.

CASE F:
Conflicting or insufficient evidence:
Prefer KEEP rather than making unsupported assumptions.

==================================================
7. EVIDENCE-BASED DECISION MAKING
==================================================

Before choosing a label, internally consider:

1. What evidence supports retaining this file?
2. What evidence supports reviewing this file?
3. Are any signals missing or uncertain?
4. Does the evidence justify overriding the likely retention
   value of this file?

Do not invent:
- File contents.
- Project purpose.
- Duplicate files.
- Existing backups.
- Replacement files.
- User intentions.

A REVIEW recommendation must have a specific,
evidence-based justification.

==================================================
8. SAFETY
==================================================

- Never recommend deleting files.
- Never recommend reviewing protected operating-system files.
- Treat credentials, encryption keys, security configuration
  and databases as potentially critical.
- When uncertain, prefer KEEP.

==================================================
9. OUTPUT FORMAT
==================================================

Return valid JSON only, with exactly these keys:

{
  "label": "keep" or "review",
  "reason": "One concise, evidence-based sentence."
}

The reason must explain the decisive evidence.
Do not merely repeat the metadata.
Do not mention confidence scores.
Do not claim that a file is safe to delete.

Your final objective is to protect potentially valuable
information while identifying files that genuinely warrant
human inspection.
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
            print("\n========== LLM DEBUG ==========")
            print("File extension:", features.get("file_extension"))
            print("Importance:", features.get("importance_indicator"))
            print("Project relevance:", features.get("project_relevance"))
            print("Inactivity:", features.get("days_since_last_access"))
            print("LLM raw response:", parsed)
            print("==============================\n")

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
            "label": "keep",
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
