# Independent mixed-resolution review preview

Use this tool after creating a new `mixed-candidates/run/character` assembly. It reads the selected assembly only, does not edit a PNG or source record, and does not create an approval.

```powershell
& 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe' -X utf8 -B 'E:/work/image/qdao_original_roster_v14_hd/tools/serve_mixed_preview.py' --assembly 'E:/work/image/qdao_original_roster_v14_hd/mixed-candidates/ACTUAL_RUN/04_mountain_guardian_boy' --port 8876
```

Open `http://127.0.0.1:8876/`. With no `--assembly`, the page explains the missing selection rather than showing fixture assets. The server is loopback-only, rejects linked paths, exposes only declared action/portrait PNG routes, and sends no-cache headers. It never writes to the assembly. Do not expose this local review server on another interface.

The page begins paused, respects deliberate user playback, and offers all eight directions, 16 actual frames at 30 ms (480 ms loop), independent idle, slow playback, exact stepping, normal/large views, 01/05/09/13 contacts and 15/16/01 seam panels. Space toggles playback; left/right keys step. Missing or changed PNGs remain visibly absent.

All real PNGs draw into the same 1024-square canvas. A preserved 512 frame at 52 PPU and a native 1024 frame at 104 PPU therefore occupy equal world geometry. The preview labels actual source dimensions and PPU; displaying a 512 PNG larger does not improve its resolution or alter its bytes. The old all-HD preview remains unchanged.

On refresh the server hashes all present runtime files and five current review-input documents. It checks exact PNG slots, dimensions, SHA and basic mixed geometry. The browser also hashes each fetched image's bytes before decoding and showing it, preventing a silently stale image from being displayed after a server snapshot. The source panel shows raw/receipt/model records as saved; it does not certify model identity. This preview's checks are not independent source reconstruction.

“导出待审查输入” downloads a JSON draft bound to current file hashes. Its status is **pending**, reviewer/time are blank, every review flag is false, evidence is empty, and no direction is pre-approved. Recheck files immediately before beginning a new review. Fill actual observations, evidence PNG hashes, reviewer and a fresh review timestamp only after completing the visual inspection required by `APPROVE_STAGE_MIXED_ROSTER.md`.

Screenshot evidence must show the exact loaded frames. Normal and large comparison, all directions, transitions, native pixels, and 1920×1080 closeup evidence remain actual reviewer responsibilities. Browser preview evidence does not replace real Unity gameplay captures.

Design: jade `#175d57`, ivory paper `#f6f1e5`, ink `#18333c`, stage blue `#dce8ea`, brass focus `#906721`; Chinese serif title and Microsoft YaHei UI controls. A direction compass, two equal-world-size stages and an explicit frame timeline serve the artwork. No decorative animation or automatic playback is added. The project UI specification's ivory/jade palette takes precedence over the design search's generic marketing-page suggestion; a focused accessibility search supported manual playback, keyboard controls and reduced-motion behavior.

Verified 2026-09-19 in actual headless Edge at 1920×1080, 375×812 and 812×375. The temporary QA fixture contained three byte-identical copies of actual existing 04 images (512 walk, 1024 walk, 512 idle), with all other slots explicitly missing. Browser and server reports plus screenshots are under `mixed-preparation/recovery-20260919/`. They are preview QA only, not artwork review or acceptance. The fixture and QA server were removed/stopped after the run.
