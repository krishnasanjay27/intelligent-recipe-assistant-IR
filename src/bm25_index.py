import math
from collections import Counter

class BM25Index:
    def __init__(self, documents, k1=1.5, b=0.75):
        """
        documents: list of token lists (NOT strings)
        Example: [["tomato", "rice", "onion"], ...]
        """
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.N = len(documents)

        # Document lengths
        self.doc_lengths = [len(doc) for doc in documents]
        self.avg_doc_len = sum(self.doc_lengths) / self.N

        # Term frequencies per document
        self.term_freqs = [Counter(doc) for doc in documents]

        # Document frequency for each term
        self.df = Counter()
        for doc in documents:
            for term in set(doc):
                self.df[term] += 1

        # IDF values
        self.idf = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))


    def free_raw_documents(self):
        """Drop the raw token lists to reclaim memory.
        Call this AFTER construction if you no longer need them."""
        self.documents = None

    def search(self, query_tokens, top_k=10):
        """
        query_tokens: list of tokens
        """
        scores = []

        for i in range(self.N):
            score = 0
            doc_len = self.doc_lengths[i]
            tf = self.term_freqs[i]

            for term in query_tokens:
                if term not in tf:
                    continue

                term_tf = tf[term]
                term_idf = self.idf.get(term, 0)

                numerator = term_tf * (self.k1 + 1)
                denominator = term_tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))

                score += term_idf * (numerator / denominator)

            scores.append(score)

        # Get top_k results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        top_scores = [scores[i] for i in top_indices]

        return top_indices, top_scores
