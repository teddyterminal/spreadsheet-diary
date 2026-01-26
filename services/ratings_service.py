import pandas as pd

START_RATING = 245

class RatingsService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = self.load_df()


    def load_df(self) -> pd.DataFrame:
        # Read CSV and normalize common header variations (e.g. "Date", "+/-").
        df = pd.read_csv(self.csv_path)

        # normalize column names to lowercase stripped strings
        df.rename(columns=lambda s: s.strip().lower(), inplace=True)

        # map common +/- header to 'diff'
        if "+/-" in df.columns:
            df.rename(columns={"+/-": "diff"}, inplace=True)

        # ensure date column is parsed
        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values("date").reset_index(drop=True)
        return df

    def save_df(self) -> None:
        self.df[["date", "diff"]].to_csv(self.csv_path, index=False)


    def decorate_df_columns(self) -> pd.DataFrame:
        df = self.df.copy()

        # Rating (cumulative)
        df["Rating"] = START_RATING + df["diff"].cumsum()

        # Rolling diffs
        df["WD"] = df["Rating"] - df["Rating"].shift(7)
        df["MD"] = df["Rating"] - df["Rating"].shift(30)
        df["YD"] = df["Rating"] - df["Rating"].shift(365)

        df["avg_year_upto"] = df["Rating"].shift(1).rolling(365, min_periods=1).mean()

        # Placeholder entropy functions
        df["entropy"] = abs(df["diff"]) / (4.5 + (
            df["Rating"].shift(1) + df["YD"] - df["avg_year_upto"]) / 200)
        df["avg_entropy"] = df["entropy"].rolling(90, min_periods=1).mean()

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
            streak.append(abs(current))
        df["streak"] = streak

        # Record flag
        df["record"] = df["Rating"] == df["Rating"].cummax()

        df["+/-"] = df["diff"]
        df["ENT"] = df["entropy"].round(3)
        df["ENT90"] = df["avg_entropy"].round(3)
        df["YTD\nW"] = df["YTD W"]
        df["YTD\nL"] = df["YTD L"]
        df["YTD\nT"] = df["YTD T"]
        df["YTD\nPW"] = df["YTD PW"]
        df["YTD\nPL"] = df["YTD PL"]
        df["YTD\nTOT"] = df["Total YTD"]
        df["STRK"] = df["streak"]
        df["REC?"] = df["record"].apply(lambda x: "✓" if x else "")
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")


        return df[["date", "Rating", "+/-", "WD", "MD", "YD", "ENT", "ENT90",
                "L30W", "YTD\nW", "YTD\nL", "YTD\nT", "YTD\nPW", "YTD\nPL", "YTD\nTOT", "STRK", "REC?"]]

