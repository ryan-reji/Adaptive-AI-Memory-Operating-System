from pathlib import Path


def extract_text_chunk(file_path, start_word=0, max_words=1000):
    path = Path(file_path)

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            text = file.read()

        words = text.split()

        chunk = words[start_word:start_word + max_words]

        return " ".join(chunk)

    except Exception as error:
        print(f"Could not extract text from {path}: {error}")
        return None


if __name__ == "__main__":
    test_file = "memory/tests/test_data/test.py"

    text = extract_text_chunk(test_file)

    print("Text chunk:")
    print(text)