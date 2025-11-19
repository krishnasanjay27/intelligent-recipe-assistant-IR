import sys
import os

# Make "src/" visible to Python when backend runs inside backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

# Import IR modules
from src.tfidf_index import TFIDFIndex
from src.bm25_index import BM25Index
from src.search import HybridSearch
from src.preprocessing import basic_clean, tokenize, remove_stopwords, lemmatize

app = FastAPI()

# Enable CORS so React frontend can call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Load preprocessed dataset
# ---------------------------
print("Loading dataset...")
df = pd.read_csv("../data/preprocessed_10000.csv")

# Convert token columns from string to Python list
df["ingredients_tokens"] = df["ingredients_tokens"].apply(eval)
df["steps_tokens"] = df["steps_tokens"].apply(eval)

print("Building TF-IDF index...")
tfidf_index = TFIDFIndex(df["search_text"].tolist())

print("Building BM25 index...")
bm25_index = BM25Index(df["ingredients_tokens"].tolist())

print("Building Hybrid Search...")
search_engine = HybridSearch(tfidf_index, bm25_index, df)

print("Backend ready!")


# ---------------------------
# Request Model
# ---------------------------
class SearchQuery(BaseModel):
    query: str
    diet: list[str] | None = None
    cuisine: str | None = None
    max_time: int | None = None
    top_k: int = 10


# ---------------------------
# Search Endpoint
# ---------------------------
@app.post("/search")
def search_recipes(data: SearchQuery):

    cleaned = basic_clean(data.query)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    query_tokens = lemmatize(tokens)

    results = search_engine.search(
        query=data.query,
        query_tokens=query_tokens,
        top_k=data.top_k,
        diet=data.diet,
        cuisine=data.cuisine,
        max_time=data.max_time
    )

    output = []
    for _, row in results.iterrows():
        output.append({
            "name": row["name"],
            "minutes": int(row["minutes"]),
            "tags": row["tags"],
            "score": float(row["final_score"]),
            "ingredients": row["ingredients"],
            "steps": row["steps"],
            "description": row.get("description", "")
        })

    return {"results": output}
