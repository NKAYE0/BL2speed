---
pyproject_url: https://raw.githubusercontent.com/NKAYE0/BL2speed/main/bl2speed/pyproject.toml
---

Makes sprinting faster, leaving normal walking speed untouched.

Adds a **Sprint Speed** option with choices from `1x` up to `10x`. The number
is how fast you sprint compared to a normal sprint, so `2x` means you cover
ground twice as quickly as vanilla sprinting does. `1x` is the game's own
speed, so the mod can be left enabled with no effect. The default is `1.5x`.

Also adds an **Air Control** option, from `Off` up to `10x` the game's normal
air control, so you can steer more while jumping or falling. It's `Off` by
default, which leaves air control exactly as vanilla.

The multipliers are true multiples of vanilla sprint speed rather than raw
internal values — the mod reads the game's own sprint definition at runtime and
solves for the value that produces the requested speed, so `2x` really is twice
as fast.

### Notes

- Walking, crouching and vehicle speeds are unchanged. Only sprinting (and air
  control, if turned on) is affected, and disabling the mod restores the
  game's own values exactly.
- **Coop is untested.** The mod only edits your own game's sprint definition
  and touches no networking code, so it shouldn't affect anyone else — but BL2
  corrects player movement against the host, and I haven't tested whether a
  faster sprint gets corrected. Expect the possibility of rubber-banding,
  especially at high multipliers. Reports welcome.
- With **Air Control** left `Off`, momentum behaves exactly as vanilla once you
  leave the ground, so at `3x` sprint and above you will overshoot ledges and
  jumps you're used to. Turning Air Control up helps you correct mid-air.
- Air control is only changed on your own character, never other players'.
