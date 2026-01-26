from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd

START_RATING = 245
CSV_PATH = "ratings.csv"

app = FastAPI()
# Serve static files under /static so API routes are not shadowed.
app.mount("/static", StaticFiles(directory=".", html=True), name="static")


@app.get("/")
def root():
    return FileResponse("index.html")

undo_stack = []

def load_df():
    # Read CSV and normalize common header variations (e.g. "Date", "+/-").
    df = pd.read_csv(CSV_PATH)

    # normalize column names to lowercase stripped strings
    df.rename(columns=lambda s: s.strip().lower(), inplace=True)

    # map common +/- header to 'diff'
    if "+/-" in df.columns:
        df.rename(columns={"+/-": "diff"}, inplace=True)

    # ensure date column is parsed
    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date").reset_index(drop=True)
    return df

def save_df(df):
    df[["date", "diff"]].to_csv(CSV_PATH, index=False)

def compute(df):
    df = df.copy()

    # Rating (cumulative)
    df["Rating"] = START_RATING + df["diff"].cumsum()

    # Rolling diffs
    df["WD"] = df["Rating"] - df["Rating"].shift(7)
    df["MD"] = df["Rating"] - df["Rating"].shift(30)
    df["YD"] = df["Rating"] - df["Rating"].shift(365)

    # Placeholder entropy functions
    df["entropy"] = 0.0
    df["avg_entropy"] = 0.0

    # Wins / 30
    def win_score(x):
        if x > 0: return 1
        if x == 0: return 0.5
        return 0

    df["win_score"] = df["diff"].apply(win_score)
    df["L30W"] = df["win_score"].rolling(30).sum()

    # Year columns
    df["year"] = df["date"].dt.year

    df["YTD W"] = df.groupby("year")["diff"].transform(lambda s: (s > 0).cumsum())
    df["YTD L"] = df.groupby("year")["diff"].transform(lambda s: (s < 0).cumsum())
    df["YTD T"] = df.groupby("year")["diff"].transform(lambda s: (s == 0).cumsum())

    df["YTD PW"] = df.groupby("year")["diff"].transform(lambda s: s.clip(lower=0).cumsum())
    df["YTD PL"] = df.groupby("year")["diff"].transform(lambda s: s.clip(upper=0).cumsum())
    df["Total YTD"] = df["YTD PW"] + df["YTD PL"]

    # Streak
    streak = []
    current = 0
    for d in df["diff"]:
        if d > 0:
            current = current + 1 if current > 0 else 1
        elif d < 0:
            current = current - 1 if current < 0 else -1
        else:
            current = 0
        streak.append(current)
    df["streak"] = streak

    # Record flag
    df["record"] = df["Rating"] == df["Rating"].cummax()

    df["+/-"] = df["diff"]
    df["ENT"] = df["entropy"]
    df["ENT90"] = df["avg_entropy"]
    df["YTD\nW"] = df["YTD W"]
    df["YTD\nL"] = df["YTD L"]
    df["YTD\nT"] = df["YTD T"]
    df["YTD\nPW"] = df["YTD PW"]
    df["YTD\nPL"] = df["YTD PL"]
    df["YTD\nTOT"] = df["Total YTD"]
    df["STRK"] = df["streak"]
    df["REC?"] = df["record"].apply(lambda x: "✓" if x else "")


    return df[["date", "Rating", "+/-", "WD", "MD", "YD", "ENT", "ENT90",
               "L30W", "YTD\nW", "YTD\nL", "YTD\nT", "YTD\nPW", "YTD\nPL", "YTD\nTOT", "STRK", "REC?"]]

@app.get("/data")
def get_data():
    df = compute(load_df())
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.fillna("").to_dict(orient="records")

class Edit(BaseModel):
    row: int
    diff: float

@app.post("/edit")
def edit(edit: Edit):
    df = load_df()
    undo_stack.append(df.copy())

    df.loc[edit.row, "diff"] = edit.diff
    save_df(df)

    return {"status": "ok"}

@app.post("/undo")
def undo():
    global undo_stack
    if not undo_stack:
        return {"status": "empty"}

    df = undo_stack.pop()
    save_df(df)
    return {"status": "ok"}