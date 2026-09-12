# Front end for the old SDK (PythonSDK 0.7.x / ModMenu 2.x).
#
# Only imported when the old SDK is the one running - see __init__.py.
# Same behaviour as the new-SDK front end, expressed in the old API.

from Mods import ModMenu

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


class SpeedMod(ModMenu.SDKMod):
    Name = NAME
    Author = AUTHOR
    Description = DESCRIPTION
    Version = VERSION
    Types = ModMenu.ModTypes.Utility
    SaveEnabledState = ModMenu.EnabledSaveType.LoadWithSettings

    def __init__(self) -> None:
        super().__init__()

        self.SpeedSpinner = ModMenu.Options.Spinner(
            Caption=OPTION_NAME,
            Description=OPTION_DESCRIPTION,
            StartingValue=DEFAULT_CHOICE,
            Choices=list(MULTIPLIERS),
        )
        self.Options = [self.SpeedSpinner]

    def Enable(self) -> None:
        super().Enable()
        sprint.apply(multiplier_for(self.SpeedSpinner.CurrentValue))

    def Disable(self) -> None:
        sprint.restore()
        super().Disable()

    def ModOptionChanged(self, option, new_value) -> None:
        # Apply straight away, but only while the mod is actually on.
        if option is self.SpeedSpinner and self.IsEnabled:
            sprint.apply(multiplier_for(new_value))


def register() -> object:
    """Create the mod instance and register it with the old mod menu."""
    instance = SpeedMod()
    ModMenu.RegisterMod(instance)
    return instance
