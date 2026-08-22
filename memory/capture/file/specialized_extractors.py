from pathlib import Path
import pymupdf


def extract_pdf_chunk(file_path, start_page=0, max_pages=5):
    doc = pymupdf.open(file_path)

    end_page = min(start_page + max_pages, len(doc))

    text = ""

    for page_number in range(start_page, end_page):
        text += doc[page_number].get_text()

    metadata = doc.metadata

    doc.close()

    return {
        "content": text,
        "metadata": metadata,
        "start_page": start_page,
        "end_page": end_page
    }


def extract_specialized(file_path, start_chunk=0, chunk_size=5):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_chunk(
            file_path,
            start_page=start_chunk * chunk_size,
            max_pages=chunk_size
        )

    # DOCX/XLSX/PPTX specialized extraction
    # will be added here later.

    return None


if __name__ == "__main__":
    test_file = "memory/tests/test_data/test.pdf"

    result = extract_specialized(test_file)

    print("Pages:", result["start_page"], "to", result["end_page"])
    print("Content:")
    print(result["content"][:1000])