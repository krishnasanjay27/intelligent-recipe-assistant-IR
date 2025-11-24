import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

import json
import numpy as np

from src.tfidf_index import TFIDFIndex
from src.bm25_index import BM25Index
from src.search import HybridSearch
from src.preprocessing import preprocess_ingredients, preprocess_steps, build_search_text, basic_clean, tokenize, remove_stopwords, lemmatize

import pandas as pd

# ---------------------------
# LOAD DATA
# ---------------------------
print("Loading dataset...")
df = pd.read_csv("../data/preprocessed_60000.csv")

# ---------------------------
# BUILD INDEXES
# ---------------------------
print("Building TF-IDF index...")
tfidf = TFIDFIndex(df["search_text"].tolist())

print("Building BM25 index...")
bm25 = BM25Index(df["search_text"].tolist())

print("Building Hybrid Search...")
searcher = HybridSearch(tfidf, bm25, df)

# ---------------------------
# EVALUATION METRICS
# ---------------------------
def precision_at_k(pred_ids, true_ids, k=10):
    pred_k = pred_ids[:k]
    return len(set(pred_k) & set(true_ids)) / k

def recall_at_k(pred_ids, true_ids, k=10):
    pred_k = pred_ids[:k]
    return len(set(pred_k) & set(true_ids)) / len(true_ids)

def f1(p, r):
    if p + r == 0:
        return 0
    return 2 * p * r / (p + r)

def ndcg_at_k(pred_ids, true_ids, k=10):
    dcg = 0.0
    for i, pid in enumerate(pred_ids[:k]):
        if pid in true_ids:
            dcg += 1 / np.log2(i + 2)

    ideal_hits = min(len(true_ids), k)
    idcg = sum([1 / np.log2(i + 2) for i in range(ideal_hits)])

    return dcg / idcg if idcg > 0 else 0


# ---------------------------
# LOAD QUERIES
# ---------------------------
with open("eval_queries.json") as f:
    eval_queries = json.load(f)

# ---------------------------
# RUN EVALUATION
# ---------------------------
results = []

for q in eval_queries:
    query = q["query"]
    true_ids = q["relevant_ids"]

    cleaned = basic_clean(query)
    q_tokens = lemmatize(remove_stopwords(tokenize(cleaned)))

    # TF-IDF
    idx, scores = tfidf.search(query, top_k=10)
    tfidf_ids = df.iloc[idx]["id"].tolist()

    # BM25
    idx, scores = bm25.search(q_tokens, top_k=10)
    bm25_ids = df.iloc[idx]["id"].tolist()

    # Hybrid
    ranked_df = searcher.search(query, q_tokens, top_k=10)
    hybrid_ids = ranked_df["id"].tolist()

    # Compute metrics
    for model_name, pred in [
        ("TF-IDF", tfidf_ids),
        ("BM25", bm25_ids),
        ("Hybrid", hybrid_ids)
    ]:
        p = precision_at_k(pred, true_ids)
        r = recall_at_k(pred, true_ids)
        f = f1(p, r)
        nd = ndcg_at_k(pred, true_ids)

        results.append([model_name, query, p, r, f, nd])

# ---------------------------
# OUTPUT RESULTS
# ---------------------------
df_results = pd.DataFrame(results, columns=["Model", "Query", "Precision@10", "Recall@10", "F1", "nDCG@10"])
df_results.to_csv("evaluation_results.csv", index=False)

print(df_results)
print("\nSaved to evaluation_results.csv")
