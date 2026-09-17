from memory.ai_engine.retrieval.retriever import Retriever
from memory.ai_engine.rag.context_builder import ContextBuilder
from memory.ai_engine.rag.llm_client import OllamaLLM


class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.context_builder = ContextBuilder()
        self.llm = OllamaLLM()

    def answer(self, query: str, top_k: int = 3) -> dict:
        # Step 1: Retrieve relevant information
        retrieval = self.retriever.search(
            query=query,
            top_k=top_k
        )

        # Step 2: Build context
        context = self.context_builder.build(
            retrieval["results"]
        )

        # Step 3: Create grounded prompt
        prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I don't have enough information in the retrieved context."

Do not invent facts.

Context:
{context}

User Question:
{query}

Answer:
"""

        # Step 4: Generate answer using local LLM
        answer = self.llm.generate(prompt)

        return {
            "query": query,
            "answer": answer,
            "context": context,
            "retrieval_time_ms": retrieval["retrieval_time_ms"]
        }