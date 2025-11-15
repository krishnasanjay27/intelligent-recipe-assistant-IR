import numpy as np
from src.filters import filter_by_diet, filter_by_cuisine, filter_by_time


class HybridSearch:
    def __init__(self, tfidf_index, bm25_index, df):
        self.tfidf = tfidf_index
        self.bm25 = bm25_index
        self.df = df

    def search(
        self,
        query,
        query_tokens,
        top_k=10,
        alpha=0.7,
        diet=None,
        cuisine=None,
        max_time=None
    ):
        """
        Hybrid search with optional filters:
        - diet: list (e.g. ["vegetarian"])
        - cuisine: string (e.g. "indian")
        - max_time: integer (minutes)
        """

        # 1. TF-IDF full ranking
        tfidf_indices, tfidf_scores = self.tfidf.search(query, top_k=len(self.df))

        # 2. BM25 full ranking
        bm25_indices, bm25_scores = self.bm25.search(query_tokens, top_k=len(self.df))

        # Convert to maps
        tfidf_map = dict(zip(tfidf_indices, tfidf_scores))
        bm25_map = dict(zip(bm25_indices, bm25_scores))

        # Normalize TF-IDF
        tfidf_values = np.array(list(tfidf_map.values()))
        tfidf_norm = (tfidf_values - tfidf_values.min()) / (tfidf_values.max() - tfidf_values.min() + 1e-8)

        # Normalize BM25
        bm25_values = np.array(list(bm25_map.values()))
        bm25_norm = (bm25_values - bm25_values.min()) / (bm25_values.max() - bm25_values.min() + 1e-8)

        # Hybrid score
        final_scores = alpha * bm25_norm + (1 - alpha) * tfidf_norm

        # Sort documents by hybrid score
        sorted_indices = np.argsort(final_scores)[::-1]

        # Build ranked dataframe
        ranked_df = self.df.iloc[[tfidf_indices[i] for i in sorted_indices]].copy()
        ranked_df["final_score"] = final_scores[sorted_indices]

        # Apply filters
        if diet:
            ranked_df = filter_by_diet(ranked_df, diet)

        if cuisine:
            ranked_df = filter_by_cuisine(ranked_df, cuisine)

        if max_time:
            ranked_df = filter_by_time(ranked_df, max_time)

        # Return top results
        return ranked_df.head(top_k)
