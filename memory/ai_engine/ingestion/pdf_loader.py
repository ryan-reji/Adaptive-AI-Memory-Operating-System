from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(file_path: str) -> list[dict]:
    """
    Extract text from each page of a PDF.

    Returns:
        [
            {
                "page": 1,
                "text": "..."
            }
        ]
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Expected a PDF file.")

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    return pages