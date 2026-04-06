import pandas as pd
import datetime as dt

from services.utils import START_DATE, NOTIONAL_MULTIPLIER, START_RATING, TimePeriodStatistics


class AggregationService:

    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def produce_aggregate_stats(self, start_date: dt.date, end_date: dt.date):
        if start_date < START_DATE or end_date < START_DATE:
            raise ValueError(f"Dates must be on or after {START_DATE.isoformat()}")
        if start_date > end_date:
            raise ValueError("Start date must be on or before end date")

        if start_date.isoformat() == START_DATE.isoformat():
            starting_rating = START_RATING
        else:
            starting_rating = self.df.loc[
                pd.to_datetime(self.df["date"]) == pd.to_datetime(start_date), "rating"].iloc[0]

        # Filter the DataFrame to the specified date range
        mask = (pd.to_datetime(self.df["date"])>= pd.to_datetime(start_date)) & \
            (pd.to_datetime(self.df["date"]) <= pd.to_datetime(end_date))
        range_df = self.df.loc[mask].copy()

        average_rating = range_df["rating"].mean()
        average_entropy = range_df["entropy"].mean()

        wins = (range_df["diff"] > 0).sum()
        losses = (range_df["diff"] < 0).sum()
        ties = (range_df["diff"] == 0).sum()
        days = wins + losses + ties
        winning_percentage = (wins + ties/2) / days if days > 0 else 0

        points_won = range_df["diff"].clip(lower=0).sum()
        points_lost = abs(range_df["diff"].clip(upper=0).sum())
        total_points_awarded = points_won + points_lost
        points_per_day = total_points_awarded / days if days > 0 else 0
        point_winning_percentage = points_won / total_points_awarded if total_points_awarded > 0 else 0


        streak_flips = (range_df["streak"] == 1).sum()

        value_per_win = points_won / wins if wins > 0 else 0
        value_per_loss = points_lost / losses if losses > 0 else 0
        value_diff = value_per_win - value_per_loss

        notional_diff = \
            (points_won * NOTIONAL_MULTIPLIER + points_lost) * wins / \
            (wins * NOTIONAL_MULTIPLIER + losses) - \
            (points_won + points_lost * NOTIONAL_MULTIPLIER) * losses / \
            (wins + losses * NOTIONAL_MULTIPLIER) if (wins + losses) > 0 else 0

        total_diff = points_won - points_lost
        ending_rating = starting_rating + total_diff

        x_factor = total_diff - notional_diff

        return TimePeriodStatistics(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            starting_rating=starting_rating,
            ending_rating=ending_rating,
            average_rating=average_rating,
            average_entropy=average_entropy,
            days=days,
            wins=wins,
            losses=losses,
            ties=ties,
            streak_flips=streak_flips,
            winning_percentage=winning_percentage,
            points_won=points_won,
            points_lost=points_lost,
            total_points_awarded=total_points_awarded,
            points_per_day=points_per_day,
            point_winning_percentage=point_winning_percentage,
            value_per_win=value_per_win,
            value_per_loss=value_per_loss,
            value_diff=value_diff,
            notional_diff=notional_diff,
            x_factor=x_factor,
            total_diff=total_diff
        )

    def produce_yearly_stats(self) -> list[dict]:
        df = self.df.copy()
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df["prog_date"] = pd.to_datetime(df["date"])

        results = []
        for year, group in df.groupby("year"):
            stats = self.produce_aggregate_stats(
                start_date=group["prog_date"].min().date(),
                end_date=group["prog_date"].max().date()
            )
            results.append(stats.model_dump())
            results[-1]["year"] = year
            del results[-1]["start_date"]
            del results[-1]["end_date"]
        
        return results

    def produce_monthly_stats(self) -> list[dict]:
        df = self.df.copy()
        df["year"] = pd.to_datetime(df["date"]).dt.year
        df["month"] = pd.to_datetime(df["date"]).dt.month
        df["prog_date"] = pd.to_datetime(df["date"])

        results = []
        for (year, month), group in df.groupby(["year", "month"]):
            stats = self.produce_aggregate_stats(
                start_date=group["prog_date"].min().date(),
                end_date=group["prog_date"].max().date()
            )
            results.append(stats.model_dump())
            results[-1]["year"] = int(year)
            results[-1]["month"] = int(month)
            del results[-1]["start_date"]
            del results[-1]["end_date"]
        
        return results
    
    def produce_epoch_stats(self) -> list[dict]:
        df = self.df
        df["epoch"] = pd.to_datetime(df["date"]).view(int) // 10**16
        df["prog_date"] = pd.to_datetime(df["date"])

        results = []
        for epoch, group in df.groupby("epoch"):
            stats = self.produce_aggregate_stats(
                start_date=group["prog_date"].min().date(),
                end_date=group["prog_date"].max().date()
            )
            results.append(stats.model_dump())
            results[-1]["epoch"] = int(epoch)
        
        return results
