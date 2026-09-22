# Mod entry point. This is what the mod manager loads.
#
# Holds the one option and wires it to the sprint logic. Everything else -
# name, version, author, description, coop support, supported games - comes
# from pyproject.toml, so it's only written down in one place.

from mods_base import SpinnerOption, build_mod

from . import sprint

# Menu text -> how many times faster than a normal sprint. 1x is the game's
# own sprint speed, i.e. no change.
MULTIPLIERS: dict[str, float] = {
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


def _multiplier_for(choice: str) -> float:
    # Falls back to the default if a saved setting no longer matches a choice.
    return MULTIPLIERS.get(choice, MULTIPLIERS[DEFAULT_CHOICE])


def _on_multiplier_changed(_option: SpinnerOption, new_value: str) -> None:
    # Apply straight away so the new speed is felt on the next sprint.
    sprint.apply(_multiplier_for(new_value))


speed_multiplier = SpinnerOption(
    "Sprint Speed",
    DEFAULT_CHOICE,
    list(MULTIPLIERS),
    description=(
        "How much faster than normal you sprint. 1x leaves sprinting at the"
        " game's normal speed. Walking speed is never changed. Takes effect the"
        " next time you sprint."
    ),
    on_change_while_enabled=_on_multiplier_changed,
)


def on_enable() -> None:
    sprint.apply(_multiplier_for(speed_multiplier.value))


def on_disable() -> None:
    sprint.restore()


mod = build_mod()
