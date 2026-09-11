# Mod entry point. This is what the mod manager loads.
#
# One option (sprint speed multiplier), wired to the sprint speed edit in
# sprint.py. Enabling applies the chosen speed, disabling puts it back.

from __future__ import annotations

import mods_base
from mods_base import CoopSupport, SpinnerOption, build_mod

from . import sprint

# The mod manager has to be new enough for the APIs used here.
assert mods_base.__version_info__ >= (1, 4), "Please update the SDK mod manager"

# Menu text -> how many times faster than a normal sprint.
MULTIPLIERS: dict[str, float] = {
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


def _current_multiplier() -> float:
    # Falls back to the default if a saved setting no longer matches a choice.
    return MULTIPLIERS.get(speed_multiplier.value, MULTIPLIERS[DEFAULT_CHOICE])


def _on_multiplier_changed(_option: SpinnerOption, new_value: str) -> None:
    # Apply straight away so the new speed is felt on the next sprint.
    sprint.apply(MULTIPLIERS.get(new_value, MULTIPLIERS[DEFAULT_CHOICE]))


speed_multiplier = SpinnerOption(
    "Sprint Speed",
    DEFAULT_CHOICE,
    list(MULTIPLIERS),
    description=(
        "How much faster than normal you sprint. Normal walking speed is not"
        " changed. Takes effect the next time you sprint."
    ),
    on_change_while_enabled=_on_multiplier_changed,
)


def on_enable() -> None:
    sprint.apply(_current_multiplier())


def on_disable() -> None:
    sprint.restore()


mod = build_mod(
    on_enable=on_enable,
    on_disable=on_disable,
    coop_support=CoopSupport.ClientSide,
)
