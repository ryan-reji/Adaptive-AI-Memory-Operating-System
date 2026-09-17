from memory.ai_engine.ingestion.document_processor import process_pdf


PDF_PATH = "memory/ai_engine/tests/test_data/research_paper.pdf"


chunks = process_pdf(PDF_PATH)

print("Total chunks:", len(chunks))

for chunk in chunks[:5]:

    print("\n" + "=" * 60)
    print("CHUNK ID:", chunk["chunk_id"])
    print("PAGE:", chunk["page"])
    print("SOURCE:", chunk["source"])
    print("=" * 60)

    print(chunk["content"][:500])