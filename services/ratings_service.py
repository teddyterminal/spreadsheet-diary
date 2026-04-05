from enum import Enum
import pandas as pd

START_RATING = 245

class SpecialDay(Enum):
    NONE = 0
    SUPERB = 1
    TERRIBLE = 2
    MEMORABLE = 3
    DEVASTATING = 4
    LEGENDARY = 5
    CATACLYSMIC = 6

class Momentum(Enum):
    NONE = 0
    EXPECTED = 1
    UNEXPECTED = 2

class Mark(Enum):
    NONE = ""
    SWISH = "Swish"
    PENNANT = "Pennant"
    CHAMPIONSHIP = "Championship"
    BINGO = "Bingo"
    LOTTERY = "Lottery"
    ROYAL_FLUSH = "Royal Flush"
    RAIN = "Rain"
    DOWNPOUR = "Downpour"
    HURRICANE = "Hurricane"
    BOMB = "Bomb"
    NUKE = "Nuke"
    H_BOMB = "H-Bomb"

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


    def _ordinal_suffix(self, n: int) -> str:
        if 11 <= (n % 100) <= 13:
            return "th"
        elif n % 10 == 1:
            return "st"
        elif n % 10 == 2:
            return "nd"
        elif n % 10 == 3:
            return "rd"
        else:
            return "th"

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

        # --- New Columns ---
        # 1. Superb/Terrible
        superb_count = 0
        terrible_count = 0
        superb_terrible_col = []
        for d in df["diff"]:
            if d >= 5:
                superb_count += 1
                superb_terrible_col.append(f"{superb_count}{self._ordinal_suffix(superb_count)} Superb")
            elif d <= -5:
                terrible_count += 1
                superb_terrible_col.append(f"{terrible_count}{self._ordinal_suffix(terrible_count)} Terrible")
            else:
                superb_terrible_col.append("")
        df["superb"] = superb_terrible_col

        # 2. Memorable/Devastating
        memorable_count = 0
        devastating_count = 0
        memorable_devastating_col = []
        for d in df["diff"]:
            if d >= 10:
                memorable_count += 1
                memorable_devastating_col.append(f"{memorable_count}{self._ordinal_suffix(memorable_count)} Memorable")
            elif d <= -10:
                devastating_count += 1
                memorable_devastating_col.append(f"{devastating_count}{self._ordinal_suffix(devastating_count)} Devastating")
            else:
                memorable_devastating_col.append("")
        df["memorable"] = memorable_devastating_col

        # 3. Legendary/Cataclysmic
        legendary_count = 0
        cataclysmic_count = 0
        legendary_cataclysmic_col = []
        for d in df["diff"]:
            if d >= 20:
                legendary_count += 1
                legendary_cataclysmic_col.append(f"{legendary_count}{self._ordinal_suffix(legendary_count)} Legendary")
            elif d <= -20:
                cataclysmic_count += 1
                legendary_cataclysmic_col.append(f"{cataclysmic_count}{self._ordinal_suffix(cataclysmic_count)} Cataclysmic")
            else:
                legendary_cataclysmic_col.append("")
        df["legendary"] = legendary_cataclysmic_col

        # 4. Momentum
        momentum_col = []
        for i, d in enumerate(df["diff"]):
            l30w = df["last_30_wins"].iloc[i] if "last_30_wins" in df else 0
            special = None
            if d >= 5:
                special = 1
            elif d <= -5:
                special = -1
            if special:
                if (d >= 5 and l30w >= 15) or (d <= -5 and l30w <= 15):
                    momentum_col.append(Momentum.EXPECTED.name)
                else:
                    momentum_col.append(Momentum.UNEXPECTED.name)
            else:
                momentum_col.append("")
        df["momentum"] = momentum_col

        # 5. Mark
        mark_map = {
            ("Superb", "EXPECTED"): Mark.SWISH.value,
            ("Memorable", "EXPECTED"): Mark.PENNANT.value,
            ("Legendary", "EXPECTED"): Mark.CHAMPIONSHIP.value,
            ("Superb", "UNEXPECTED"): Mark.BINGO.value,
            ("Memorable", "UNEXPECTED"): Mark.LOTTERY.value,
            ("Legendary", "UNEXPECTED"): Mark.ROYAL_FLUSH.value,
            ("Terrible", "EXPECTED"): Mark.RAIN.value,
            ("Devastating", "EXPECTED"): Mark.DOWNPOUR.value,
            ("Cataclysmic", "EXPECTED"): Mark.HURRICANE.value,
            ("Terrible", "UNEXPECTED"): Mark.BOMB.value,
            ("Devastating", "UNEXPECTED"): Mark.NUKE.value,
            ("Cataclysmic", "UNEXPECTED"): Mark.H_BOMB.value,
        }
        mark_col = []
        for i in range(len(df)):
            label = ""
            # Find which special day
            if df["legendary"].iloc[i]:
                if "Legendary" in df["legendary"].iloc[i]:
                    label = "Legendary"
                elif "Cataclysmic" in df["legendary"].iloc[i]:
                    label = "Cataclysmic"
            elif df["memorable"].iloc[i]:
                if "Memorable" in df["memorable"].iloc[i]:
                    label = "Memorable"
                elif "Devastating" in df["memorable"].iloc[i]:
                    label = "Devastating"
            elif df["superb"].iloc[i]:
                if "Superb" in df["superb"].iloc[i]:
                    label = "Superb"
                elif "Terrible" in df["superb"].iloc[i]:
                    label = "Terrible"
            momentum = df["momentum"].iloc[i]
            mark = mark_map.get((label, momentum), "") if label and momentum else ""
            mark_col.append(mark)
        df["mark"] = mark_col

        # --- Color settings placeholder ---
        # You can set colors for these new columns in your frontend CSS as needed.

        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["entropy"] = df["entropy"].round(3)
        df["avg_entropy"] = df["avg_entropy"].round(3)

        return df[["date", "rating", "diff", "diff_7", "diff_30", "diff_365", "entropy", "avg_entropy",
            "last_30_wins", "wins", "losses", "ties", "points_won", "points_lost", "total_points", "streak", "record",
            "superb", "memorable", "legendary", "momentum", "mark"]]
