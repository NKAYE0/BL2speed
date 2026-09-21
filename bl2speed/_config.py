# Shared mod details, used by both the new-SDK and old-SDK front ends.
#
# Keeping them here means the speed choices and the mod's name/version are
# written down once, not copied into two places that can drift apart.

from __future__ import annotations

NAME = "Speed"
AUTHOR = "NK"
VERSION = "1.0.0"
DESCRIPTION = "Sprint faster. Normal walking speed is not changed."

# Menu text -> how many times faster than a normal sprint. 1x is the game's
# own sprint speed, i.e. no change.
MULTIPLIERS = {
    "1x": 1.0,
    "1.25x": 1.25,
    "1.5x": 1.5,
    "1.75x": 1.75,
    "2x": 2.0,
    "2.5x": 2.5,
    "3x": 3.0,
    "5x": 5.0,
    "10x": 10.0,
}

DEFAULT_CHOICE = "1.5x"

OPTION_NAME = "Sprint Speed"
OPTION_DESCRIPTION = (
    "How much faster than normal you sprint. 1x leaves sprinting at the game's"
    " normal speed. Walking speed is never changed. Takes effect the next time"
    " you sprint."
)


def multiplier_for(choice: str) -> float:
    """Turn a menu choice into a number, falling back to the default."""
    return MULTIPLIERS.get(choice, MULTIPLIERS[DEFAULT_CHOICE])
