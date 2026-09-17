from memory.ai_engine.ingestion.pdf_loader import extract_pdf_text
from memory.ai_engine.ingestion.text_cleaner import clean_text


PDF_PATH = "memory/ai_engine/tests/test_data/research_paper.pdf"

pages = extract_pdf_text(PDF_PATH)

for page in pages[:2]:
    cleaned = clean_text(page["text"])

    print("\n" + "=" * 60)
    print(f"PAGE {page['page']}")
    print("=" * 60)
    print(cleaned[:1000])