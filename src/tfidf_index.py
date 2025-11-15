import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TFIDFIndex:
    def __init__(self, documents):
        """
        documents: list of preprocessed 'search_text' strings
        """
        self.vectorizer = TfidfVectorizer()
        self.doc_matrix = self.vectorizer.fit_transform(documents)

    def search(self, query_text, top_k=10):
        """
        Search for top_k similar recipes based on TF-IDF cosine similarity.
        """
        query_vec = self.vectorizer.transform([query_text])
        scores = cosine_similarity(query_vec, self.doc_matrix).flatten()

        # Sort scores (highest first)
        top_indices = scores.argsort()[::-1][:top_k]
        return top_indices, scores[top_indices]
