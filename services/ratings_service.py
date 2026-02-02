import pandas as pd

START_RATING = 245

class RatingsService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = self.load_df()


    def load_df(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)

        # ensure date column is parsed
        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values("date").reset_index(drop=True)
        return df

    def save_df(self) -> None:
        self.df[["date", "diff"]].to_csv(self.csv_path, index=False)


    def decorate_df_columns(self) -> pd.DataFrame:
        df = self.df.copy()

        # Rating (cumulative)
        df["rating"] = START_RATING + df["diff"].cumsum()

        # Rolling diffs
        df["diff_7"] = df["rating"] - df["rating"].shift(7)
        df["diff_30"] = df["rating"] - df["rating"].shift(30)
        df["diff_365"] = df["rating"] - df["rating"].shift(365)

        df["avg_year_upto"] = df["rating"].shift(1).rolling(365, min_periods=1).mean()

        # Placeholder entropy functions
        df["entropy"] = abs(df["diff"]) / (4.5 + (
            df["rating"].shift(1) + df["diff_365"] - df["avg_year_upto"]) / 200)
        df["avg_entropy"] = df["entropy"].rolling(90, min_periods=1).mean()

        # Wins / 30
        def win_score(x):
            if x > 0: return 1
            if x == 0: return 0.5
            return 0

        df["win_score"] = df["diff"].apply(win_score)
        df["last_30_wins"] = df["win_score"].rolling(30).sum()

        # Year columns
        df["year"] = df["date"].dt.year

        df["wins"] = df.groupby("year")["diff"].transform(lambda s: (s > 0).cumsum())
        df["losses"] = df.groupby("year")["diff"].transform(lambda s: (s < 0).cumsum())
        df["ties"] = df.groupby("year")["diff"].transform(lambda s: (s == 0).cumsum())

        df["points_won"] = df.groupby("year")["diff"].transform(lambda s: s.clip(lower=0).cumsum())
        df["points_lost"] = df.groupby("year")["diff"].transform(lambda s: s.clip(upper=0).cumsum())
        df["total_points"] = df["points_won"] + df["points_lost"]

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
        df["record"] = df["rating"] == df["rating"].cummax()
        df["record"] = df["record"].apply(lambda x: "✓" if x else "")

        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["entropy"] = df["entropy"].round(3)
        df["avg_entropy"] = df["avg_entropy"].round(3)

        return df[["date", "rating", "diff", "diff_7", "diff_30", "diff_365", "entropy", "avg_entropy",
                "last_30_wins", "wins", "losses", "ties", "points_won", "points_lost", "total_points", "streak", "record"]]
