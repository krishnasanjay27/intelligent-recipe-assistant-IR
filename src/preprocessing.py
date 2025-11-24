import re
import spacy
import nltk
from nltk.corpus import stopwords
import ast
import pandas as pd

# ---------------------------------------
# Load stopwords + spaCy model
# ---------------------------------------

stop_words = set(stopwords.words("english"))

# Make sure you ran:
# python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")


# ---------------------------------------
# BASIC CLEANING
# ---------------------------------------

def basic_clean(text):
    """
    Lowercase + remove punctuation + remove digits + collapse spaces.
    Keeps only alphabetic characters and spaces.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # keep only letters + spaces
    text = re.sub(r"\s+", " ", text)       # collapse multiple spaces
    return text.strip()


# ---------------------------------------
# TOKENIZATION
# ---------------------------------------

def tokenize(text):
    """
    Split cleaned text into tokens.
    """
    return text.split()


# ---------------------------------------
# STOPWORD REMOVAL
# ---------------------------------------

def remove_stopwords(tokens):
    """
    Remove common English stopwords such as:
    the, and, or, with, in, for, etc.
    """
    return [t for t in tokens if t not in stop_words]


# ---------------------------------------
# LEMMATIZATION
# ---------------------------------------

def lemmatize(tokens):
    """
    Lemmatize tokens using spaCy's language model.
    Converts words to their base form:
      tomatoes → tomato
      onions → onion
      cooked → cook
    """
    doc = nlp(" ".join(tokens))
    return [token.lemma_ for token in doc]


# ---------------------------------------
# PREPROCESS INGREDIENTS  (optimized)
# ---------------------------------------

def preprocess_ingredients(ingredients_str):
    """
    Convert ingredient list string to cleaned tokens (FAST version).
    Calls spaCy only once per recipe.
    """
    try:
        ingredients = ast.literal_eval(ingredients_str)
    except:
        return []

    combined_text = " ".join(ingredients)

    cleaned = basic_clean(combined_text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)  # spaCy called ONLY ONCE

    return tokens


# ---------------------------------------
# PREPROCESS STEPS (optimized)
# ---------------------------------------

def preprocess_steps(steps_str):
    """
    Convert steps list string to cleaned tokens (FAST version).
    Calls spaCy only once per recipe.
    """
    try:
        steps = ast.literal_eval(steps_str)
    except:
        return []

    combined_text = " ".join(steps)

    cleaned = basic_clean(combined_text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)  # spaCy called ONLY ONCE

    return tokens


# ---------------------------------------
# BUILD SEARCH TEXT
# ---------------------------------------

def build_search_text(title, ingredients_tokens, steps_tokens):
    """
    Combine title, ingredients, and steps into one weighted search text.
    title weight = x2
    ingredients weight = x3
    steps weight = x1
    """
    # Preprocess title
    cleaned_title = basic_clean(title)
    title_tokens = tokenize(cleaned_title)
    title_tokens = remove_stopwords(title_tokens)
    title_tokens = lemmatize(title_tokens)

    # Apply weights
    weighted_title = title_tokens * 2
    weighted_ing = ingredients_tokens * 5
    weighted_steps = steps_tokens * 0.5

    # Combine all tokens
    all_tokens = weighted_title + weighted_ing + weighted_steps

    return " ".join(all_tokens)


# ---------------------------------------
# PREPROCESS ENTIRE DATAFRAME
# ---------------------------------------

def preprocess_dataframe(df):
    """
    Apply full preprocessing pipeline to a recipes dataframe.
    Produces:
    - ingredients_tokens
    - steps_tokens
    - search_text
    Also keeps ORIGINAL fields for UI display:
    - description
    - ingredients
    - steps
    """

    processed_rows = []

    for _, row in df.iterrows():

        # Processed (for IR)
        ing_tokens = preprocess_ingredients(row["ingredients"])
        step_tokens = preprocess_steps(row["steps"])

        search_text = build_search_text(
            row["name"],
            ing_tokens,
            step_tokens
        )

        # Store both PROCESSED + ORIGINAL DATA
        processed_rows.append({
            "id": row["id"],
            "name": row["name"],
            "minutes": row["minutes"],
            "tags": row["tags"],

            # Original text (UI display)
            "description": row.get("description", ""),
            "ingredients": row["ingredients"],     # string list
            "steps": row["steps"],                 # string list

            # Processed text (IR)
            "ingredients_tokens": ing_tokens,
            "steps_tokens": step_tokens,
            "search_text": search_text
        })

    return pd.DataFrame(processed_rows)
