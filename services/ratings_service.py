from enum import Enum
import pandas as pd
from services.utils import START_RATING, SpecialDay, Momentum, Mark, mark_mapping, \
    SUPERB_TERRIBLE_THRESHOLD, MEMORABLE_DEVASTATING_THRESHOLD, LEGENDARY_CATACLYSMIC_THRESHOLD
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

    def calculate_special_day(self, diff: float, last_30_wins: int) -> tuple[SpecialDay, Momentum, Mark]:
        special_day = None
        momentum = None
        mark = None

        if diff >= SUPERB_TERRIBLE_THRESHOLD:
            special_day = SpecialDay.SUPERB
        elif diff <= -SUPERB_TERRIBLE_THRESHOLD:
            special_day = SpecialDay.TERRIBLE

        if diff >= MEMORABLE_DEVASTATING_THRESHOLD:
            special_day = SpecialDay.MEMORABLE
        elif diff <= -MEMORABLE_DEVASTATING_THRESHOLD:
            special_day = SpecialDay.DEVASTATING

        if diff >= LEGENDARY_CATACLYSMIC_THRESHOLD:
            special_day = SpecialDay.LEGENDARY
        elif diff <= -LEGENDARY_CATACLYSMIC_THRESHOLD:
            special_day = SpecialDay.CATACLYSMIC

        if special_day:
            if (diff >= SUPERB_TERRIBLE_THRESHOLD and last_30_wins >= 15) or \
                    (diff <= -SUPERB_TERRIBLE_THRESHOLD and last_30_wins <= 15):
                momentum = Momentum.EXPECTED
            else:
                momentum = Momentum.UNEXPECTED

            mark = mark_mapping[special_day, momentum]

        return special_day, momentum, mark

    def decorate_df_columns(self) -> pd.DataFrame:
        df = self.df.copy()

        # Rating (cumulative)
        df["rating"] = START_RATING + df["diff"].cumsum()

        # Rolling diffs
        df["diff_7"] = df["rating"] - df["rating"].shift(7)
        df["diff_30"] = df["rating"] - df["rating"].shift(30)
        df["diff_365"] = df["rating"] - df["rating"].shift(365)

        df["avg_year_upto"] = df["rating"].shift(1).rolling(365, min_periods=1).mean()

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

        # Special Days
        superb_count = 0
        terrible_count = 0
        memorable_count = 0
        devastating_count = 0
        legendary_count = 0
        cataclysmic_count = 0

        mark_counts = {
            Mark.SWISH: 0,
            Mark.PENNANT: 0,
            Mark.CHAMPIONSHIP: 0,
            Mark.BINGO: 0,
            Mark.LOTTERY: 0,
            Mark.ROYAL_FLUSH: 0,
            Mark.RAIN: 0,
            Mark.DOWNPOUR: 0,
            Mark.HURRICANE: 0,
            Mark.BOMB: 0,
            Mark.NUKE: 0,
            Mark.H_BOMB: 0
        }

        superb_terrible_col = []
        memorable_devastating_col = []
        legendary_cataclysmic_col = []

        momentum_col = []
        mark_col = []

        for _, row in enumerate(df[["diff", "last_30_wins"]].itertuples()):
            this_special_day, this_momentum, this_mark = self.calculate_special_day(row.diff, row.last_30_wins)

            superb_terrible_col.append("")
            memorable_devastating_col.append("")
            legendary_cataclysmic_col.append("")
            momentum_col.append("")
            mark_col.append("")

            if this_special_day is None:
                continue
            
            # today was a special day
            match this_special_day:
                case SpecialDay.SUPERB | SpecialDay.MEMORABLE | SpecialDay.LEGENDARY:
                    superb_count += 1
                    superb_terrible_col[-1] = f"{superb_count}{self._ordinal_suffix(superb_count)} Superb"
                case SpecialDay.TERRIBLE:
                    terrible_count += 1
                    superb_terrible_col[-1] = f"{terrible_count}{self._ordinal_suffix(terrible_count)} Terrible"
                case SpecialDay.MEMORABLE | SpecialDay.LEGENDARY:
                    memorable_count += 1
                    memorable_devastating_col[-1] = \
                        f"{memorable_count}{self._ordinal_suffix(memorable_count)} Memorable"
                case SpecialDay.DEVASTATING | SpecialDay.CATACLYSMIC:
                    devastating_count += 1
                    memorable_devastating_col[-1] = \
                        f"{devastating_count}{self._ordinal_suffix(devastating_count)} Devastating"
                case SpecialDay.LEGENDARY:
                    legendary_count += 1
                    legendary_cataclysmic_col[-1] = \
                        f"{legendary_count}{self._ordinal_suffix(legendary_count)} Legendary"
                case SpecialDay.CATACLYSMIC:
                    cataclysmic_count += 1
                    legendary_cataclysmic_col[-1] = \
                        f"{cataclysmic_count}{self._ordinal_suffix(cataclysmic_count)} Cataclysmic"

            momentum_col[-1] = this_momentum.value if this_momentum else ""

            if this_mark:
                mark_counts[this_mark] += 1
                mark_col[-1] = f"{mark_counts[this_mark]}{self._ordinal_suffix(mark_counts[this_mark])} {this_mark.value}"


        df["superb"] = superb_terrible_col
        df["memorable"] = memorable_devastating_col
        df["legendary"] = legendary_cataclysmic_col
        df["momentum"] = momentum_col
        df["mark"] = mark_col

        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["entropy"] = df["entropy"].round(3)
        df["avg_entropy"] = df["avg_entropy"].round(3)

        return df[["date", "rating", "diff", "diff_7", "diff_30", "diff_365", "entropy", "avg_entropy",
            "last_30_wins", "wins", "losses", "ties", "points_won", "points_lost", "total_points", "streak", "record",
            "superb", "memorable", "legendary", "momentum", "mark"]]
