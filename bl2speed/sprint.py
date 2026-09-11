# Talks to the game object that controls sprint speed.
#
# BL2 implements sprinting with a single shared object:
#   SprintDefinition  GD_PlayerShared.Sprint.SprintDefinition_Default
# Its first attribute effect is the thing that makes you move faster while
# the sprint key is held. We only ever change that effect's
# BaseValueScaleConstant (how big the bonus is), and we remember the stock
# value so it can be put back exactly when the mod is turned off.

from __future__ import annotations

import unrealsdk

SPRINT_CLASS = "SprintDefinition"
SPRINT_PATH = "GD_PlayerShared.Sprint.SprintDefinition_Default"

LOG_PREFIX = "[Speed]"

# Stock values, captured the first time we successfully read the object.
# _stock_scale is None until then, which also means "nothing to restore".
_stock_scale: float | None = None

# True if the sprint effect multiplies movement speed (MT_Scale) rather than
# adding a flat amount. Only in the multiply case can we work out an exact
# final speed multiplier.
_is_scale_modifier: bool = False


def _find_sprint_definition() -> object | None:
    """Find the sprint definition object, or return None if it isn't there."""
    try:
        sprint_def = unrealsdk.find_object(SPRINT_CLASS, SPRINT_PATH)
    except Exception:  # noqa: BLE001 - some SDK builds raise instead of returning None
        sprint_def = None

    if sprint_def is None:
        unrealsdk.logging.warning(
            f"{LOG_PREFIX} Could not find {SPRINT_CLASS} '{SPRINT_PATH}'."
            f" Sprint speed left unchanged.",
        )
    return sprint_def


def _find_sprint_effect(sprint_def: object) -> tuple[object, object] | None:
    """Return (effects_array, sprint_speed_effect), or None if unavailable."""
    effects = getattr(sprint_def, "AttributeEffects", None)
    if effects is None or len(effects) == 0:
        unrealsdk.logging.warning(
            f"{LOG_PREFIX} The sprint definition has no attribute effects."
            f" Sprint speed left unchanged.",
        )
        return None
    return effects, effects[0]


def _capture_stock_values(effect: object) -> None:
    """Record the game's own values once, so we can restore and calibrate."""
    global _stock_scale, _is_scale_modifier

    if _stock_scale is not None:
        return

    _stock_scale = float(effect.BaseModifierValue.BaseValueScaleConstant)

    modifier_type = getattr(effect, "ModifierType", None)
    _is_scale_modifier = modifier_type is not None and "MT_Scale" in str(modifier_type)

    unrealsdk.logging.info(
        f"{LOG_PREFIX} Read stock sprint values:"
        f" BaseValueConstant={float(effect.BaseModifierValue.BaseValueConstant)}"
        f" BaseValueScaleConstant={_stock_scale}"
        f" ModifierType={modifier_type}",
    )


def _scale_for_multiplier(effect: object, multiplier: float) -> float:
    """Work out the BaseValueScaleConstant needed for the chosen multiplier."""
    assert _stock_scale is not None

    base_value = float(effect.BaseModifierValue.BaseValueConstant)
    stock_bonus = base_value * _stock_scale

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
    unrealsdk.logging.warning(
        f"{LOG_PREFIX} Sprint effect isn't a plain multiplier"
        f" (ModifierType={getattr(effect, 'ModifierType', None)},"
        f" BaseValueConstant={base_value}, other source={uses_other_source})."
        f" Scaling the sprint bonus by {multiplier} instead of the final speed.",
    )
    return (_stock_scale or 1.0) * multiplier


def _write_scale(effects: object, effect: object, new_scale: float) -> None:
    """Write the new scale constant back, one level at a time.

    Reading a struct out of the game can hand back either a live reference or
    a copy depending on SDK version, so each level is assigned back explicitly
    to make sure the change actually lands.
    """
    modifier_value = effect.BaseModifierValue
    modifier_value.BaseValueScaleConstant = new_scale
    effect.BaseModifierValue = modifier_value
    effects[0] = effect


def apply(multiplier: float) -> bool:
    """Set sprint speed to `multiplier` times the game's normal sprint speed.

    Returns True if the change was made, False if the game object couldn't be
    read (in which case nothing was touched).
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
    _write_scale(effects, effect, new_scale)

    unrealsdk.logging.info(
        f"{LOG_PREFIX} Sprint speed set to {multiplier}x"
        f" (scale constant {new_scale}).",
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

    _write_scale(effects, effect, _stock_scale)
    unrealsdk.logging.info(f"{LOG_PREFIX} Sprint speed restored to normal.")
    return True
