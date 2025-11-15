import numpy as np

class HybridSearch:
    def __init__(self, tfidf_index, bm25_index, df):
        self.tfidf = tfidf_index
        self.bm25 = bm25_index
        self.df = df

    def search(self, query, query_tokens, top_k=10, alpha=0.7):
        """
        alpha controls strength of BM25 (0.7 recommended)
        """

        # TF-IDF scores
        tfidf_indices, tfidf_scores = self.tfidf.search(query, top_k=len(self.df))

        # BM25 scores
        bm25_indices, bm25_scores = self.bm25.search(query_tokens, top_k=len(self.df))

        # Map indices -> scores
        tfidf_map = dict(zip(tfidf_indices, tfidf_scores))
        bm25_map = dict(zip(bm25_indices, bm25_scores))

        # Normalize both score sets
        tfidf_values = np.array(list(tfidf_map.values()))
        bm25_values = np.array(list(bm25_map.values()))

        tfidf_norm = (tfidf_values - tfidf_values.min()) / (tfidf_values.max() - tfidf_values.min() + 1e-8)
        bm25_norm  = (bm25_values - bm25_values.min()) / (bm25_values.max() - bm25_values.min() + 1e-8)

        # Compute combined score
        final_scores = alpha * bm25_norm + (1 - alpha) * tfidf_norm

        # Sort by final score
        sorted_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for i in sorted_indices:
            doc_index = tfidf_indices[i]
            results.append((doc_index, final_scores[i]))

        return results
