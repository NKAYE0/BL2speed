# Mod entry point. This is what the mod manager loads.
#
# Holds the options and wires them to the sprint and air control logic. Everything else -
# name, version, author, description, coop support, supported games - comes
# from pyproject.toml, so it's only written down in one place.

from typing import Any

from mods_base import SpinnerOption, build_mod, hook
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from . import air_control, sprint

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


# Menu text -> how many times the game's normal air control. "Off" leaves
# air control completely untouched.
AIR_CONTROL_MULTIPLIERS: dict[str, float] = {
    "Off": 1.0,
    "1.5x": 1.5,
    "2x": 2.0,
    "3x": 3.0,
    "5x": 5.0,
    "10x": 10.0,
}

AIR_CONTROL_DEFAULT = "Off"


def _air_multiplier_for(choice: str) -> float:
    # Falls back to the default if a saved setting no longer matches a choice.
    return AIR_CONTROL_MULTIPLIERS.get(
        choice,
        AIR_CONTROL_MULTIPLIERS[AIR_CONTROL_DEFAULT],
    )


def _apply_air_control(choice: str) -> None:
    multiplier = _air_multiplier_for(choice)
    if multiplier == 1.0:
        # "Off" means hands off: put back the stock value if we changed it.
        air_control.restore()
    else:
        air_control.apply(multiplier)


def _on_air_control_changed(_option: SpinnerOption, new_value: str) -> None:
    _apply_air_control(new_value)


air_control_multiplier = SpinnerOption(
    "Air Control",
    AIR_CONTROL_DEFAULT,
    list(AIR_CONTROL_MULTIPLIERS),
    description=(
        "How much you can steer while in the air, compared to normal. Off"
        " leaves air control at the game's normal value. Takes effect"
        " immediately."
    ),
    on_change_while_enabled=_on_air_control_changed,
)


# Air control lives on the player's pawn, which is replaced on every level
# load and respawn, so re-apply it each time the player finishes spawning.
@hook("WillowGame.WillowPlayerController:SpawningProcessComplete", Type.POST)
def _on_player_spawned(
    obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    if not obj.IsLocalPlayerController():
        # In coop the host sees this for every player; only touch our own.
        return
    multiplier = _air_multiplier_for(air_control_multiplier.value)
    if multiplier != 1.0:
        air_control.apply_to_pawn(obj.Pawn, multiplier)


def on_enable() -> None:
    sprint.apply(_multiplier_for(speed_multiplier.value))
    _apply_air_control(air_control_multiplier.value)


def on_disable() -> None:
    sprint.restore()
    air_control.restore()


mod = build_mod()
