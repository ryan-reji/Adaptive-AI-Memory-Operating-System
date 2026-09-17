from pathlib import Path

from memory.ai_engine.ingestion.pdf_loader import extract_pdf_text


PDF_PATH = Path(
    "memory/ai_engine/tests/test_data/research_paper.pdf"
)


pages = extract_pdf_text(str(PDF_PATH))

print(f"Pages with text extracted: {len(pages)}")

for page in pages[:2]:
    print("\n" + "=" * 60)
    print(f"PAGE {page['page']}")
    print("=" * 60)
    print(page["text"][:1000])