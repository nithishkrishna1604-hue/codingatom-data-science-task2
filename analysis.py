"""
analysis.py — cleaning + analysis logic for the IMDb Top 250 dashboard.

Kept separate from app.py (the Streamlit UI) so it can be tested and
verified on its own with plain Python, with no Streamlit dependency.
This is the same logic used in imdb_analysis.py (Task 1), refactored
into reusable functions so the dashboard reproduces everything from
the raw CSV rather than reading pre-computed files.
"""

import ast
import math

import numpy as np
import pandas as pd

BUDGET_OUTLIER_THRESHOLD = 400_000_000
MIN_GENRE_N = 5
Z_95 = 1.959964  # critical value for a 95% two-tailed confidence interval


def parse_genres(x):
    if pd.isna(x):
        return []
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        return [g.strip(" '\"[]") for g in str(x).split(",")]


def load_and_clean(csv_path):
    """Load the raw CSV and return (raw_df, cleaned_df). Raw is untouched."""
    raw = pd.read_csv(csv_path)
    df = raw.copy()

    if "endYear" in df.columns:
        df = df.drop(columns=["endYear"])

    df["genres_list"] = df["genres"].apply(parse_genres)
    df["genre_count"] = df["genres_list"].apply(len)

    numeric_cols = ["budget", "grossWorldwide", "averageRating", "numVotes",
                     "runtimeMinutes", "metascore"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["budget_flag"] = np.where(
        df["budget"] > BUDGET_OUTLIER_THRESHOLD, "excluded_likely_currency_mismatch", "ok"
    )
    df["valid_for_q2"] = (
        df["budget"].notna() & df["grossWorldwide"].notna() & (df["budget_flag"] == "ok")
    )
    return raw, df


def genre_table(df, min_n=MIN_GENRE_N):
    """Q1: genre-level table (n>=min_n), sorted by average rating descending."""
    exploded = df.explode("genres_list").rename(columns={"genres_list": "genre"})
    stats = exploded.groupby("genre").agg(
        num_movies=("primaryTitle", "count"),
        avg_rating=("averageRating", "mean"),
        avg_votes=("numVotes", "mean"),
    ).reset_index()
    kept = stats[stats["num_movies"] >= min_n].sort_values("avg_rating", ascending=False).reset_index(drop=True)
    small = stats[stats["num_movies"] < min_n]["genre"].tolist()
    return kept, small


def fisher_ci(r, n, z=Z_95):
    """95% confidence interval for a Pearson r via Fisher's z transformation."""
    if n <= 3 or abs(r) >= 1:
        return (float("nan"), float("nan"))
    zr = 0.5 * math.log((1 + r) / (1 - r))
    se = 1 / math.sqrt(n - 3)
    lo_z, hi_z = zr - z * se, zr + z * se
    return math.tanh(lo_z), math.tanh(hi_z)


def budget_gross_table(df):
    """Q2: movies with valid budget & gross (outliers excluded), plus stats."""
    q2 = df[df["valid_for_q2"]].copy()
    q2["gross_minus_budget_proxy"] = q2["grossWorldwide"] - q2["budget"]
    r = q2["budget"].corr(q2["grossWorldwide"])
    lo, hi = fisher_ci(r, len(q2))
    stats = {
        "n": len(q2),
        "r": r,
        "ci_low": lo,
        "ci_high": hi,
        "median_budget": q2["budget"].median(),
        "median_gross": q2["grossWorldwide"].median(),
    }
    return q2, stats


def rating_votes_table(df):
    """Q3: full sample rating vs votes, plus stats."""
    q3 = df[["primaryTitle", "averageRating", "numVotes"]].dropna().copy()
    r = q3["averageRating"].corr(q3["numVotes"])
    lo, hi = fisher_ci(r, len(q3))
    stats = {
        "n": len(q3),
        "r": r,
        "ci_low": lo,
        "ci_high": hi,
        "rating_min": q3["averageRating"].min(),
        "rating_max": q3["averageRating"].max(),
    }
    return q3, stats


def outlier_titles(df):
    return df.loc[df["budget_flag"] != "ok", "primaryTitle"].tolist()
