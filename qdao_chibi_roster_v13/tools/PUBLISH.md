# V13 explicit staging and publication

`publish.py` is prepared but has not staged or published anything. It cannot pass while the 64 generated transition frames are missing. Every invocation requires an explicit Unity project under `E:/work`; there is no default destination. Without `--execute`, it only validates and reports a plan.

Before either mode:

1. Finish the 145 PNG delivery set and complete a fresh visual review. Seal it with `approve.py` as described below; this fixes manifest/QC to `passed`, binds the visual record to those final hashes, and writes independently verified validation. Do not re-run `assemble` afterward without a new review.
2. Keep `manifest.json`, `qc.json`, and `validation.json` unchanged throughout staging, runtime tests and publication. The tool independently re-verifies the candidate without rewriting validation, compares its full semantic result with the saved validation, and hashes all three actual files. `candidateRevision` is SHA-256 of their canonical compact JSON hash map.
3. `stage` is restricted to an existing isolated Unity project. It explicitly rejects `E:/work/mmorpg-client`. `publish` requires a passed runtime approval for the identical candidate, even when publishing to a nonformal project.

Read-only checks:

```powershell
python tools/publish.py --mode stage --client-project E:/work/tmp/qdao-v13-verify-20260917
python tools/publish.py --mode publish --client-project E:/work/mmorpg-client --runtime-approval runtime-validation/final-v13/runtime-approval.json
```

Add `--execute` only when the corresponding action is intended. Staging can happen before runtime tests; formal publication cannot.

The tool copies and hashes all 145 PNGs in the project's `Temp/QdaoV13Publish` directory first. It preserves existing V13 GUIDs, applies 8192 maximum size only to V13 strips, and uses current character texture metadata for new files. It then moves the previous V13 character directory into `publication/<transaction>/before/resources`, moves the complete staged directory into place, checks all PNG hashes again, and atomically writes `appearance.json` last. The activation declares V13 / 16 frames / 30 ms / independent idle / alignment v3 / contact 0 / passed visual review and the three true SHA values. No V12 path is written.

Before activation, missing V13 metadata keeps the client's V12 fallback available. On an exception during the swap, the tool preserves the failed candidate and restores the prior directory. It never recursively deletes either version. Each successful action leaves a receipt, complete prior file inventory and prior character-folder metadata in `publication/<transaction>`. To restore a successful publication later, preserve the current V13 directory first, then restore the receipt's `backup` directory and saved folder metadata; the backup includes the previous appearance activation. Do not copy only selected frames across versions.

## Runtime approval schema

The JSON below describes the future final evidence. It is a schema example, not proof of any completed run. Paths are absolute or relative to this approval JSON. Every evidence file is hashed. A staging receipt supplies `candidateRevision`, `sourceApprovals` and `appearanceSha256`.

```json
{
  "schema": "qdao-v13-runtime-approval/v1",
  "status": "passed",
  "characterId": "24_lu_dongbin",
  "version": 13,
  "candidateRevision": "COPY_FROM_STAGE_RECEIPT",
  "sourceApprovals": {
    "manifest_sha256": "ACTUAL_HASH",
    "qc_sha256": "ACTUAL_HASH",
    "validation_sha256": "ACTUAL_HASH"
  },
  "stagingReceipt": {"path": "../../publication/TRANSACTION/receipt.json", "sha256": "ACTUAL_HASH"},
  "inputSnapshot": {"path": "input-snapshot.json", "sha256": "ACTUAL_HASH"},
  "runtimeObservation": {"path": "runtime-observed-appearances.json", "sha256": "ACTUAL_HASH"},
  "baselineRuntimeObservation": {"path": "../baseline/runtime-observed-appearances.json", "sha256": "ACTUAL_HASH"},
  "baselineInputSnapshot": {"path": "../baseline/input-snapshot.json", "sha256": "ACTUAL_HASH"},
  "tests": [
    {"kind": "EditMode", "path": "editmode.xml", "sha256": "ACTUAL_HASH", "requiredV13TestNames": ["ACTUAL_FULL_TEST_NAME_CONTAINING_V13"]},
    {"kind": "PlayMode", "path": "playmode.xml", "sha256": "ACTUAL_HASH", "requiredV13TestNames": ["ACTUAL_FULL_TEST_NAME_CONTAINING_V13"]}
  ]
}
```

