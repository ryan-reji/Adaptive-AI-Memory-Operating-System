[33mcommit aa56ce4e4d5b5d805f1a908e52e88ef2e18a8e82[m
Author: Miguel <user11111111s@users.noreply.github.com>
Date:   Fri Oct 2 17:17:12 2026 +0530

    Fix cross-process Chroma RAG staleness

[1mdiff --git a/memory/ai_engine/vector_store/chroma_store.py b/memory/ai_engine/vector_store/chroma_store.py[m
[1mindex 0caa5e5..fba5d94 100644[m
[1m--- a/memory/ai_engine/vector_store/chroma_store.py[m
[1m+++ b/memory/ai_engine/vector_store/chroma_store.py[m
[36m@@ -1,41 +1,47 @@[m
[32m+[m[32mimport os[m
[32m+[m
 import chromadb[m
 [m
 [m
[31m-CHROMA_PATH = "memory/ai_engine/chroma_db"[m
[31m-COLLECTION_NAME = "personal_memory"[m
[32m+[m[32mCHROMA_HOST = os.getenv("CHROMA_HOST", "127.0.0.1")[m
[32m+[m[32mCHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))[m
[32m+[m[32mCOLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "personal_memory")[m
 [m
 [m
 class ChromaStore:[m
 [m
     def __init__(self):[m
[31m-        self.client = chromadb.PersistentClient([m
[31m-            path=CHROMA_PATH[m
[32m+[m[32m        self.client = chromadb.HttpClient([m
[32m+[m[32m            host=CHROMA_HOST,[m
[32m+[m[32m            port=CHROMA_PORT,[m
         )[m
 [m
         self.collection = self.client.get_or_create_collection([m
             name=COLLECTION_NAME[m
         )[m
 [m
[32m+[m[32m    def heartbeat(self):[m
[32m+[m[32m        return self.client.heartbeat()[m
[32m+[m
     def add_documents([m
         self,[m
         ids,[m
         documents,[m
         embeddings,[m
[31m-        metadatas[m
[32m+[m[32m        metadatas,[m
     ):[m
         self.collection.upsert([m
             ids=ids,[m
             documents=documents,[m
             embeddings=embeddings.tolist(),[m
[31m-            metadatas=metadatas[m
[32m+[m[32m            metadatas=metadatas,[m
         )[m
 [m
     def count(self):[m
         return self.collection.count()[m
 [m
     def search(self, query_embedding, top_k=5):[m
[31m-[m
         return self.collection.query([m
             query_embeddings=[query_embedding.tolist()],[m
[31m-            n_results=top_k[m
[31m-        )[m
\ No newline at end of file[m
[32m+[m[32m            n_results=top_k,[m
[32m+[m[32m        )[m

[33mcommit a03a5d7f1fc5386cef0738cb2de682a1dd249be2[m
Author: DivineMarshal <divinemarshal33@gmail.com.com>
Date:   Thu Sep 17 12:36:02 2026 +0530

    Implement AI memory engine and RAG pipeline

[1mdiff --git a/memory/ai_engine/vector_store/chroma_store.py b/memory/ai_engine/vector_store/chroma_store.py[m
[1mnew file mode 100644[m
[1mindex 0000000..0caa5e5[m
[1m--- /dev/null[m
[1m+++ b/memory/ai_engine/vector_store/chroma_store.py[m
[36m@@ -0,0 +1,41 @@[m
[32m+[m[32mimport chromadb[m
[32m+[m
[32m+[m
[32m+[m[32mCHROMA_PATH = "memory/ai_engine/chroma_db"[m
[32m+[m[32mCOLLECTION_NAME = "personal_memory"[m
[32m+[m
[32m+[m
[32m+[m[32mclass ChromaStore:[m
[32m+[m
[32m+[m[32m    def __init__(self):[m
[32m+[m[32m        self.client = chromadb.PersistentClient([m
[32m+[m[32m            path=CHROMA_PATH[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        self.collection = self.client.get_or_create_collection([m
[32m+[m[32m            name=COLLECTION_NAME[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    def add_documents([m
[32m+[m[32m        self,[m
[32m+[m[32m        ids,[m
[32m+[m[32m        documents,[m
[32m+[m[32m        embeddings,[m
[32m+[m[32m        metadatas[m
[32m+[m[32m    ):[m
[32m+[m[32m        self.collection.upsert([m
[32m+[m[32m            ids=ids,[m
[32m+[m[32m            documents=documents,[m
[32m+[m[32m            embeddings=embeddings.tolist(),[m
[32m+[m[32m            metadatas=metadatas[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    def count(self):[m
[32m+[m[32m        return self.collection.count()[m
[32m+[m
[32m+[m[32m    def search(self, query_embedding, top_k=5):[m
[32m+[m
[32m+[m[32m        return self.collection.query([m
[32m+[m[32m            query_embeddings=[query_embedding.tolist()],[m
[32m+[m[32m            n_results=top_k[m
[32m+[m[32m        )[m
\ No newline at end of file[m
