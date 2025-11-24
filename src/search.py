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

        # Convert to maps (document_index -> score)
        tfidf_map = dict(zip(tfidf_indices, tfidf_scores))
        bm25_map = dict(zip(bm25_indices, bm25_scores))

        # Use all documents in the dataframe for scoring
        # This ensures we don't miss any documents even if search methods return fewer
        all_doc_indices = list(range(len(self.df)))
        
        # Calculate scores for all documents (0.0 if not in search results)
        tfidf_scores_all = np.array([tfidf_map.get(idx, 0.0) for idx in all_doc_indices])
        bm25_scores_all = np.array([bm25_map.get(idx, 0.0) for idx in all_doc_indices])

        # Normalize TF-IDF
        if tfidf_scores_all.max() > tfidf_scores_all.min():
            tfidf_norm = (tfidf_scores_all - tfidf_scores_all.min()) / (tfidf_scores_all.max() - tfidf_scores_all.min() + 1e-8)
        else:
            tfidf_norm = tfidf_scores_all

        # Normalize BM25
        if bm25_scores_all.max() > bm25_scores_all.min():
            bm25_norm = (bm25_scores_all - bm25_scores_all.min()) / (bm25_scores_all.max() - bm25_scores_all.min() + 1e-8)
        else:
            bm25_norm = bm25_scores_all

        # Hybrid score
        final_scores = alpha * bm25_norm + (1 - alpha) * tfidf_norm

        # Sort documents by hybrid score (get indices into all_doc_indices)
        sorted_score_indices = np.argsort(final_scores)[::-1]
        
        # Get the actual document indices in sorted order
        sorted_doc_indices = [all_doc_indices[i] for i in sorted_score_indices]

        # Build ranked dataframe using the sorted document indices
        ranked_df = self.df.iloc[sorted_doc_indices].copy()
        ranked_df["final_score"] = final_scores[sorted_score_indices]

        # Apply filters
        if diet:
            ranked_df = filter_by_diet(ranked_df, diet)

        # Always call filter_by_cuisine - it handles None and empty strings internally
        ranked_df = filter_by_cuisine(ranked_df, cuisine)

        if max_time:
            ranked_df = filter_by_time(ranked_df, max_time)

        # Return top results
        return ranked_df.head(top_k)
