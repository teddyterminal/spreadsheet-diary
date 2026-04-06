from enum import Enum
import datetime as dt
from pydantic import BaseModel

START_RATING = 245
START_DATE = dt.datetime.fromisoformat("2010-01-01").date()

NOTIONAL_MULTIPLIER = 2

SUPERB_TERRIBLE_THRESHOLD = 5
MEMORABLE_DEVASTATING_THRESHOLD = 10
LEGENDARY_CATACLYSMIC_THRESHOLD = 20

class SpecialDay(Enum):
    SUPERB = "Superb"
    TERRIBLE = "Terrible"
    MEMORABLE = "Memorable"
    DEVASTATING = "Devastating"
    LEGENDARY = "Legendary"
    CATACLYSMIC = "Cataclysmic"

class Momentum(Enum):
    EXPECTED = "Expected"
    UNEXPECTED = "Unexpected"

class Mark(Enum):
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

mark_mapping = {
    (SpecialDay.SUPERB, Momentum.EXPECTED): Mark.SWISH,
    (SpecialDay.MEMORABLE, Momentum.EXPECTED): Mark.PENNANT,
    (SpecialDay.LEGENDARY, Momentum.EXPECTED): Mark.CHAMPIONSHIP,

    (SpecialDay.SUPERB, Momentum.UNEXPECTED): Mark.BINGO,
    (SpecialDay.MEMORABLE, Momentum.UNEXPECTED): Mark.LOTTERY,
    (SpecialDay.LEGENDARY, Momentum.UNEXPECTED): Mark.ROYAL_FLUSH,

    (SpecialDay.TERRIBLE, Momentum.EXPECTED): Mark.RAIN,
    (SpecialDay.DEVASTATING, Momentum.EXPECTED): Mark.DOWNPOUR,
    (SpecialDay.CATACLYSMIC, Momentum.EXPECTED): Mark.HURRICANE,

    (SpecialDay.TERRIBLE, Momentum.UNEXPECTED): Mark.BOMB,
    (SpecialDay.DEVASTATING, Momentum.UNEXPECTED): Mark.NUKE,
    (SpecialDay.CATACLYSMIC, Momentum.UNEXPECTED): Mark.H_BOMB
}

class TimePeriodStatistics(BaseModel):
    start_date: dt.date
    end_date: dt.date
    starting_rating: float
    ending_rating: float

    average_rating: float
    average_entropy: float

    wins: int
    losses: int
    ties: int
    streak_flips: int
    winning_percentage: float

    points_won: float
    points_lost: float
    total_points_awarded: float
    points_per_day: float
    point_winning_percentage: float

    value_per_win: float
    value_per_loss: float
    notional_diff: float
    x_factor: float
    total_diff: float
