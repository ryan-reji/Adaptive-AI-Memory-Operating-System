import json

from memory.ai_engine.rag.llm_client import OllamaLLM


VALID_DECISIONS = {"relevant", "irrelevant", "uncertain"}


class RelevanceProcessor:

    def __init__(self):
        self.llm = OllamaLLM()

    def build_prompt(self, evidence):
     return f"""
You are the relevance classifier for a personal AI memory system.

Your job is to decide whether each activity should be retained as
potential long-term memory.

First infer the user's current work/context from the COMPLETE set
of activities provided.

Classification rules:

- relevant:
  Clearly connected to the user's current work, projects, research,
  programming, or tasks.

- irrelevant:
  Clearly unrelated to the user's work/context.
  This includes entertainment and leisure activities such as:
  - Unrelated YouTube videos
  - Gaming websites and gaming activity
  - Netflix and other streaming services
  - Movies and TV shows
  - Music and music-streaming sites
  - Sports and sports websites
  - Memes and casual entertainment
  - Unrelated social media browsing
  when there is no evidence that the activity is connected to the
  user's current work.

- uncertain:
  The activity could reasonably be related to the user's work,
  but there is not enough information to confidently classify it.

IMPORTANT:
- Use the entire evidence set to understand the user's context.
- Do NOT mark something uncertain merely because the individual activity
  lacks information.
- If the activity is clearly connected to the inferred context, mark it
  relevant.
- If the activity is clearly unrelated to the inferred context, mark it
  irrelevant.
- Use uncertain only when the activity could reasonably be relevant but
  there is insufficient information to determine that.
- Do not invent information that is not present in the evidence.
- When uncertain, choose "uncertain" rather than guessing.

Examples:

VS Code editing a file in the user's active project → relevant
Research about a technology being used in the project → relevant
GitHub related to the project → relevant
YouTube programming tutorial related to the project → relevant
YouTube video explaining a technology used in the project → relevant
Random YouTube entertainment → irrelevant
YouTube football/sports video unrelated to the project → irrelevant
Unrelated social media browsing → irrelevant
Unknown activity that could potentially relate to the project → uncertain
Activity with insufficient information to determine relevance → uncertain
Random YouTube entertainment → irrelevant
YouTube football/sports video unrelated to the project → irrelevant
Gaming website or gaming activity → irrelevant
Netflix/movie/TV-show browsing → irrelevant
Music streaming unrelated to the project → irrelevant
Unrelated social media browsing → irrelevant
YouTube programming tutorial related to the project → relevant
Netflix documentary being researched for the project → relevant
Gaming technology research related to the project → relevant

Activity evidence:

 {json.dumps(evidence, indent=2)}

Return ONLY valid JSON:

 {{
    "decisions": [
        {{
            "evidence_id": 123,
            "decision": "relevant"
        }}
    ]
 }}
"""

    def process(self, evidence):
        prompt = self.build_prompt(evidence)
        response = self.llm.generate(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            # Conservative fallback:
            # if the LLM response cannot be understood,
            # keep all evidence.
            return [
                {
                    "evidence_id": item["id"],
                    "decision": "uncertain"
                }
                for item in evidence
            ]

        decisions = result.get("decisions")

        if not isinstance(decisions, list):
            return [
                {
                    "evidence_id": item["id"],
                    "decision": "uncertain"
                }
                for item in evidence
            ]

        valid_ids = {item["id"] for item in evidence}
        validated = []

        for decision in decisions:
            evidence_id = decision.get("evidence_id")
            decision_value = decision.get("decision")

            if (
                evidence_id in valid_ids
                and decision_value in VALID_DECISIONS
            ):
                validated.append({
                    "evidence_id": evidence_id,
                    "decision": decision_value
                })

        # Any evidence missing from the LLM response is uncertain.
        returned_ids = {
            item["evidence_id"]
            for item in validated
        }

        for item in evidence:
            if item["id"] not in returned_ids:
                validated.append({
                    "evidence_id": item["id"],
                    "decision": "uncertain"
                })

        return validated