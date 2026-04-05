from enum import Enum

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

