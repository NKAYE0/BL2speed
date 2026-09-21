# Speed

A Borderlands 2 mod that makes sprinting faster. Normal walking speed is left
alone — only sprinting changes.

One setting, in the mod's options menu:

**Sprint Speed** — `1x`, `1.25x`, `1.5x`, `1.75x`, `2x`, `2.5x`, `3x`, `5x`,
`10x`

The number is how fast you sprint compared to a normal sprint, so `2x` means
you cover ground twice as quickly as vanilla sprinting does. `1x` is the game's
own speed, so you can leave the mod enabled with no effect.

Built for the modern
[willow2-mod-manager](https://bl-sdk.github.io/willow2-mod-db/) (`mods_base`).

## Installing

1. Install [willow2-mod-manager](https://bl-sdk.github.io/willow2-mod-db/) for
   Borderlands 2.
2. Drop `bl2speed.sdkmod` into the `sdk_mods` folder in your game directory,
   e.g. `steamapps/common/Borderlands 2/sdk_mods/`.
3. Launch the game and enable **Speed** in the mods menu.
4. Pick a speed under its options. The default is `1.5x`.

## How it works

Sprinting in BL2 comes from one shared game object:

```
SprintDefinition  GD_PlayerShared.Sprint.SprintDefinition_Default
```

Its first attribute effect is the speed bonus applied while the sprint key is
held. The mod changes only that effect's `BaseValueScaleConstant` — how large
the bonus is — and records the game's own value first so it can be put back
exactly when the mod is disabled.

To turn "2x" into the right scale constant, the mod reads the game's stock
values at runtime rather than hardcoding numbers, then solves for the bonus
that produces the requested final speed. In a stock game the sprint bonus is
`0.35` applied as `MT_Scale`, so a normal sprint is 1.35x walking speed and
"2x" works out to a scale constant of 4.857 — but none of those numbers are
hardcoded, and the mod confirms `MT_Scale` against the game's own enum table
rather than assuming. Everything it reads is written to the SDK log on enable,
so a bad calculation is visible rather than silent.

Because it edits one definition object and nothing else, the mod does not hook
any functions, does not run per-frame code, and has no effect on enemies,
vehicles or NPCs.

## Project layout

```
bl2speed/                  # the mod package (this folder = the release contents)
    __init__.py             # entry point: detects the SDK, hands off
    _sdk.py                  # thin layer over the two SDKs' differing APIs
    _config.py                # the speed choices and mod details, defined once
    sprint.py                  # reads and edits the sprint definition
    _modern.py                  # front end for mods_base
    _legacy.py                   # front end for ModMenu
    pyproject.toml                # mod metadata (read by the SDK mod database)
package.py                          # builds the release file
```

The SDK-specific parts are confined to `_sdk.py`, `_modern.py` and
`_legacy.py`. The sprint logic in `sprint.py` is shared and knows nothing
about which SDK it's running under.

### Legacy SDK support

There is a complete front end for the legacy PythonSDK 0.7.x (`ModMenu`) in
`_legacy.py`, and `__init__.py` picks between the two automatically. It is
**not advertised as supported**, because it has never been run on a real
legacy install — only written against the `ModMenu` API and checked for
syntax. `python package.py --legacy` builds the matching `bl2speed.zip` for
whenever someone gets round to testing it.

## Things worth knowing

- **Co-op:** the mod is client-side — it changes your own game only, and other
  players don't need it. Very high multipliers can make the host's copy of you
  lag behind or snap back, since the game wasn't built for that speed.
- **Cliffs:** at `3x` and above you will overshoot ledges and jumps that you
  are used to. This mod deliberately doesn't touch air control, so momentum
  behaves exactly as vanilla once you leave the ground.
- **Achievements and saves:** nothing is written to your save; disabling the
  mod returns sprinting to normal immediately.

## Releasing

Build the release files:

```
python package.py
```

That produces `dist/bl2speed.sdkmod`, ready to attach to a GitHub release and
to upload to Nexus Mods. The script refuses to build if the version in
`_config.py` and the version in `pyproject.toml` have drifted apart.

To also list it on the SDK mod database, add a markdown file to the
`_willow2_mods` folder of
[bl-sdk.github.io](https://github.com/bl-sdk/bl-sdk.github.io) pointing at this
repo's `pyproject.toml` raw URL — the site reads the name, version, author and
license from it automatically.

## License

GPL-3.0 — see [LICENSE](LICENSE).
