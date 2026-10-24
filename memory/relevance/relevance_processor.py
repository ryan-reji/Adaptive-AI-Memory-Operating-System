
import json
import os
from pathlib import Path

import joblib

from memory.ai_engine.rag.llm_client import OllamaLLM


VALID_DECISIONS = {"relevant", "irrelevant", "uncertain"}

# LinearSVC decision scores are margins, not probabilities.
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "relevance_svm_pipeline.joblib"
)


class RelevanceProcessor:
    def __init__(
        self,
        model_path=None,
        confidence_threshold=None,
        model=None,
        llm=None,
    ):
        self.model_path = Path(model_path or MODEL_PATH)

        self.confidence_threshold = (
            float(confidence_threshold)
            if confidence_threshold is not None
            else float(
                os.getenv(
                    "RELEVANCE_SVM_THRESHOLD",
                    DEFAULT_CONFIDENCE_THRESHOLD,
                )
            )
        )

        if self.confidence_threshold < 0:
            raise ValueError("Confidence threshold cannot be negative.")

        # Dependency injection supports isolated unit tests.
        self.model = model if model is not None else self._load_model()
        self.llm = llm if llm is not None else OllamaLLM()

    def _load_model(self):
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Relevance model not found: {self.model_path}"
            )

        model = joblib.load(self.model_path)

        if not hasattr(model, "predict") or not hasattr(
            model, "decision_function"
        ):
            raise TypeError(
                "Expected a trained TF-IDF + Linear SVM pipeline "
                "with predict() and decision_function()."
            )

        return model

    @staticmethod
    def evidence_to_text(item):
        """Format activity fields as used during model training."""
        details = item.get("details", "")

        if isinstance(details, (dict, list)):
            details = json.dumps(details, ensure_ascii=False)

        return (
            f"source: {item.get('source_type', '')} "
            f"action: {item.get('action', '')} "
            f"duration: {item.get('duration_seconds', '')} "
            f"details: {details}"
        )

    def build_prompt(self, evidence, candidate_ids=None):
        """Build a strict prompt for low-confidence predictions."""
        candidates = [
            item
            for item in evidence
            if candidate_ids is None or item["id"] in candidate_ids
        ]

        return f"""
You are the final relevance judge for a personal AI memory system.

The local TF-IDF + Linear SVM classifier identified the candidate
activities below as low-confidence cases. Resolve those cases using
the available evidence and the complete activity context.

AVAILABLE FIELDS:
Evidence may contain source_type, timestamp, action,
duration_seconds, and details.

Browser details may contain browser, title, sessions, first_seen,
and last_seen. A URL may not exist. Never require a URL.

CLASSIFICATION RULES:

1. RELEVANT
Choose relevant when an activity clearly connects to the user's
work, projects, programming, study, research, or ongoing tasks.

Examples:
- Editing code in an active project.
- Researching a technology used in a project.
- Visiting a project-related GitHub repository.
- Watching a tutorial that directly supports current project work.

2. IRRELEVANT
Choose irrelevant when an activity is clearly unrelated to the
user's work or projects.

Examples:
- Football highlights unrelated to work.
- Random gaming websites or gameplay.
- Funny videos, memes, movies, and casual entertainment.
- Music streaming and unrelated social media browsing.

IMPORTANT:
Do not label ordinary entertainment uncertain merely because a URL
is missing, duration is short, or a browser title is the only useful
detail. If the title clearly identifies unrelated entertainment and
no work connection is evident, choose irrelevant.

A technical topic is not automatically work-related. Likewise,
YouTube or browser activity is not automatically irrelevant.

3. UNCERTAIN
Choose uncertain only when the evidence genuinely supports multiple
reasonable interpretations and the user's context does not resolve
the ambiguity, or when there is too little meaningful information.

DECISION PROCEDURE:
- Use the complete activity context.
- Classify each candidate independently.
- Use actual evidence; do not invent facts.
- Do not automatically prefer uncertain as a safe default.
- Return exactly one decision for each candidate evidence ID.
- Do not classify non-candidate items.

FULL ACTIVITY CONTEXT:
{json.dumps(evidence, indent=2, ensure_ascii=False, default=str)}

CANDIDATES REQUIRING A FINAL DECISION:
{json.dumps(candidates, indent=2, ensure_ascii=False, default=str)}

Return ONLY valid JSON in this format:
{{
  "decisions": [
    {{"evidence_id": 123, "decision": "irrelevant"}}
  ]
}}

Allowed labels: relevant, irrelevant, uncertain.
No markdown, explanations, or additional keys.
"""

    @staticmethod
    def _uncertain_decisions(items):
        return [
            {
                "evidence_id": item["id"],
                "decision": "uncertain",
            }
            for item in items
        ]

    
    def _llm_fallback(self, evidence, candidates):
        """Resolve low-confidence predictions and retry missing LLM decisions."""
        if not candidates:
            return []

        candidate_ids = {item["id"] for item in candidates}
        validated = {}

        def parse_response(response, allowed_ids):
            """Extract only valid decisions for the requested evidence IDs."""
            try:
                result = json.loads(response)
            except (json.JSONDecodeError, TypeError):
                return {}

            if not isinstance(result, dict):
                return {}

            entries = result.get("decisions")
            if not isinstance(entries, list):
                return {}

            parsed = {}
            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                evidence_id = entry.get("evidence_id")
                decision = entry.get("decision")

                if (
                    evidence_id in allowed_ids
                    and isinstance(decision, str)
                    and decision.strip().lower() in VALID_DECISIONS
                ):
                    parsed[evidence_id] = decision.strip().lower()

            return parsed

        print(
            f"[LLM FALLBACK] Resolving "
            f"{len(candidates)} low-confidence item(s)"
        )

        # First attempt: resolve all candidates in one request.
        try:
            response = self.llm.generate(
                self.build_prompt(evidence, candidate_ids)
            )
            validated.update(parse_response(response, candidate_ids))
        except Exception as exc:
            print(
                f"[LLM FALLBACK ERROR] Batch request failed: "
                f"{type(exc).__name__}: {exc}"
            )

        # Retry every candidate omitted or invalidated by the first response.
        missing = [
            item for item in candidates
            if item["id"] not in validated
        ]

        if missing:
            print(
                f"[LLM RETRY] Retrying {len(missing)} missing "
                f"decision(s) individually"
            )

        for item in missing:
            evidence_id = item["id"]

            try:
                response = self.llm.generate(
                    self.build_prompt(evidence, {evidence_id})
                )
                retry_result = parse_response(response, {evidence_id})

                if evidence_id in retry_result:
                    validated[evidence_id] = retry_result[evidence_id]
                    print(
                        f"[LLM RETRY SUCCESS] id={evidence_id} "
                        f"decision={validated[evidence_id]}"
                    )
                else:
                    print(
                        f"[LLM RETRY WARNING] id={evidence_id}: "
                        "No valid decision returned"
                    )

            except Exception as exc:
                print(
                    f"[LLM RETRY ERROR] id={evidence_id}: "
                    f"{type(exc).__name__}: {exc}"
                )

        # Never lose an evidence item, even if all LLM attempts fail.
        output = []
        for item in candidates:
            evidence_id = item["id"]
            decision = validated.get(evidence_id, "uncertain")

            if evidence_id not in validated:
                print(
                    f"[LLM WARNING] id={evidence_id}: "
                    "using uncertain after retries"
                )

            output.append({
                "evidence_id": evidence_id,
                "decision": decision,
            })

        return output


    def process(self, evidence):
        """
        Return the existing pipeline format:
        [{"evidence_id": ..., "decision": ...}, ...]
        """
        if not evidence:
            return []

        texts = [
            self.evidence_to_text(item)
            for item in evidence
        ]

        predictions = self.model.predict(texts)
        scores = self.model.decision_function(texts)

        # This implementation expects binary LinearSVC output.
        if getattr(scores, "ndim", 1) != 1:
            raise ValueError(
                "Expected binary LinearSVC decision scores."
            )

        if len(predictions) != len(evidence) or len(scores) != len(evidence):
            raise ValueError(
                "The model returned a different number of results "
                "than the supplied evidence count."
            )

        final_decisions = {}
        low_confidence = []

        for item, prediction, score in zip(
            evidence, predictions, scores
        ):
            prediction = str(prediction).strip().lower()
            margin = float(score)

            use_fallback = (
                prediction not in {"relevant", "irrelevant"}
                or abs(margin) < self.confidence_threshold
            )

            print(
                f"[SVM] id={item['id']} "
                f"prediction={prediction} "
                f"margin={margin:.4f} "
                f"fallback={use_fallback}"
            )

            if use_fallback:
                low_confidence.append(item)
            else:
                final_decisions[item["id"]] = prediction

        fallback_decisions = self._llm_fallback(
            evidence,
            low_confidence,
        )

        for entry in fallback_decisions:
            final_decisions[entry["evidence_id"]] = entry["decision"]

        # Preserve the input order and the existing pipeline schema.
        return [
            {
                "evidence_id": item["id"],
                "decision": final_decisions.get(
                    item["id"], "uncertain"
                ),
            }
            for item in evidence
        ]