`input-snapshot.json` uses the root task's existing snapshot schema: `source`, `project`, `created_utc`, `files: [{path, sha256, bytes}]`, `count`. Capture it **after staging** and **before both test runs**. Its inventory must contain all 145 exact `Assets/Resources/World/Characters/QdaoRosterV13/24_lu_dongbin/...` PNGs plus the precise `appearance.json` SHA from the staging receipt. The saved tested project's files are checked again. The current run1 snapshot, which contains only V12 resources, cannot satisfy this gate.

The runtime observation is the unmodified `runtime-observed-appearances.json` emitted by `QdaoRosterSandboxPlayModeTests`. Do not hand-write a replacement summary. Its top-level `inputSnapshotSha256` is read by Unity from the `QDAO_ROSTER_INPUT_SNAPSHOT` environment variable and must match the exact full input snapshot. The observed `projectPath`, all eight actor identities, their loaded versions, frame inventories, independent texture/sprite counts, actual dedicated-idle use, and successful behavior assertions are checked. Lu must actually load V13 / 16 frames and the exact `activationSha256` from `Resources.Load<TextAsset>(...).bytes`; the other seven must actually load complete V12 / eight frames. Real-controller movement, all distinct animation resources, v3 alignment and contact 0, and the 480 ms cycle are required. Floating-point timing uses narrow tolerances.

The genuine V12 `baselineRuntimeObservation` and its `baselineInputSnapshot` are also required. They prove that V13 preserves the observed controller speed and cycle world distance, while frames per world unit double. A current V12 run may supply this baseline, but can never supply the final V13 observation or V13 input snapshot.

The isolated tested project's complete Assets / Packages / ProjectSettings file set and every SHA must still match its snapshot; shared writable links and symlink/junction ancestors are rejected. The publication target must match the tested **relevant** input set and hashes: character catalog/animator and Qdao editor code, ActorWorld, GameClient, real movement controller, sandbox bootstrap, BattleArtCatalog, relevant Qdao/Battle appearance tests, assembly definitions, Packages/ProjectSettings and existing roster assets. Both removed and newly added relevant files are checked. Unrelated target UI/social/map differences are recorded in the receipt, remain untouched, and are not represented as validated by this run.

Both Unity XML files must be genuine passing runs started after the input snapshot; the named V13 test cases must be present and passed. A manual version declaration, a historical V12 XML, or an approval for different art is insufficient.

## Final candidate approval

`approve.py` also defaults to a dry run. It requires a fresh reviewer-authored JSON describing the inspected images. This is internal visual acceptance, not a claim that the user has approved the art.

```powershell
python tools/approve.py --review-input review/fresh-visual-review.json
# Only after actual visual inspection of the complete candidate:
python tools/approve.py --review-input review/fresh-visual-review.json --execute
```

The review input contains:

- `status: "passed"`, `reviewed_input_manifest_sha256` and `reviewed_input_qc_sha256` for the exact pre-approval files inspected.
- `reviewed_artifacts`: the complete map of 145 delivery relative paths to their actual PNG SHA-256 values.
- `reviewed_directions`: all eight directions; `notes_by_direction`: a nonempty specific review note for each direction.
- `normal_size_review`, `enlarged_review`, `seam_15_16_01_review`, and `anatomical_contacts_01_09_review`: true only after those inspections.
- `evidence`: actual saved screenshot/contact-sheet records with `path` and `sha256`.

The tool first independently verifies all exports and source reconstruction. It then archives previous metadata, fixes `manifest.status`, `qc.status`, and `qc.visual_review` to `passed`, and writes `review/visual-review.json` bound to the **final** manifest/QC SHA. Finally it writes `validation.json`, which includes the visual-review SHA. Manifest does not reference validation, so there is no hash cycle. Any failure restores previous metadata bytes and retains failed metadata as evidence; PNGs are never changed. A later art/manifest/QC revision invalidates the earlier visual approval, and publication checks its SHA again after copying assets.

No approve, stage or publish operation has been executed against the current incomplete candidate.
