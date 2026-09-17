from memory.ai_engine.embeddings.embedder import Embedder


embedder = Embedder()

texts = [
    "Retrieval Augmented Generation uses retrieved information.",
    "Vector databases store numerical representations.",
    "I went to the gym today."
]

vectors = embedder.encode(texts)

print("\nNumber of texts:", len(texts))
print("Vector shape:", vectors.shape)
print("Embedding dimension:", vectors.shape[1])

print("\nFirst vector:")
print(vectors[0])