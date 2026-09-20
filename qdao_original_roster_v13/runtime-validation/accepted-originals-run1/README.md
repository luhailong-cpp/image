# Accepted Original 00 + 02 — actual Unity run

This run tested the frozen `00_reference_topright_boy` and `02_fire_talisman_boy` candidates in the existing isolated project `E:/work/tmp/qdao-original-live-candidate-20260917`. The project was not rebuilt or replaced. No other Original candidate was staged.

- EditMode: **329/329 passed**, 0 failed/skipped, 2026-09-17 13:50:10–13:51:32 UTC (`editmode.xml`).
- PlayMode: **21/21 passed**, 0 failed/skipped, 2026-09-17 14:19:00–14:19:19 UTC (`playmode.xml`).
- Actual schema 2 report: `city-captures/runtime-observed-appearances.json`; `testedOriginalCount=2`, `selectedAppearanceCount=10`, completed behavior assertions.
- Both Originals actually loaded version 13, 8 directions × 16 unique frame textures, 512px separate sprites, 30ms/frame, cycle 480.00003ms. Actual manifest and activation bytes match the reviewed candidates.
- Both completed a real northward CharacterController route: 4.800003 world units, 16 sampled poses, move speed 9. They stopped on dedicated idle within 2 stationary frames. The separate animator test exercised all eight directions; this is not a claim of eight real navigation routes.
- The actual V12 speed baseline has the same controller SHA, speed 9 and 480.00003ms / 4.32000017-unit cycle. The 16-frame distance cadence doubles as required, preserving travel speed and cycle distance.
- Actual missing-resource tests passed: all 137 Original frame/idle/portrait omissions prevent activation without substituting another identity; legacy Lu V13 disappearance tests retain a complete same-identity V12/V11 fallback.

The complete Edit input has 25,028 files. Unity generated 319 new Original `.meta` files, and no existing input changed, before the separate Play snapshot. `input-playmode.json` has 25,347 files with SHA `302a87555ea02e4f7e29d1328adfa0541450984e42bff54c53848c681ee3f276`. The observer and launch records bind this exact snapshot. `post-playmode.json` independently hashes all 25,347 files: **0 added, 0 removed, 0 changed**; no shared writable links. The original capture script and later strengthened capture script are archived separately; the initial capture was supplemented by `editmode-hardlink-audit.json`.

The two full city PNGs were actually viewed. They show the expected character identity/name, clean transparent edges and ground placement. Screenshots are captured before each motor route; their facing need not match the final stopped-idle observation. This run covers the real **offline Tianyong sandbox** and actual motor, not online login.

`runtime-result-review.json` records the inspected values and PNG SHAs. The raw observations, snapshots, logs and XML are retained without editing. Historical empty-Original runs were not used for candidate acceptance.

Formal publication **completed** to `E:/work/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV13` for exactly 00 and 02. `publish-dry-run.json` first returned ready; `publish-execute.json` then completed both targets. `formal-publication-audit.json` independently confirms **296 exact tested resource files** and **2,222 existing character files unchanged** (0 added/removed/changed outside the new family). This is publication of the tested bytes into the formal project; the real Unity run described above occurred in the isolated project.
