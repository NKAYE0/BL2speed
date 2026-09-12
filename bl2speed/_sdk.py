# Thin layer over the two Borderlands SDKs.
#
# The new SDK (willow2-mod-manager / mods_base) and the old one (PythonSDK
# 0.7.x) name the same functions differently. Everything else in this mod
# calls through here so it doesn't have to care which one is running.
#
#   new: unrealsdk.find_object(...)  raises ValueError when missing
#   old: unrealsdk.FindObject(...)   returns None when missing
#   new: unrealsdk.logging.info / .warning
#   old: unrealsdk.Log

from __future__ import annotations

import unrealsdk

# The new SDK is the one with snake_case functions. Checking for the function
# itself is more reliable than checking a version number.
IS_NEW_SDK = hasattr(unrealsdk, "find_object")


def find_object(class_name: str, object_path: str):
    """Find a game object by class and path, or return None if it isn't there."""
    if IS_NEW_SDK:
        try:
            return unrealsdk.find_object(class_name, object_path)
        except ValueError:
            # The new SDK raises rather than returning None.
            return None
    return unrealsdk.FindObject(class_name, object_path)


def log_info(message: str) -> None:
    """Write an ordinary message to the SDK log/console."""
    if IS_NEW_SDK:
        unrealsdk.logging.info(message)
    else:
        unrealsdk.Log(message)


def log_warning(message: str) -> None:
    """Write a warning to the SDK log/console."""
    if IS_NEW_SDK:
        unrealsdk.logging.warning(message)
    else:
        # The old SDK has no warning level, so mark it in the text instead.
        unrealsdk.Log("WARNING: " + message)


# --- Attribute modifier types ---------------------------------------------
#
# Both SDKs hand the ModifierType property back as a bare number, not a name,
# so it has to be turned back into something meaningful before it can be
# compared against MT_Scale.

MODIFIER_TYPE_ENUM = "EModifierType"
SCALE_MODIFIER_NAME = "MT_Scale"

# Standard ordering in the Willow games (MT_Scale, MT_PreAdd, MT_PostAdd),
# used only when the game's own enum table can't be read.
_ASSUMED_SCALE_VALUE = 0


def is_scale_modifier(value):
    """Is this EModifierType the multiply kind rather than the add kind?

    Returns (answer, how_we_decided) so the reason can be logged.
    """
    # Some SDK versions hand back a readable name, most hand back a number.
    text = str(value)
    if SCALE_MODIFIER_NAME in text:
        return True, "name '{0}'".format(text)
    if "MT_" in text:
        return False, "name '{0}'".format(text)

    try:
        number = int(value)
    except (TypeError, ValueError):
        return False, "unrecognised value '{0}'".format(text)

    # Ask the game what number MT_Scale actually is, rather than assuming.
    if IS_NEW_SDK and hasattr(unrealsdk, "find_enum"):
        try:
            scale_value = int(unrealsdk.find_enum(MODIFIER_TYPE_ENUM)[SCALE_MODIFIER_NAME])
            return (
                number == scale_value,
                "game enum ({0} == {1})".format(SCALE_MODIFIER_NAME, scale_value),
            )
        except (ValueError, KeyError, TypeError):
            pass

    return number == _ASSUMED_SCALE_VALUE, "assumed standard enum ordering"
