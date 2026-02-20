print(">>> app.py loaded")

import sys
import os
import platform
import threading
import traceback
import gc

import nltk
import gdown
import pandas as pd

# Make "src/" visible to Python when backend runs inside backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
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
init_error = None          # stores error message if startup failed
init_done = False          # True once background init finishes


# ---------------------------
# Helper: resolve NLTK data directory (platform-aware)
# ---------------------------
def _get_nltk_data_dir() -> str:
    env = os.environ.get("NLTK_DATA")
    if env:
        return env
    if platform.system() == "Linux":
        return "/opt/render/nltk_data"
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "nltk_data")


# ---------------------------
# Background initialisation (runs in a thread)
# ---------------------------
def _initialize():
    global df, search_engine, init_error, init_done

    print(">>> background init started", flush=True)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    try:
        # ---------- NLTK SETUP ----------
        print("Setting up NLTK...", flush=True)
        NLTK_DIR = _get_nltk_data_dir()
        os.environ["NLTK_DATA"] = NLTK_DIR
        os.makedirs(NLTK_DIR, exist_ok=True)

        if NLTK_DIR not in nltk.data.path:
            nltk.data.path.insert(0, NLTK_DIR)

        for pkg in ["wordnet", "omw-1.4", "stopwords"]:
            try:
                nltk.data.find(f"corpora/{pkg}")
                print(f"  NLTK '{pkg}' already present.", flush=True)
            except LookupError:
                print(f"  Downloading NLTK '{pkg}'...", flush=True)
                nltk.download(pkg, download_dir=NLTK_DIR)

        print("NLTK ready.", flush=True)

        # ---------- DATASET SETUP ----------
        DATA_DIR = os.path.join(BASE_DIR, "..", "data")
        os.makedirs(DATA_DIR, exist_ok=True)
        DATA_PATH = os.path.join(DATA_DIR, "preprocessed_60000.csv")

        if not os.path.exists(DATA_PATH):
            print("Dataset not found. Downloading via gdown...", flush=True)
            gdown.download(
                "https://drive.google.com/uc?id=1M74qCt0Kq566XsdwCfboARwEmIJCXrEY",
                DATA_PATH,
                quiet=False,
            )
            if not os.path.exists(DATA_PATH):
                raise RuntimeError("gdown finished but dataset file is missing!")
            print("Dataset downloaded.", flush=True)
        else:
            print("Dataset already present, skipping download.", flush=True)

        # ---------- LOAD DATASET (memory-efficient) ----------
        print("Loading dataset...", flush=True)
        df = pd.read_csv(DATA_PATH)

        required_cols = {"ingredients_tokens", "steps_tokens", "search_text"}
        if not required_cols.issubset(df.columns):
            raise RuntimeError(
                f"Dataset missing columns: {required_cols - set(df.columns)}"
            )

        # Parse token columns — these are stored as string repr of lists
        print("Parsing token columns...", flush=True)
        df["ingredients_tokens"] = df["ingredients_tokens"].apply(eval)
        df["steps_tokens"] = df["steps_tokens"].apply(eval)

        # ---------- BUILD TF-IDF INDEX ----------
        print("Building TF-IDF index...", flush=True)
        search_texts = df["search_text"].tolist()
        tfidf_index = TFIDFIndex(search_texts)
        del search_texts
        gc.collect()

        # ---------- BUILD BM25 INDEX ----------
        print("Building BM25 index...", flush=True)
        ingredient_tokens = df["ingredients_tokens"].tolist()
        bm25_index = BM25Index(ingredient_tokens)
        del ingredient_tokens
        gc.collect()

        # Free raw documents stored inside BM25 (they are duplicates)
        bm25_index.free_raw_documents()
        gc.collect()

        # ---------- BUILD HYBRID SEARCH ----------
        print("Building Hybrid Search...", flush=True)
        search_engine = HybridSearch(tfidf_index, bm25_index, df)

        # Drop heavy token columns from df — they're already inside the indices
        df = df.drop(columns=["ingredients_tokens", "steps_tokens", "search_text"])
        gc.collect()

        print("✅ Backend ready!", flush=True)

    except Exception as exc:
        traceback.print_exc()
        init_error = str(exc)
        print(
            "⚠️  Startup failed — the /search endpoint will return 503 "
            "until the issue is resolved.",
            flush=True,
        )
    finally:
        init_done = True


# ---------------------------
# Lifespan: kick off background init, then yield immediately
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=_initialize, daemon=True)
    thread.start()
    print(">>> server is accepting connections (init running in background)", flush=True)
    yield
    print(">>> shutdown", flush=True)


# ---------------------------
# App
# ---------------------------
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# Health check
# ---------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "search_ready": search_engine is not None,
        "init_done": init_done,
        "init_error": init_error,
    }


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
        if not init_done:
            raise HTTPException(
                status_code=503,
                detail="Server is still starting up. Please wait a moment and try again.",
            )
        raise HTTPException(
            status_code=503,
            detail=f"Search engine failed to initialize: {init_error or 'unknown error'}",
        )

    cleaned = basic_clean(data.query)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)

    try:
        query_tokens = lemmatize(tokens)
    except Exception:
        query_tokens = tokens

    results = search_engine.search(
        query=data.query,
        query_tokens=query_tokens,
        top_k=data.top_k,
        diet=data.diet,
        cuisine=data.cuisine,
        max_time=data.max_time,
    )

    output = []
    for _, row in results.iterrows():
        score = float(row["final_score"])
        if score != score:
            score = 0.0

        output.append(
            {
                "name": row["name"],
                "minutes": int(row["minutes"]),
                "tags": row["tags"],
                "score": score,
                "ingredients": row["ingredients"],
                "steps": row["steps"],
                "description": str(row.get("description", "")),
            }
        )

    return {"results": output}
