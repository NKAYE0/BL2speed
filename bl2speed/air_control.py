# Talks to the player pawn to change air control.
#
# Air control is how much you can steer while in the air. In Unreal Engine 3
# it's the AirControl float on the pawn itself: 0 means no steering at all
# once you leave the ground, higher values let you change direction mid-jump.
#
# Unlike sprint, this lives on the live pawn rather than a shared definition,
# so it has to be re-applied whenever the player gets a new pawn (level load,
# respawn). The stock value is read from the first untouched pawn we see and
# used both to work out multipliers and to put things back on disable.

import unrealsdk
from mods_base import get_pc

PLAYER_PAWN_CLASS = "WillowPlayerPawn"

LOG_PREFIX = "[Speed]"

# Stock value, captured the first time we read a pawn. None until then, which
# also means "nothing to restore".
_stock_air_control: float | None = None


def _is_player_pawn(obj) -> bool:
    """True if obj is an on-foot player pawn (not a vehicle, not None)."""
    if obj is None:
        return False
    cls = obj.Class
    while cls is not None:
        if cls.Name == PLAYER_PAWN_CLASS:
            return True
        cls = cls.SuperField
    return False


def _local_player_pawn():
    """Return the local player's on-foot pawn, or None if there isn't one."""
    pc = get_pc()
    if pc is None:
        return None
    pawn = pc.Pawn
    return pawn if _is_player_pawn(pawn) else None


def apply_to_pawn(pawn, multiplier: float) -> bool:
    """Set `pawn`'s air control to `multiplier` times the game's normal value."""
    global _stock_air_control

    if not _is_player_pawn(pawn):
        return False

    if _stock_air_control is None:
        _stock_air_control = float(pawn.AirControl)
        unrealsdk.logging.info(
            f"{LOG_PREFIX} Read stock air control: {_stock_air_control}",
        )

    new_value = _stock_air_control * multiplier
    pawn.AirControl = new_value
    unrealsdk.logging.info(
        f"{LOG_PREFIX} Air control set to {multiplier}x ({new_value}).",
    )
    return True


def apply(multiplier: float) -> bool:
    """Apply to the local player's current pawn, if they have one right now.

    Returns False when there's no pawn (e.g. at the main menu); the spawn hook
    will apply it once one exists.
    """
    return apply_to_pawn(_local_player_pawn(), multiplier)


def restore() -> bool:
    """Put the game's own air control back. Safe to call at any time."""
    if _stock_air_control is None:
        # We never changed anything, so there is nothing to undo.
        return True

    pawn = _local_player_pawn()
    if pawn is None:
        # No pawn to fix; the next one spawns with the stock value anyway.
        return True

    pawn.AirControl = _stock_air_control
    unrealsdk.logging.info(f"{LOG_PREFIX} Air control restored to normal.")
    return True
