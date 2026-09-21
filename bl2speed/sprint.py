# Talks to the game object that controls sprint speed.
#
# BL2 implements sprinting with a single shared object:
#   SprintDefinition  GD_PlayerShared.Sprint.SprintDefinition_Default
# Its first attribute effect is the thing that makes you move faster while
# the sprint key is held. We only ever change that effect's
# BaseValueScaleConstant (how big the bonus is), and we remember the stock
# value so it can be put back exactly when the mod is turned off.
#
# Works on both SDKs - everything game-facing goes through _sdk.

from __future__ import annotations

import math

from . import _sdk

SPRINT_CLASS = "SprintDefinition"
SPRINT_PATH = "GD_PlayerShared.Sprint.SprintDefinition_Default"

LOG_PREFIX = "[Speed]"

# Stock values, captured the first time we successfully read the object.
# _stock_scale is None until then, which also means "nothing to restore".
_stock_scale = None  # type: float | None

# True if the sprint effect multiplies movement speed (MT_Scale) rather than
# adding a flat amount. Only in the multiply case can we work out an exact
# final speed multiplier.
_is_scale_modifier = False


def _find_sprint_effects():
    """Return the sprint definition's attribute effects, or None if unavailable."""
    sprint_def = _sdk.find_object(SPRINT_CLASS, SPRINT_PATH)
    if sprint_def is None:
        _sdk.log_warning(
            f"{LOG_PREFIX} Could not find {SPRINT_CLASS} '{SPRINT_PATH}'."
            f" Sprint speed left unchanged.",
        )
        return None

    effects = getattr(sprint_def, "AttributeEffects", None)
    if effects is None or len(effects) == 0:
        _sdk.log_warning(
            f"{LOG_PREFIX} The sprint definition has no attribute effects."
            f" Sprint speed left unchanged.",
        )
        return None
    return effects


def _capture_stock_values(effect) -> None:
    """Record the game's own values once, so we can restore and calibrate."""
    global _stock_scale, _is_scale_modifier

    if _stock_scale is not None:
        return

    _stock_scale = float(effect.BaseModifierValue.BaseValueScaleConstant)

    modifier_type = getattr(effect, "ModifierType", None)
    _is_scale_modifier, reason = _sdk.is_scale_modifier(modifier_type)

    _sdk.log_info(
        f"{LOG_PREFIX} Read stock sprint values:"
        f" BaseValueConstant={float(effect.BaseModifierValue.BaseValueConstant)}"
        f" BaseValueScaleConstant={_stock_scale}"
        f" ModifierType={modifier_type}"
        f" (multiplies={_is_scale_modifier}, from {reason})",
    )


def _scale_for_multiplier(effect, multiplier: float) -> float:
    """Work out the BaseValueScaleConstant needed for the chosen multiplier.

    Only called after _capture_stock_values, so _stock_scale is set.
    """
    modifier_value = effect.BaseModifierValue
    base_value = float(modifier_value.BaseValueConstant)
    stock_bonus = base_value * _stock_scale

    # If the bonus is pulled from another attribute or an initialisation
    # definition, the constant above isn't the whole story and the maths below
    # would be wrong.
    uses_other_source = (
        getattr(modifier_value, "BaseValueAttribute", None) is not None
        or getattr(modifier_value, "InitializationDefinition", None) is not None
    )

    if _is_scale_modifier and base_value != 0.0 and not uses_other_source:
        # Sprint speed = walk speed * (1 + bonus).
        # For a sprint `multiplier` times as fast as the stock sprint:
        #     1 + new_bonus = multiplier * (1 + stock_bonus)
        required_bonus = multiplier * (1.0 + stock_bonus) - 1.0
        return required_bonus / base_value

    # Fallback: we can't calculate the exact final speed, so scale the sprint
    # bonus itself instead. Still faster, but the chosen number won't be an
    # exact multiple of normal sprint speed.
    _sdk.log_warning(
        f"{LOG_PREFIX} Sprint effect isn't a plain multiplier"
        f" (BaseValueConstant={base_value}, other source={uses_other_source})."
        f" Scaling the sprint bonus by {multiplier} instead of the final speed.",
    )
    return _stock_scale * multiplier


def _write_scale(effects, new_scale: float) -> bool:
    """Write the new scale constant back, then check that it actually landed."""
    effect = effects[0]
    modifier_value = effect.BaseModifierValue
    modifier_value.BaseValueScaleConstant = new_scale

    # Depending on SDK version, reading a struct hands back either a live
    # reference or a copy, so assign each level back as well. Not every SDK
    # allows assigning into the array, hence the guard.
    try:
        effect.BaseModifierValue = modifier_value
        effects[0] = effect
    except (TypeError, AttributeError, ValueError):
        pass

    # The game stores this as a 32-bit float, so what reads back is never
    # exactly the 64-bit value Python sent. Compare with a tolerance well
    # inside float32's precision rather than demanding an exact match.
    written = float(effects[0].BaseModifierValue.BaseValueScaleConstant)
    if not math.isclose(written, new_scale, rel_tol=1e-5, abs_tol=1e-6):
        _sdk.log_warning(
            f"{LOG_PREFIX} Tried to set the sprint scale to {new_scale} but the"
            f" game still reads {written}. Sprint speed may be unchanged.",
        )
        return False
    return True


def apply(multiplier: float) -> bool:
    """Set sprint speed to `multiplier` times the game's normal sprint speed.

    Returns True if the change was made, False if the game object couldn't be
    read or the write didn't take.
    """
    effects = _find_sprint_effects()
    if effects is None:
        return False

    _capture_stock_values(effects[0])

    new_scale = _scale_for_multiplier(effects[0], multiplier)
    if not _write_scale(effects, new_scale):
        return False

    _sdk.log_info(
        f"{LOG_PREFIX} Sprint speed set to {multiplier}x (scale constant {new_scale}).",
    )
    return True


def restore() -> bool:
    """Put the game's own sprint speed back. Safe to call at any time."""
    if _stock_scale is None:
        # We never changed anything, so there is nothing to undo.
        return True

    effects = _find_sprint_effects()
    if effects is None:
        return False

    if not _write_scale(effects, _stock_scale):
        return False

    _sdk.log_info(f"{LOG_PREFIX} Sprint speed restored to normal.")
    return True
