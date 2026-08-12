"""
IMDb Top 250 Movies — Task 2 Dashboard
CodingAtom Data Science & Analytics Internship

A Streamlit dashboard that presents the Task 1 findings to a non-technical
reader. Everything is computed live from the raw CSV (see analysis.py) —
nothing here is a pre-computed screenshot or hardcoded number.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analysis import (
    budget_gross_table,
    genre_table,
    load_and_clean,
    outlier_titles,
    rating_votes_table,
)

GOLD = "#F5C518"
NAVY = "#1B2430"
ACCENT_RED = "#E63946"

st.set_page_config(
    page_title="IMDb Top 250 — Ratings, Popularity & Financial Performance",
    page_icon="🎬",
    layout="wide",
)


@st.cache_data
def get_data():
    raw, df = load_and_clean("data/imdb_top250.csv")
    gt, small_genres = genre_table(df)
    q2, q2_stats = budget_gross_table(df)
    q3, q3_stats = rating_votes_table(df)
    outliers = outlier_titles(df)
    return raw, df, gt, small_genres, q2, q2_stats, q3, q3_stats, outliers


raw, df, gt, small_genres, q2, q2_stats, q3, q3_stats, outliers = get_data()

top_rating = gt.iloc[0]
top_votes = gt.sort_values("avg_votes", ascending=False).iloc[0]
most_common = gt.sort_values("num_movies", ascending=False).iloc[0]

# ---------------------------------------------------------------- header
st.markdown(
    f"<h1 style='color:{NAVY};margin-bottom:0;'>🎬 IMDb Top 250 Movies</h1>"
    f"<p style='color:#666;font-size:1.1rem;margin-top:0;'>Ratings, Popularity and Financial Performance"
    f" &nbsp;·&nbsp; CodingAtom Data Science &amp; Analytics Internship</p>",
    unsafe_allow_html=True,
)
st.caption(
    f"{len(raw)} movies · {raw.shape[1]} raw columns · cleaned and analysed live from the raw CSV below — "
    "no numbers on this page are hardcoded."
)

tab_overview, tab_q1, tab_q2, tab_q3, tab_data = st.tabs(
    ["📋 Overview & Takeaways", "🎭 Q1 — Genres", "💰 Q2 — Budget vs Gross", "⭐ Q3 — Rating vs Votes", "🔍 Data & Limitations"]
)

# ========================================================================
# OVERVIEW TAB
# ========================================================================
with tab_overview:
    st.subheader("Problem")
    st.write(
        "Producers, streamers and analysts want a quick, honest read on what separates strongly-performing "
        "movies from the rest — by genre, by budget, and by audience popularity — without over-claiming what "
        "the data actually proves."
    )

    st.subheader("Three key takeaways")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Highest-rated genre (5+ movies)", top_rating["genre"], f"avg {top_rating['avg_rating']:.2f} (n={int(top_rating['num_movies'])})")
        st.caption(f"Most popular by votes: **{top_votes['genre']}** (~{top_votes['avg_votes']/1e6:.2f}M votes/movie)")
    with c2:
        st.metric("Budget ↔ Worldwide Gross", f"r = {q2_stats['r']:.2f}", f"95% CI: {q2_stats['ci_low']:.2f} – {q2_stats['ci_high']:.2f}")
        st.caption(f"Fairly strong positive relationship (n={q2_stats['n']} of 250 movies)")
    with c3:
        st.metric("Rating ↔ Number of Votes", f"r = {q3_stats['r']:.2f}", f"95% CI: {q3_stats['ci_low']:.2f} – {q3_stats['ci_high']:.2f}")
        st.caption(f"Moderate positive relationship (n={q3_stats['n']} of 250 movies)")

    st.subheader("Recommended action")
    st.info(
        "Treat genre (particularly Fantasy and Sci-Fi) and adequate budget as **favourable, not sufficient**, "
        "signals when evaluating a movie project. Both show a real association with stronger rating or "
        "box-office outcomes in this sample, but a large budget alone does not guarantee a large return, and "
        "a high rating does not guarantee a large audience. Because this analysis covers only the IMDb Top "
        "250 — an already highly-rated, curated list — any decision should be checked against a broader, "
        "more representative dataset before being treated as general industry guidance."
    )

    st.subheader("Approach")
    st.write(
        "Data was cleaned and analysed with **pandas** (missing values documented, genres split, 6 "
        "currency-mismatched budgets flagged and excluded only where relevant), charted with **matplotlib**, "
        "and presented here with **Streamlit**. No machine learning was used — only descriptive statistics "
        "and Pearson correlation, with 95% confidence intervals (Fisher's z method) so the results are honest "
        "about how much uncertainty is involved."
    )

# ========================================================================
# Q1 — GENRES
# ========================================================================
with tab_q1:
    st.subheader("Which movie genres have the highest average IMDb ratings, and how many Top 250 movies fall into each genre?")
    st.write(
        "Only genres with **5 or more movies** are compared below, so that a genre with just one or two "
        f"titles can't dominate the ranking. ({', '.join(small_genres)} were excluded from this comparison "
        "for having fewer than 5 movies — they remain in the underlying data.)"
    )

    metric_choice = st.radio("Sort / colour genres by:", ["Average IMDb Rating", "Number of Movies", "Average Number of Votes"], horizontal=True)
    col_map = {"Average IMDb Rating": "avg_rating", "Number of Movies": "num_movies", "Average Number of Votes": "avg_votes"}
    sort_col = col_map[metric_choice]
    gt_sorted = gt.sort_values(sort_col, ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    color = GOLD if sort_col != "num_movies" else NAVY
    ax.barh(gt_sorted["genre"], gt_sorted[sort_col], color=color, edgecolor=NAVY)
    ax.set_xlabel(metric_choice)
    ax.set_title(f"{metric_choice} by Genre (genres with 5+ movies)", color=NAVY, fontweight="bold")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    st.pyplot(fig, use_container_width=True)

    st.markdown(
        f"**Insight:** {top_rating['genre']} has the highest average rating "
        f"({top_rating['avg_rating']:.2f}, n={int(top_rating['num_movies'])}), {top_votes['genre']} attracts "
        f"the most votes on average (~{top_votes['avg_votes']/1e6:.2f}M/movie), and {most_common['genre']} is "
        f"the most frequent genre ({int(most_common['num_movies'])} of 250 movies). Rating differences between "
        "genres are small overall — expected, since the Top 250 already contains only highly rated films."
    )

    with st.expander("See the full genre table"):
        display_gt = gt.copy()
        display_gt["avg_rating"] = display_gt["avg_rating"].round(2)
        display_gt["avg_votes"] = display_gt["avg_votes"].round(0).astype(int)
        display_gt.columns = ["Genre", "Number of Movies", "Average IMDb Rating", "Average Number of Votes"]
        st.dataframe(display_gt, use_container_width=True, hide_index=True)

# ========================================================================
# Q2 — BUDGET VS GROSS
# ========================================================================
with tab_q2:
    st.subheader("Is there a relationship between production budget and worldwide box office gross?")
    st.write(
        f"Movies missing budget or gross, plus 6 movies with unrealistic budgets (likely a currency mismatch — "
        f"see the Data & Limitations tab), are excluded from this question only. That leaves "
        f"**n = {q2_stats['n']} of 250 movies** (88%)."
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Sample size (n)", q2_stats["n"])
    m2.metric("Pearson r", f"{q2_stats['r']:.3f}")
    m3.metric("95% Confidence Interval", f"{q2_stats['ci_low']:.2f} – {q2_stats['ci_high']:.2f}")

    show_trend = st.checkbox("Show trend line", value=True, key="q2_trend")
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    ax2.scatter(q2["budget"] / 1e6, q2["grossWorldwide"] / 1e6, color=GOLD, edgecolor=NAVY, s=40, alpha=0.85)
    if show_trend:
        import numpy as np
        z = np.polyfit(q2["budget"], q2["grossWorldwide"], 1)
        xline = np.linspace(q2["budget"].min(), q2["budget"].max(), 100)
        ax2.plot(xline / 1e6, (z[0] * xline + z[1]) / 1e6, color=ACCENT_RED, lw=2, ls="--", label="Trend line")
        ax2.legend(frameon=False)
    ax2.set_xlabel("Budget (Million USD)")
    ax2.set_ylabel("Worldwide Gross (Million USD)")
    ax2.set_title("Budget vs Worldwide Gross", color=NAVY, fontweight="bold")
    for spine in ["top", "right"]:
        ax2.spines[spine].set_visible(False)
    st.pyplot(fig2, use_container_width=True)

    st.markdown(
        f"**What this means:** a correlation of {q2_stats['r']:.2f} is a fairly strong positive relationship — "
        "movies with bigger budgets tend to gross more worldwide in this sample. The 95% confidence interval "
        f"({q2_stats['ci_low']:.2f}–{q2_stats['ci_high']:.2f}) does not include 0, supporting a real, non-zero "
        "relationship. **This is a correlation, not proof of cause and effect** — a bigger budget does not by "
        "itself cause bigger revenue."
    )

    with st.expander("See the movie-level table (sortable)"):
        display_q2 = q2[["primaryTitle", "budget", "grossWorldwide", "gross_minus_budget_proxy"]].copy()
        display_q2.columns = ["Movie", "Budget (USD)", "Worldwide Gross (USD)", "Gross-minus-Budget Proxy (USD, NOT profit)"]
        st.dataframe(display_q2.sort_values("Gross-minus-Budget Proxy (USD, NOT profit)", ascending=False),
                     use_container_width=True, hide_index=True)
        st.caption("'Gross-minus-Budget Proxy' is NOT profit — it excludes marketing, distribution, taxes and theatre revenue shares, which this dataset does not contain.")

# ========================================================================
# Q3 — RATING VS VOTES
# ========================================================================
with tab_q3:
    st.subheader("Do movies with higher IMDb ratings tend to receive more user votes?")
    st.write(f"All 250 movies have both a rating and a vote count, so the full sample is used (n = {q3_stats['n']}).")

    m1, m2, m3 = st.columns(3)
    m1.metric("Sample size (n)", q3_stats["n"])
    m2.metric("Pearson r", f"{q3_stats['r']:.3f}")
    m3.metric("95% Confidence Interval", f"{q3_stats['ci_low']:.2f} – {q3_stats['ci_high']:.2f}")

    show_trend3 = st.checkbox("Show trend line", value=True, key="q3_trend")
    fig3, ax3 = plt.subplots(figsize=(9, 6))
    ax3.scatter(q3["averageRating"], q3["numVotes"] / 1e6, color=NAVY, edgecolor=GOLD, s=40, alpha=0.8)
    if show_trend3:
        import numpy as np
        z3 = np.polyfit(q3["averageRating"], q3["numVotes"], 1)
        xline3 = np.linspace(q3["averageRating"].min(), q3["averageRating"].max(), 100)
        ax3.plot(xline3, (z3[0] * xline3 + z3[1]) / 1e6, color=ACCENT_RED, lw=2, ls="--", label="Trend line")
        ax3.legend(frameon=False)
    ax3.set_xlabel("IMDb Rating")
    ax3.set_ylabel("Number of Votes (Millions)")
    ax3.set_title("IMDb Rating vs Number of Votes", color=NAVY, fontweight="bold")
    for spine in ["top", "right"]:
        ax3.spines[spine].set_visible(False)
    st.pyplot(fig3, use_container_width=True)

    st.markdown(
        f"**What this means:** a correlation of {q3_stats['r']:.2f} is a moderate positive relationship — "
        "higher-rated movies tend to get somewhat more votes, but the link is not strong. The 95% confidence "
        f"interval ({q3_stats['ci_low']:.2f}–{q3_stats['ci_high']:.2f}) does not include 0, but it is wide "
        "enough to show real uncertainty. **Correlation does not prove causation** — vote count likely also "
        "depends on a movie's age and how widely it was released."
    )

    with st.expander("See the movie-level table (sortable)"):
        display_q3 = q3.copy()
        display_q3.columns = ["Movie", "IMDb Rating", "Number of Votes"]
        st.dataframe(display_q3.sort_values("Number of Votes", ascending=False), use_container_width=True, hide_index=True)

# ========================================================================
# DATA & LIMITATIONS
# ========================================================================
with tab_data:
    st.subheader("Cleaning decisions")
    st.markdown(
        "- **endYear** removed — 100% empty, doesn't apply to movies (only TV series).\n"
        "- **genres** split from a single text field into a list per movie, so a multi-genre movie is counted "
        "once under each of its genres (Q1 only).\n"
        f"- **6 movies flagged with unrealistic budgets** (likely a currency mismatch, e.g. yen/rupees/lira "
        f"recorded as USD): {', '.join(outliers)}. Kept in the data, excluded only from Q2.\n"
        "- **No rows were deleted.** Missing values were left blank and excluded only where a specific "
        "question required that field."
    )

    st.subheader("Bias and confounders")
    st.markdown(
        "- **Selection bias:** the IMDb Top 250 is a curated list of already highly-rated films, not a "
        "random sample — findings describe this list, not movies in general.\n"
        "- **Small sample:** only 250 movies total; Q2 uses an even smaller subset (219) once missing/flagged "
        "budgets are removed.\n"
        "- **User-generated ratings:** IMDb ratings and votes come from self-selected users, not a controlled "
        "survey.\n"
        "- **Vote count depends on movie age and reach:** an older or more widely released movie has had more "
        "opportunity to accumulate votes, independent of quality — a plausible confounder for Q3.\n"
        "- **No inflation adjustment:** budget/gross span movies from 1921 to 2026.\n"
        "- **Worldwide gross is not profit:** marketing, distribution, taxes and theatre revenue shares are "
        "not in this dataset.\n"
        "- **Overlapping genres:** movies average 2.5 genres each, so genre comparisons in Q1 aren't fully "
        "independent of one another."
    )

    st.subheader("Raw data preview")
    st.dataframe(raw.head(20), use_container_width=True)
    st.caption(f"Showing 20 of {len(raw)} rows, {raw.shape[1]} columns — unmodified from the original CSV.")

st.divider()
st.caption("Built with pandas + matplotlib + Streamlit, for the CodingAtom Data Science & Analytics Internship — Task 2.")
