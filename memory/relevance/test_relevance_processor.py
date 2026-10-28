
import numpy as np

from memory.relevance.relevance_processor import RelevanceProcessor


class FakeModel:
    def __init__(self, predictions, scores):
        self.predictions = np.array(predictions)
        self.scores = np.array(scores)

    def predict(self, texts):
        return self.predictions

    def decision_function(self, texts):
        return self.scores


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1
        return self.response


def evidence(evidence_id):
    return {
        "id": evidence_id,
        "source_type": "vscode",
        "action": "edited",
        "duration_seconds": 300,
        "details": "Worked on AI memory project",
    }


def test_high_confidence_relevant_skips_llm():
    llm = FakeLLM('{"decisions": []}')
    processor = RelevanceProcessor(
        model=FakeModel(["relevant"], [1.2]),
        llm=llm,
        confidence_threshold=0.5,
    )

    result = processor.process([evidence(1)])

    assert result == [
        {"evidence_id": 1, "decision": "relevant"}
    ]
    assert llm.calls == 0


def test_high_confidence_irrelevant_skips_llm():
    llm = FakeLLM('{"decisions": []}')
    processor = RelevanceProcessor(
        model=FakeModel(["irrelevant"], [-1.1]),
        llm=llm,
        confidence_threshold=0.5,
    )

    result = processor.process([evidence(2)])

    assert result == [
        {"evidence_id": 2, "decision": "irrelevant"}
    ]
    assert llm.calls == 0


def test_low_confidence_uses_llm_fallback():
    llm = FakeLLM(
        '{"decisions": [{"evidence_id": 3, "decision": "relevant"}]}'
    )
    processor = RelevanceProcessor(
        model=FakeModel(["irrelevant"], [0.1]),
        llm=llm,
        confidence_threshold=0.5,
    )

    result = processor.process([evidence(3)])

    assert result == [
        {"evidence_id": 3, "decision": "relevant"}
    ]
    assert llm.calls == 1


def test_llm_failure_returns_uncertain():
    llm = FakeLLM("not valid JSON")
    processor = RelevanceProcessor(
        model=FakeModel(["relevant"], [0.1]),
        llm=llm,
        confidence_threshold=0.5,
    )

    result = processor.process([evidence(4)])

    assert result == [
        {"evidence_id": 4, "decision": "uncertain"}
    ]
    # One batch attempt plus one individual retry.
    assert llm.calls == 2

