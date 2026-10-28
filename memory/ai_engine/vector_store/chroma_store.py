import os

import chromadb


CHROMA_HOST = os.getenv("CHROMA_HOST", "127.0.0.1")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "personal_memory")


class ChromaStore:

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def heartbeat(self):
        return self.client.heartbeat()

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
        )

    def count(self):
        return self.collection.count()

    def search(self, query_embedding, top_k=5):
        return self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
        )
