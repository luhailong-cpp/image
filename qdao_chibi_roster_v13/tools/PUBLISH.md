# V13 explicit staging and publication

`publish.py` is prepared but has not staged or published anything. It cannot pass while the 64 generated transition frames are missing. Every invocation requires an explicit Unity project under `E:/work`; there is no default destination. Without `--execute`, it only validates and reports a plan.

Before either mode:

1. Finish the 145 PNG delivery set, complete the visual review, and run `python tools/verify.py --require-visual`.
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
  "runtimeObservation": {"path": "runtime-observation.json", "sha256": "ACTUAL_HASH"},
  "tests": [
    {"kind": "EditMode", "path": "editmode.xml", "sha256": "ACTUAL_HASH", "requiredV13TestNames": ["ACTUAL_FULL_TEST_NAME_CONTAINING_V13"]},
    {"kind": "PlayMode", "path": "playmode.xml", "sha256": "ACTUAL_HASH", "requiredV13TestNames": ["ACTUAL_FULL_TEST_NAME_CONTAINING_V13"]}
  ]
}
```

`input-snapshot.json` uses the root task's existing snapshot schema: `source`, `project`, `created_utc`, `files: [{path, sha256, bytes}]`, `count`. Capture it **after staging** and **before both test runs**. Its inventory must contain all 145 exact `Assets/Resources/World/Characters/QdaoRosterV13/24_lu_dongbin/...` PNGs plus the precise `appearance.json` SHA from the staging receipt. The saved tested project's files are checked again. The current run1 snapshot, which contains only V12 resources, cannot satisfy this gate.

`runtime-observation.json` must be recorded from the actual game's loaded appearance and movement checks. It includes `characterId`, `version:13`, `frameCount:16`, `frameDurationMs:30`, `dedicatedIdle:true`, `alignmentVersion:3`, `contactFrame:0`, `candidateRevision`, `inputSnapshotSha256`, `appearanceSha256`, `resourceRoot:"World/Characters/QdaoRosterV13/24_lu_dongbin"`, `observedFramesPerDirection` with all eight directions equal to 16, `movementCycleMs:480`, `movementSpeedUnchanged:true`, and `otherSevenUseCompleteV12:true`.

Both Unity XML files must be genuine passing runs started after the input snapshot; the named V13 test cases must be present and passed. A manual version declaration, a historical V12 XML, or an approval for different art is insufficient.
