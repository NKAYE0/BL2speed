# Mod entry point. This is what the mod manager loads.
#
# Works with both Borderlands SDKs. It checks which one is running and hands
# off to the matching front end; the actual sprint logic is shared.
#
#   new SDK: put this folder in  <game>/sdk_mods/
#   old SDK: put this folder in  <game>/Binaries/Win32/Mods/

from . import _sdk

if _sdk.IS_NEW_SDK:
    from ._modern import register
else:
    from ._legacy import register

mod = register()
