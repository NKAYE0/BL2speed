# Speed

A Borderlands 2 mod that makes sprinting faster. Normal walking speed is left
alone — only sprinting changes.

One setting, in the mod's options menu:

**Sprint Speed** — `1.25x`, `1.5x`, `1.75x`, `2x`, `2.5x`, `3x`, `5x`, `10x`

The number is how fast you sprint compared to a normal sprint, so `2x` means
you cover ground twice as quickly as vanilla sprinting does.

Built on the [Borderlands SDK](https://bl-sdk.github.io/) (the modern
`willow2-mod-manager` / `mods_base` framework, not the legacy PythonSDK).

## Installing

1. Install [willow2-mod-manager](https://bl-sdk.github.io/willow2-mod-db/) for
   Borderlands 2.
2. Put `bl2speed.sdkmod` (or the `bl2speed` folder) into
   `Binaries/Win32/sdk_mods/`.
3. Launch the game and enable **Speed** in the mods menu.
4. Pick a speed under the mod's options.

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
that produces the requested final speed. Everything it reads is written to the
SDK console log on enable, so any miscalculation is visible rather than silent.

Because it edits one definition object and nothing else, the mod does not hook
any functions, does not run per-frame code, and has no effect on enemies,
vehicles or NPCs.

## Project layout

```
bl2speed/                  # the mod package (this folder = the .sdkmod contents)
    __init__.py             # entry point: the option, and enable/disable wiring
    pyproject.toml           # mod metadata (name, version, license, ...)
    sprint.py                 # reads and edits the sprint definition
package.py                     # builds dist/bl2speed.sdkmod
```

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

Build the release file:

```
python package.py
```

That produces `dist/bl2speed.sdkmod`, ready to attach to a GitHub release and
to upload to Nexus Mods.

To also list it on the SDK mod database, add a markdown file to the
`_willow2_mods` folder of
[bl-sdk.github.io](https://github.com/bl-sdk/bl-sdk.github.io) pointing at this
repo's `pyproject.toml` raw URL — the site reads the name, version, author and
license from it automatically.

## License

GPL-3.0 — see [LICENSE](LICENSE).
