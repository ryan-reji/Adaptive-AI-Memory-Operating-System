class ContextBuilder:
    def build(self, retrieval_results):
        context_parts = []

        for i, result in enumerate(retrieval_results, start=1):
            source_type = result.get("source_type", "unknown")
            source_name = result.get("source_name") or result.get("source", "unknown")
            timestamp = result.get("timestamp")
            page = result.get("page")

            metadata_lines = [
                f"Source Type: {source_type}",
                f"Source: {source_name}",
            ]

            if timestamp:
                metadata_lines.append(f"Timestamp: {timestamp}")

            if page is not None:
                metadata_lines.append(f"Page: {page}")

            context_parts.append(
                f"[Context {i}]\n"
                + "\n".join(metadata_lines)
                + f"\nContent:\n{result['content']}"
            )

        return "\n\n".join(context_parts)