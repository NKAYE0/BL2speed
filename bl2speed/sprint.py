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


def _find_sprint_definition():
    """Find the sprint definition object, or return None if it isn't there."""
    sprint_def = _sdk.find_object(SPRINT_CLASS, SPRINT_PATH)
    if sprint_def is None:
        _sdk.log_warning(
            "{0} Could not find {1} '{2}'. Sprint speed left unchanged.".format(
                LOG_PREFIX, SPRINT_CLASS, SPRINT_PATH,
            ),
        )
    return sprint_def


def _find_sprint_effect(sprint_def):
    """Return (effects_array, sprint_speed_effect), or None if unavailable."""
    effects = getattr(sprint_def, "AttributeEffects", None)
    if effects is None or len(effects) == 0:
        _sdk.log_warning(
            "{0} The sprint definition has no attribute effects."
            " Sprint speed left unchanged.".format(LOG_PREFIX),
        )
        return None
    return effects, effects[0]


def _capture_stock_values(effect) -> None:
    """Record the game's own values once, so we can restore and calibrate."""
    global _stock_scale, _is_scale_modifier

    if _stock_scale is not None:
        return

    _stock_scale = float(effect.BaseModifierValue.BaseValueScaleConstant)

    modifier_type = getattr(effect, "ModifierType", None)
    _is_scale_modifier, reason = _sdk.is_scale_modifier(modifier_type)

    _sdk.log_info(
        "{0} Read stock sprint values:"
        " BaseValueConstant={1}"
        " BaseValueScaleConstant={2}"
        " ModifierType={3} (multiplies={4}, from {5})".format(
            LOG_PREFIX,
            float(effect.BaseModifierValue.BaseValueConstant),
            _stock_scale,
            modifier_type,
            _is_scale_modifier,
            reason,
        ),
    )


def _scale_for_multiplier(effect, multiplier: float) -> float:
    """Work out the BaseValueScaleConstant needed for the chosen multiplier."""
    base_value = float(effect.BaseModifierValue.BaseValueConstant)
    stock_bonus = base_value * (_stock_scale or 0.0)

    # If the bonus is pulled from another attribute or an initialisation
    # definition, the constant above isn't the whole story and the maths below
    # would be wrong.
    modifier_value = effect.BaseModifierValue
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
        "{0} Sprint effect isn't a plain multiplier (ModifierType={1},"
        " BaseValueConstant={2}, other source={3})."
        " Scaling the sprint bonus by {4} instead of the final speed.".format(
            LOG_PREFIX,
            getattr(effect, "ModifierType", None),
            base_value,
            uses_other_source,
            multiplier,
        ),
    )
    return (_stock_scale or 1.0) * multiplier


def _write_scale(effects, effect, new_scale: float) -> bool:
    """Write the new scale constant back, then check that it actually landed."""
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
            "{0} Tried to set the sprint scale to {1} but the game still"
            " reads {2}. Sprint speed may be unchanged.".format(
                LOG_PREFIX, new_scale, written,
            ),
        )
        return False
    return True


def apply(multiplier: float) -> bool:
    """Set sprint speed to `multiplier` times the game's normal sprint speed.

    Returns True if the change was made, False if the game object couldn't be
    read or the write didn't take.
    """
    sprint_def = _find_sprint_definition()
    if sprint_def is None:
        return False

    found = _find_sprint_effect(sprint_def)
    if found is None:
        return False
    effects, effect = found

    _capture_stock_values(effect)

    new_scale = _scale_for_multiplier(effect, multiplier)
    if not _write_scale(effects, effect, new_scale):
        return False

    _sdk.log_info(
        "{0} Sprint speed set to {1}x (scale constant {2}).".format(
            LOG_PREFIX, multiplier, new_scale,
        ),
    )
    return True


def restore() -> bool:
    """Put the game's own sprint speed back. Safe to call at any time."""
    if _stock_scale is None:
        # We never changed anything, so there is nothing to undo.
        return True

    sprint_def = _find_sprint_definition()
    if sprint_def is None:
        return False

    found = _find_sprint_effect(sprint_def)
    if found is None:
        return False
    effects, effect = found

    if not _write_scale(effects, effect, _stock_scale):
        return False

    _sdk.log_info("{0} Sprint speed restored to normal.".format(LOG_PREFIX))
    return True
