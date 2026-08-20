import pymupdf
from datetime import datetime
from database.db import get_connection


def extract_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    metadata = doc.metadata

    doc.close()

    return {
        "text": text,
        "metadata": metadata
    }


def save_activity(pdf_path, result):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO activities
        (source_type, source_path, title, content, captured_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "PDF",
        pdf_path,
        result["metadata"].get("title"),
        result["text"],
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    pdf_path = "test.pdf"

    result = extract_pdf(pdf_path)

    save_activity(pdf_path, result)

    print("PDF activity saved to database.")