# Front end for the new SDK (willow2-mod-manager / mods_base).
#
# Only imported when the new SDK is the one running - see __init__.py.

from __future__ import annotations

import mods_base
from mods_base import SETTINGS_DIR, CoopSupport, SpinnerOption, build_mod

from . import sprint
from ._config import (
    AUTHOR,
    DEFAULT_CHOICE,
    DESCRIPTION,
    MULTIPLIERS,
    NAME,
    OPTION_DESCRIPTION,
    OPTION_NAME,
    VERSION,
    multiplier_for,
)

# The mod manager has to be new enough for the APIs used here.
assert mods_base.__version_info__ >= (1, 4), "Please update the SDK mod manager"


def _on_multiplier_changed(_option: SpinnerOption, new_value: str) -> None:
    # Apply straight away so the new speed is felt on the next sprint.
    sprint.apply(multiplier_for(new_value))


speed_multiplier = SpinnerOption(
    OPTION_NAME,
    DEFAULT_CHOICE,
    list(MULTIPLIERS),
    description=OPTION_DESCRIPTION,
    on_change_while_enabled=_on_multiplier_changed,
)


def on_enable() -> None:
    sprint.apply(multiplier_for(speed_multiplier.value))


def on_disable() -> None:
    sprint.restore()


def register() -> object:
    """Build and register the mod with mods_base.

    Everything is passed explicitly rather than letting build_mod discover it,
    because discovery reads the module that calls it - which is this file, not
    the package root. That includes the settings file: left to itself it would
    be named after this module, so it's pinned to the package name instead.
    """
    return build_mod(
        name=NAME,
        settings_file=SETTINGS_DIR / "bl2speed.json",
        author=AUTHOR,
        version=VERSION,
        description=DESCRIPTION,
        inject_version_from_pyproject=False,
        options=[speed_multiplier],
        on_enable=on_enable,
        on_disable=on_disable,
        # Untested in coop - single player only so far.
        coop_support=CoopSupport.Unknown,
    )
