import re


def split_sentences(text: str) -> list[str]:
    """Split text into sentences while preserving readable boundaries."""

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap_sentences: int = 2
) -> list[str]:
    """
    Create sentence-aware overlapping chunks.

    Chunks are built from complete sentences instead of
    cutting through words.
    """

    if not text.strip():
        return []

    sentences = split_sentences(text)

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:

        sentence_length = len(sentence)

        if (
            current_sentences
            and current_length + sentence_length > chunk_size
        ):
            chunks.append(" ".join(current_sentences))

            # Keep a small sentence overlap
            current_sentences = current_sentences[
                -overlap_sentences:
            ]

            current_length = sum(
                len(s) for s in current_sentences
            )

        current_sentences.append(sentence)
        current_length += sentence_length + 1

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks