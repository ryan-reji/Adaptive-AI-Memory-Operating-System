from memory.ai_engine.rag.llm_client import OllamaLLM


llm = OllamaLLM()

prompt = """
Explain Retrieval-Augmented Generation (RAG) in exactly 3 sentences.
"""

answer = llm.generate(prompt)

print("\n" + "=" * 70)
print("LLM RESPONSE")
print("=" * 70)
print(answer)