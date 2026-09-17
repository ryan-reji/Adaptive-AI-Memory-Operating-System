from memory.relevance.evidence_loader import get_unprocessed_evidence
from memory.relevance.relevance_processor import RelevanceProcessor
from memory.relevance.decision_db import save_decision


def process_pending_evidence():
    evidence = get_unprocessed_evidence()

    if not evidence:
        print("No unprocessed evidence.")
        return

    processor = RelevanceProcessor()
    decisions = processor.process(evidence)

    for decision in decisions:
        save_decision(
            decision["evidence_id"],
            decision["decision"]
        )

    print(f"Processed {len(decisions)} evidence items.")


if __name__ == "__main__":
    process_pending_evidence()