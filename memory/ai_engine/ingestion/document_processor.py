import re

from memory.ai_engine.ingestion.pdf_loader import extract_pdf_text
from memory.ai_engine.ingestion.text_cleaner import clean_text
from memory.ai_engine.ingestion.chunker import chunk_text


def is_references_section(text: str) -> bool:
    return bool(
        re.search(r"(?m)^\s*REFERENCES\s*$", text)
    )


def remove_front_matter(text: str) -> str:
    """
    Remove paper metadata before the ABSTRACT.
    """
    match = re.search(r"\bABSTRACT\b", text, re.IGNORECASE)

    if match:
        return text[match.start():]

    return text


def process_pdf(file_path: str) -> list[dict]:
    pages = extract_pdf_text(file_path)

    processed_chunks = []
    chunk_counter = 1
    references_started = False
    first_content_page = True

    for page in pages:
        cleaned_text = clean_text(page["text"])

        if not cleaned_text:
            continue

        # Remove front matter from the first page.
        if first_content_page:
            cleaned_text = remove_front_matter(cleaned_text)
            first_content_page = False

        # Stop processing once References begins.
        if is_references_section(cleaned_text):
            references_started = True

        if references_started:
            continue

        chunks = chunk_text(cleaned_text)

        for chunk in chunks:
            processed_chunks.append({
                "chunk_id": f"chunk_{chunk_counter}",
                "content": chunk,
                "source": file_path,
                "page": page["page"]
            })

            chunk_counter += 1

    return processed_chunks