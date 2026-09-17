import chromadb


CHROMA_PATH = "memory/ai_engine/chroma_db"
COLLECTION_NAME = "personal_memory"


class ChromaStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas
    ):
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    def count(self):
        return self.collection.count()

    def search(self, query_embedding, top_k=5):

        return self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )