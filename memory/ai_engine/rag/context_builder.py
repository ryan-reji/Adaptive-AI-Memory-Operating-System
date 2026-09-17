class ContextBuilder:

    def build(self, retrieval_results):
        context_parts = []

        for i, result in enumerate(retrieval_results, start=1):
            context_parts.append(
                f"[Context {i}]\n"
                f"Source: {result['source']}\n"
                f"Page: {result['page']}\n"
                f"Content:\n{result['content']}"
            )

        return "\n\n".join(context_parts)