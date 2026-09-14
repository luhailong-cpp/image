# E right-facing natural-walk sample

Use `walk-E-refined-raw.png` (4 columns x 2 rows, 627 px cells) and `preview-refined/`.

Eight distinct authored walk poses, 60 ms each. The old `preview/` is superseded because its half-cycle head height jumped 13 px. Refined output reduces that range to 6 px (79–85); head width is 141–143 px. One shared preserve scale and final scale 1.0, head axis x=256 and grounded y=471. No empty/edge/clamped frames.

All creative pixels are from built-in ImageGen. `sources.json` records 11 original generation files, prompts, hashes and rejected drafts. `build_refined.py` only keys magenta, splits, normalizes complete raw-cell pixel resolution, applies one common scale, aligns and exports. No duplicate or interpolated walk frames.

Agent has visually reviewed the 8-frame contact sheet. Root must still review cross-direction identity, body scale and idle consistency. This sample has not been published to the game and does not modify formal character 24.
