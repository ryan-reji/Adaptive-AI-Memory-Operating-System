from memory.ai_engine.ingestion.pdf_loader import extract_pdf_text
from memory.ai_engine.ingestion.text_cleaner import clean_text
from memory.ai_engine.ingestion.chunker import chunk_text


PDF_PATH = "memory/ai_engine/tests/test_data/research_paper.pdf"

pages = extract_pdf_text(PDF_PATH)

full_text = "\n\n".join(
    clean_text(page["text"])
    for page in pages
)

chunks = chunk_text(full_text)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks[:3], start=1):
    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print("=" * 60)
    print(chunk[:500])