# Preserved 512 / new native 1024 preparation

The only mixed characters are Original 04, 05 and 06. Their current 196 action
PNGs and three original portraits stay byte-identical. No old generation model
is relabelled. Original 00–03 remain sealed; 07–22 use the existing all-HD V14
contract once the required model is actually confirmed.

`prepare_mixed_roster.py` is metadata-only. It reads existing files and, with
`--execute`, writes a **new** directory beneath `mixed-preparation`. It never
writes a candidate, `manifest.json`, approval, Unity resource or source record.
Its `passed_snapshot_integrity` result means that the captured bytes still
match. It does not mean source reconstruction, visual review or publication
has passed. Historical prompt/receipt SHA conflicts are retained with both
recorded and actual hashes, and block acceptance; even an explainable newline
change must not silently replace the original source record.

## Runtime schema agreed with the client

Keep version 14 and the `QdaoOriginalRosterV14` resource family. Mixed manifests
explicitly set `resolution_mode: "mixed-preserved-v1"`; activation uses
`resolutionMode` with the same value. Unmarked V14 remains strictly all-1024.
Top-level `frame_size: [1024,1024]` and 104 PPU describe the maximum; an approved
mixed package resolves geometry from each of exactly 137 manifest file rows.

| File kind | source_kind | width / height | pixels_per_unit | root_px |
| --- | --- | --- | --- | --- |
| Preserved action | `preserved-v13` | 512 / 512 | 52 | [256,471] |
| New action | `native-hd` | 1024 / 1024 | 104 | [512,942] |
| Original portrait | `original-portrait` | 1024 / 1024 | Not used | Not used |

Every row has `path`, `sha256`, `source_kind` and `source_sha256`. Actions also
have `pixels_per_unit`, `pivot: [0.5,0.08]`, `root_px` and actual
`native_cell_size`. New native cells must be at least 1024 on both axes. Old
rows retain their actual smaller source dimensions and require
`preserved_sha256 == sha256`. The manifest's `preserved_snapshot_sha256` binds
the exact canonical `preserved-output-snapshot.json` bytes. That snapshot
contains all 199 existing runtime PNG rows, each with its original character
ID; its schema is `qdao-original-v14/preserved-output-snapshot-v1`. A client
hash field is a consistency check, not independent approval of this snapshot.

Both action classes have world-frame height `512/52 == 1024/104`, the same
pivot, alignment v2, fixed character scale (.84 for 04/05 and .88 for 06),
16 frames × 30 ms, 480 ms cycles, dedicated idle and move speed 9. This is
preservation compatibility; it does not claim old 512 art has native HD detail.

## Commands

```powershell
python -X utf8 -B tools/prepare_mixed_roster.py prepare --output mixed-preparation/NEW_RUN
python -X utf8 -B tools/prepare_mixed_roster.py prepare --output mixed-preparation/NEW_RUN --execute
python -X utf8 -B tools/prepare_mixed_roster.py check --directory mixed-preparation/NEW_RUN
python -X utf8 -B tools/prepare_mixed_roster.py check --directory mixed-preparation/NEW_RUN --require-complete
```

The last command must reject a preparation. It is an intentional guard against
treating a complete list of **slots** as a complete set of real actions.
Use paths relative to the V14 package directory, or absolute paths.

Saved files:

- `preparation.json`: every one of the 137 slots for each mixed character,
  preserved source records without rewrites, future native requirements and
  exact unresolved evidence conflicts.
- `preserved-output-snapshot.json`: runtime image hashes and per-file geometry.
- `legacy-evidence-snapshot.json`: every file in the three old candidate trees,
  original identity and baseline references, with file inventories and hashes.
- `missing-actions.json`: exact missing action paths for all remaining 19 IDs.

The tool has no merge/import/approval/publication command. A future assembler
must bind a reconciled provenance audit, unchanged preserved snapshot, and
per-new-cell raw/prompt/real built-in receipt plus actual model evidence. A
requested model, tool prompt or copied 2.5 string is insufficient. A 2.0 C2PA
creation record cannot qualify. Do not invent a generic `confirmed: true`
switch in place of an actual evidence verifier.

Before release, independently reconstruct each real source cell using its own
recorded resolution and fixed common scale; reject reuse, edge clipping and
upscaling. Review normal/enlarged motion, key contacts and loop seams plus
native detail and actual 1080p closeups. Seal all eight directions against
current manifest/QC/137 PNG hashes. A new real Unity Edit/Play run must bind
the mixed source and test code, exact asset inventory, launch/completion/logs,
normal and nearest screenshots, honest clipping observations, full post-run
input comparison and unchanged old-resource audit. Existing V13/V14 publishers
are not a mixed publication route and must not be weakened to accept these
preparations.
