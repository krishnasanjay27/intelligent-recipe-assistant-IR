print(">>> app.py loaded")

import sys
import os
import nltk
import gdown
import pandas as pd

# Make "src/" visible to Python when backend runs inside backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import IR modules
from src.tfidf_index import TFIDFIndex
from src.bm25_index import BM25Index
from src.search import HybridSearch
from src.preprocessing import basic_clean, tokenize, remove_stopwords, lemmatize

# ---------------------------
# Global state
# ---------------------------
df = None
search_engine = None

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Startup
# ---------------------------
@app.on_event("startup")
def startup_event():
    global df, search_engine

    print(">>> startup_event entered")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ---------- NLTK SETUP ----------
    print("Setting up NLTK...")
    NLTK_DIR = "/opt/render/nltk_data"
    os.environ["NLTK_DATA"] = NLTK_DIR
    os.makedirs(NLTK_DIR, exist_ok=True)

    for pkg in ["wordnet", "omw-1.4", "stopwords"]:
        try:
            nltk.data.find(pkg)
        except LookupError:
            nltk.download(pkg, download_dir=NLTK_DIR)

    print("NLTK ready.")

    # ---------- DATASET SETUP ----------
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    DATA_PATH = os.path.join(DATA_DIR, "preprocessed_60000.csv")

    if not os.path.exists(DATA_PATH):
        print("Dataset not found. Downloading...")
        gdown.download(
            "https://drive.google.com/uc?id=1M74qCt0Kq566XsdwCfboARwEmIJCXrEY",
            DATA_PATH,
            quiet=False
        )

    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    required_cols = {"ingredients_tokens", "steps_tokens", "search_text"}
    if not required_cols.issubset(df.columns):
        raise RuntimeError(f"Dataset missing columns: {required_cols - set(df.columns)}")

    df["ingredients_tokens"] = df["ingredients_tokens"].apply(eval)
    df["steps_tokens"] = df["steps_tokens"].apply(eval)

    # ---------- BUILD INDICES ----------
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
    if search_engine is None:
        raise RuntimeError("Search engine not initialized")

    cleaned = basic_clean(data.query)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)

    try:
        query_tokens = lemmatize(tokens)
    except Exception:
        query_tokens = tokens  # fallback

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
        score = float(row["final_score"])
        if score != score:
            score = 0.0

        output.append({
            "name": row["name"],
            "minutes": int(row["minutes"]),
            "tags": row["tags"],
            "score": score,
            "ingredients": row["ingredients"],
            "steps": row["steps"],
            "description": str(row.get("description", ""))
        })

    return {"results": output}
