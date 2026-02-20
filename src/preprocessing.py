import re
import ast
import pandas as pd

import nltk
import os
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# -------------------------------------------------
# NLTK setup (make sure these are downloaded once)
# -------------------------------------------------
# nltk.download("stopwords")
# nltk.download("wordnet")
# nltk.download("omw-1.4")
# Tell NLTK where data is (Render-safe)
NLTK_DATA_PATH = os.environ.get("NLTK_DATA", "/opt/render/nltk_data")
nltk.data.path.append(NLTK_DATA_PATH)

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    stop_words = set()

lemmatizer = WordNetLemmatizer()
# -------------------------------------------------
# BASIC CLEANING
# -------------------------------------------------

def basic_clean(text):
    """
    Lowercase + remove punctuation + remove digits + collapse spaces.
    Keeps only alphabetic characters and spaces.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------
# TOKENIZATION
# -------------------------------------------------

def tokenize(text):
    """
    Split cleaned text into tokens.
    """
    return text.split()


# -------------------------------------------------
# STOPWORD REMOVAL
# -------------------------------------------------

def remove_stopwords(tokens):
    """
    Remove common English stopwords.
    """
    return [t for t in tokens if t not in stop_words]


# -------------------------------------------------
# LEMMATIZATION (NLTK)
# -------------------------------------------------

def lemmatize(tokens):
    """
    Lemmatize tokens using NLTK WordNet lemmatizer.
    """
    try:
        return [lemmatizer.lemmatize(t) for t in tokens]
    except LookupError:
        return tokens


# -------------------------------------------------
# PREPROCESS INGREDIENTS
# -------------------------------------------------

def preprocess_ingredients(ingredients_str):
    """
    Convert ingredient list string to cleaned tokens.
    """
    try:
        ingredients = ast.literal_eval(ingredients_str)
    except Exception:
        return []

    combined_text = " ".join(ingredients)

    cleaned = basic_clean(combined_text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)

    return tokens


# -------------------------------------------------
# PREPROCESS STEPS
# -------------------------------------------------

def preprocess_steps(steps_str):
    """
    Convert steps list string to cleaned tokens.
    """
    try:
        steps = ast.literal_eval(steps_str)
    except Exception:
        return []

    combined_text = " ".join(steps)

    cleaned = basic_clean(combined_text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)

    return tokens


# -------------------------------------------------
# BUILD SEARCH TEXT
# -------------------------------------------------

def build_search_text(title, ingredients_tokens, steps_tokens):
    """
    Combine title, ingredients, and steps into one weighted search text.
    """
    cleaned_title = basic_clean(title)
    title_tokens = tokenize(cleaned_title)
    title_tokens = remove_stopwords(title_tokens)
    title_tokens = lemmatize(title_tokens)

    # Weights
    weighted_title = title_tokens * 2
    weighted_ing = ingredients_tokens * 5
    weighted_steps = steps_tokens

    all_tokens = weighted_title + weighted_ing + weighted_steps
    return " ".join(all_tokens)


# -------------------------------------------------
# PREPROCESS ENTIRE DATAFRAME
# -------------------------------------------------

def preprocess_dataframe(df):
    """
    Apply preprocessing pipeline to recipes dataframe.
    Produces:
    - ingredients_tokens
    - steps_tokens
    - search_text
    Keeps original fields for UI display.
    """

    processed_rows = []

    for _, row in df.iterrows():

        ing_tokens = preprocess_ingredients(row["ingredients"])
        step_tokens = preprocess_steps(row["steps"])

        search_text = build_search_text(
            row["name"],
            ing_tokens,
            step_tokens
        )

        processed_rows.append({
            "id": row["id"],
            "name": row["name"],
            "minutes": row["minutes"],
            "tags": row["tags"],

            # Original fields (UI)
            "description": row.get("description", ""),
            "ingredients": row["ingredients"],
            "steps": row["steps"],

            # Processed fields (IR)
            "ingredients_tokens": ing_tokens,
            "steps_tokens": step_tokens,
            "search_text": search_text
        })

    return pd.DataFrame(processed_rows)
