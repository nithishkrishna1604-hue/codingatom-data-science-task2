# IMDb Top 250 Movies — Task 2: Interactive Dashboard

**CodingAtom Data Science & Analytics Internship — Task 2**

A Streamlit dashboard built on top of the Task 1 analysis, aimed at a
non-technical reader: no code visible, no jargon left unexplained, just the
three questions, the charts, the honest caveats, and a clear recommendation.

**Live app:** https://codingatom-data-science-task2-fdsqpc9orrgltancbmzdna.streamlit.app/

**Task 1 analysis repo:** https://github.com/nithishkrishna1604-hue/codingatom-data-science-task1

## What it shows

- **Overview & Takeaways** — the problem, the three key takeaways, and one
  recommended action, written for someone who won't read the underlying code.
- **Q1 — Genres** — which genres rate highest and which are most popular,
  with an interactive metric switcher (rating / movie count / votes).
- **Q2 — Budget vs. Gross** — the scatter plot, the correlation, and its 95%
  confidence interval, with a trend-line toggle and a sortable movie table.
- **Q3 — Rating vs. Votes** — the same treatment for rating vs. popularity.
- **Data & Limitations** — the cleaning decisions, the bias/confounders, and
  a preview of the untouched raw data.

Every number on the page is computed live from the raw CSV via
`analysis.py` — nothing is a hardcoded value or a pasted screenshot.

## Setup — how to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Project structure

```
app.py           Streamlit UI — five tabs, no analysis logic of its own
analysis.py       Pure Python/pandas cleaning + analysis functions,
                   independently testable without Streamlit
data/             The raw CSV (bundled so the app is self-contained)
requirements.txt
```

`analysis.py` is kept separate from `app.py` deliberately: it can be
imported and unit-tested with plain Python (`python -c "from analysis import
load_and_clean, genre_table; ..."`) to verify the numbers before they ever
reach the UI. That's also what makes the whole thing reproducible from raw
data — the app doesn't read any pre-computed file, it recomputes everything
from `data/imdb_top250.csv` on every load (and caches the result with
`st.cache_data` so it doesn't recompute needlessly on every interaction).

## Decisions made

- **Streamlit over a static notebook**, to get an actually interactive
  dashboard (metric switcher, trend-line toggles, sortable tables) that a
  non-technical reader can explore themselves, not just read top to bottom.
- **matplotlib over Plotly**, to keep the dependency list to what's
  guaranteed to install cleanly on Streamlit Community Cloud's free tier
  with no extra system packages.
- **Same cleaning logic as Task 1** (same outlier flagging, same exclusion
  rules), reimplemented as importable functions rather than copy-pasted, so
  Task 1 and Task 2 can never silently drift out of sync with each other.
- **95% confidence intervals shown alongside every correlation** (Fisher's z
  method), so the dashboard doesn't present r=0.75 or r=0.55 as more certain
  than a 219- or 250-movie sample actually supports.

## Key results (reproduced live by the app)

| Question | Result |
|---|---|
| Q1 — Genres | Fantasy highest-rated (8.42, n=18); Sci-Fi most popular (~1.09M votes/movie) |
| Q2 — Budget vs. Gross | r = 0.75, 95% CI 0.68–0.80 (n=219/250) |
| Q3 — Rating vs. Votes | r = 0.55, 95% CI 0.46–0.63 (n=250/250) |

## Limitations (also shown in-app)

The IMDb Top 250 is a curated, already highly-rated sample — not a random
sample of movies — so results describe this list, not the movie industry as
a whole. See the in-app "Data & Limitations" tab for the full list
(selection bias, small sample size, user-generated ratings, no inflation
adjustment, worldwide gross ≠ profit, overlapping genres).

## Deploying (free tier)

1. Push this repo to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and click "New app."
3. Point it at this repo, branch `main`, main file `app.py`.
4. Deploy — Streamlit Community Cloud is free and needs no paid account.
5. Copy the live app URL back into this README and your LinkedIn post.

## Stack

Python · pandas · NumPy · Matplotlib · Streamlit
