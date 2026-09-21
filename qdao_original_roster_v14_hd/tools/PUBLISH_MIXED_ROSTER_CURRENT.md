# Mixed Original04–06 publication (2026-09-21)

The current publisher supports new same-ID04/05/06 packages and sequential
releases. Default execution is read-only; existing targets are never replaced.
Artwork, visual approval and actual Unity evidence must already exist. Success
means `published_pending_formal_editor_import`, not formal gameplay acceptance.

## Paths and historical protection

Paths derive from this checkout. Formal project:
`D:/luyuan/wuxingqitan/mmorpg-client`. Isolated default:
`D:/luyuan/wuxingqitan/tmp/qdao-original-live-candidate-20260921`.
`QDAO_ISOLATED_PROJECT` may select another independent project under workspace
`tmp`; stage, publisher and walking checker share that setting.

Historical evidence remains unchanged. The retained formal baseline SHA stays
`8238ab4d32a2c4782f2b853339257cd3054b5e9b8c9c796351d78b42b823377f`.
Only that SHA-pinned baseline accepts the old `E:/work/mmorpg-client` label.
New runs must bind actual current paths. Generate a new local preparation;
old absolute-path preparations do not silently become current source snapshots.

Every historical character file, including old `.meta`, must still match.
Unity importer reserialization does not waive that gate. Retain and investigate
the exact differences; do not replace the pinned baseline to make a run pass.

## Required sequence

1. Complete and independently reconstruct a new immutable assembly:128 walk,
   8idle, portrait; native1024 additions and exact preserved512 frames. Inspect
   directions, edges, transitions and seams; seal a fresh visual approval.
2. Stage140 authored files. Let isolated Unity import and build its index, then
   close the Editor. Capture fresh full Edit/Play/post snapshots and run actual
   full suites. All source/meta/camera/input/launch/XML/log bindings must pass.
3. Observe V13 originals00–03 and **every** prior/current mixed character in
   that new run. Each mixed actor passes its own manifest,136 action geometry,
   eight directions, cadence, real movement, idle and bounded residency gates.
4. For each manifest direction containing `source_kind: native-hd`, capture
   its lowest numbered native walk frame, in N/NE/E/SE/S/SW/W/NW order. At least
   two native directions are required. Current04 therefore usesSW02/NW02.
   The publisher calls `verify_mixed_walk_captures.check_frames` as a hard gate
   for all mixed actors:1024PNG SHA,104PPU,pivot,real Run-state movement and
   distinct simulation frames; normal/nearest views share each captured frame.
   Preserved512 idle screenshots cannot satisfy this requirement.
5. Actually inspect current normal/nearest PNGs and save exact SHA-bound reviews.
   Record nearest top clipping honestly. Speed9 and camera27/5 remain fixed.
6. Publisher dry-run/execute copies only140 authored files into a new target.
   Isolated GUIDs/metas/index are never copied. Let the formal Editor generate
   its own data, then close it and record the exact imported inventory using
   `record_mixed_formal_import.py`. This records local GUID/source/geometry/time
   bindings; it does not claim Unity tests or formal gameplay acceptance.

## Sequential publication

Pass `--previous-import-audit` once per prior publication in order. Each inventory
pins its publication receipt SHA, exact previous resources, and new imported
package. The publisher validates the ordered hash chain, whitelist, timestamps,
and every prior character in the fresh runtime regression. Missing audits or
any changed old PNG/JSON/meta/index fail closed.

Formal and isolated `.meta` and `runtime-index.asset` may differ across projects.
Both remain byte-for-byte protected by their own baseline/stage inventories.
Only these derived files are excluded from the cross-project authored comparison.

## Runtime review fields

Retain schema `qdao-original-v14-mixed/runtime-visual-review-v1`, actual reviewer
and UTC time,passed status,runtime/input/approval/stage SHA bindings, explicit
mixed geometry review and preserved-idle acknowledgement. Concrete notes need
at least12 characters.

`views`: both normalView/nearestView for **all mixed actors**, each with
`character_id`, `view`, `status`, `image_sha256`, `clipping_reviewed`, actual
boolean `full_frame_inside_capture`, `notes`.

`walk_views`: every native target and both views for every mixed actor. Same
fields plus `direction`, `frame_number`, `resource_sha256`, `simulation_frame`.
All must match actual bound observations. No tool creates a passed review.
Saved JSON assertions are local bindings, not signed attestations.

## Commands

From V14 root, substitute actual run names:

```powershell
$python = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$run = 'D:/luyuan/wuxingqitan/image/qdao_original_roster_v13/runtime-validation/ACTUAL_NEW_RUN'
& $python -X utf8 -B tools/verify_mixed_walk_captures.py --run $run --character 04_mountain_guardian_boy
& $python -X utf8 -B tools/publish_mixed_roster.py `
  --approved mixed-approved/APPROVED_RUN/04_mountain_guardian_boy `
  --project D:/luyuan/wuxingqitan/mmorpg-client --run $run `
  --stage-audit mixed-stage-audits/STAGE_RUN.json `
  --runtime-visual-review "$run/runtime-visual-review.json" `
  --audit mixed-publication-audits/NEW_PUBLICATION.json
```

Add `--execute` for the intended concrete package. After formal import/closure:

```powershell
& $python -X utf8 -B tools/record_mixed_formal_import.py `
  --publication-audit mixed-publication-audits/NEW_PUBLICATION.json `
  --output mixed-publication-audits/NEW_FORMAL_IMPORT.json --execute
```

For05 include04's import audit; for06 include04/05's audits in order.
No complete04–06 or actual new native runtime captures existed at this handoff;
placeholder commands are not evidence of publication.

Regression suites include `test_publish_mixed_baselines`,
`test_publish_mixed_sequence`, `test_publish_mixed_roster`,
`test_verify_mixed_walk_captures` and shared
`test_publish_original_roster_v14_gates`, plus existing assembly/approval/stage.
Temporary synthetic fixtures never become Resources, approvals or Unity evidence.
