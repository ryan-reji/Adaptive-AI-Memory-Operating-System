import re
from rank_bm25 import BM25Okapi


class HybridReranker:
    def __init__(self, semantic_weight=0.7, keyword_weight=0.3):
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    @staticmethod
    def tokenize(text):
        return re.findall(r"\b\w+\b", text.lower())

    @staticmethod
    def normalize_scores(scores):
        if not scores:
            return []

        minimum = min(scores)
        maximum = max(scores)

        if maximum == minimum:
            return [1.0 for _ in scores]

        return [
            (score - minimum) / (maximum - minimum)
            for score in scores
        ]

    def rerank(self, query, documents, semantic_distances):
        # Convert Chroma distance into a similarity-like score.
        semantic_scores = [
            1 / (1 + distance)
            for distance in semantic_distances
        ]

        # BM25 keyword scores.
        tokenized_documents = [
            self.tokenize(document)
            for document in documents
        ]

        bm25 = BM25Okapi(tokenized_documents)
        query_tokens = self.tokenize(query)
        keyword_scores = bm25.get_scores(query_tokens).tolist()

        # Normalize both scoring systems.
        normalized_semantic = self.normalize_scores(semantic_scores)
        normalized_keyword = self.normalize_scores(keyword_scores)

        # Combine semantic + keyword relevance.
        combined_scores = [
            (
                self.semantic_weight * semantic
                + self.keyword_weight * keyword
            )
            for semantic, keyword in zip(
                normalized_semantic,
                normalized_keyword
            )
        ]

        ranked = sorted(
            enumerate(combined_scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "index": index,
                "combined_score": score,
                "semantic_score": normalized_semantic[index],
                "keyword_score": normalized_keyword[index]
            }
            for index, score in ranked
        ]