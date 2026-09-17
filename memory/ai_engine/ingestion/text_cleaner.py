import re


def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove common PDF header/footer artifacts.
    text = re.sub(
        r"M\.\s*Hindi et al\.: Enhancing the Precision and Interpretability of RAG in Legal Technology: A Survey",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bVOLUME\s+\d+,\s+\d{4}\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove DOI lines.
    text = re.sub(
        r"Digital Object Identifier\s+\S+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines.
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces around line breaks.
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()