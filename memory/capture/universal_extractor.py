from pathlib import Path

from memory.capture.text_extractor import extract_text_chunk
from memory.capture.specialized_extractors import extract_specialized
from memory.capture.metadata_extractor import extract_metadata


TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".csv", ".tsv",
    ".html", ".htm", ".css", ".scss", ".sass",
    ".js", ".jsx", ".ts", ".tsx",
    ".py", ".pyw",
    ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp",
    ".java", ".kt", ".kts", ".scala",
    ".cs",
    ".go", ".rs", ".rb", ".php", ".swift",
    ".dart", ".r", ".sql",
    ".json", ".xml", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".env"
}


SPECIALIZED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".rtf",
    ".xls", ".xlsx", ".xlsm", ".ods",
    ".ppt", ".pptx", ".odp"
}


def get_extraction_type(file_path):
    extension = Path(file_path).suffix.lower()

    if extension in TEXT_EXTENSIONS:
        return "text"

    if extension in SPECIALIZED_EXTENSIONS:
        return "specialized"

    return "metadata"


def get_chunk(file_path, chunk_number=0, chunk_size=1000):
    extraction_type = get_extraction_type(file_path)

    # Text-readable files
    if extraction_type == "text":
        content = extract_text_chunk(
            file_path,
            start_word=chunk_number * chunk_size,
            max_words=chunk_size
        )

        return {
            "content": content,
            "metadata": extract_metadata(file_path),
            "extraction_type": "text",
            "chunk_number": chunk_number
        }

    # Specialized formats
    if extraction_type == "specialized":
        result = extract_specialized(
            file_path,
            start_chunk=chunk_number,
            chunk_size=5
        )

        if result is not None:
            metadata = extract_metadata(file_path)
            metadata.update(result.get("metadata", {}))

            return {
                "content": result.get("content"),
                "metadata": metadata,
                "extraction_type": "specialized",
                "chunk_number": chunk_number,
                "start_page": result.get("start_page"),
                "end_page": result.get("end_page")
            }

    # Unsupported format
    return {
        "content": None,
        "metadata": extract_metadata(file_path),
        "extraction_type": "metadata",
        "chunk_number": chunk_number
    }


if __name__ == "__main__":

    test_files = [
        "memory/tests/test_data/test.py",
        "memory/tests/test_data/test.pdf",
        "memory/tests/test_data/test.xyz"
    ]

    for file in test_files:

        print(f"\n--- {file} ---")

        result = get_chunk(file)

        print("Extraction type:", result["extraction_type"])
        print("Chunk:", result["chunk_number"])
        print("Metadata:", result["metadata"])

        if result["content"]:
            print("Content preview:")
            print(result["content"][:500])