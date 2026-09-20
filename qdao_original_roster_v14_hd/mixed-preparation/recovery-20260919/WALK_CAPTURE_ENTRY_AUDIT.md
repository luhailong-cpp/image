# Actual native walk capture entry audit — 2026-09-19

Scope: source inspection and test-only implementation. Work stopped on the user's request to write a handoff and continue another time. **Final state is in `WALK_CAPTURE_FINAL_HANDOFF.md` and `WALK_CAPTURE_HANDOFF_STATE.json`.** No Unity process, asset import, screenshot, gameplay run, formal source sync, or publication was performed for this audit. Existing idle screenshots cannot prove a 1024 walking closeup.

## Current entry and defect

The sole isolated project is `E:/work/tmp/qdao-original-live-candidate-20260917`. No AGENTS.md exists on its `Assets/Tests/PlayMode` ancestor chain. `E:/work/image/AGENTS.md` governs these accompanying image-project reports/tools. Existing project locks and metadata must be retained.

`Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs` already builds the real offline Tianyong sandbox and drives its actual `TianyongPlayerController`/`CharacterController`. Its only screenshot call occurs immediately after changing appearance, before `WalkWithRealMotor`. Later movement observations are collected after settling. Thus current `normalView` and `nearestView` describe the preserved independent 512 idle, despite the report correctly inventorying 136 mixed action resources.

`QdaoRosterAnimatorPlayModeTests.EveryCharacter_WalksItsDeclaredFramesInAllEightDirections_AndSettlesOnItsIdlePose` currently compares every frame against `Appearance.FrameWidth == 1024` and every V14 sprite against PPU 104. Mixed appearance deliberately uses 1024 only as a reference maximum. Preserved 512/52 frames will fail this test when real mixed04 is available. Its assertions need the resource-specific `appearance.GeometryForResource(resourcePath)`; uniqueness, all 16 poses, 30 ms cadence, idle identity and bounded directional residency should remain unchanged.

The production `TianyongSandboxAutoDrive` has `-sandboxDrive`, `-shotDir`, `-driveNoQuit`, `-driveTimeout`; it offers no character/direction/frame selector and no roster input snapshot binding. It is not a substitute for the existing acceptance runner.

## Proposed test-only implementation

1. Correct per-resource dimensions, pivot and PPU assertions in the existing all-character PlayMode test.
2. Extend the existing sandbox test with two deterministic target resources for mixed04: `walk/SW/02.png` and `walk/NW/02.png`. Their resource indices are 1 (the files are one-based); sprite names may encode zero-based indices and must not be used alone as proof.
3. For each target, find a clear short route in the corresponding camera-relative direction, warp only before the measured interval, and use `SetDebugDirection` with the actual motor. Wait for actual `Run`, positive recorded motor travel, correct direction, and renderer texture identity matching `Resources.Load<Texture2D>(appearance.FrameResourcePath(direction, 1))`. Do not set sprite/animation phase manually or substitute idle.
4. Capture the same actual sprite synchronously at configured default 27 and minimum 5, without advancing simulation between the two captures. Use the existing 1920×1080 PNG/render/projection logic. Preserve game camera rotation, focus semantics, player geometry and map config. Restore requested zoom, render target and active texture in `finally`. Report real crop bounds; nearest top clipping is allowed only as an honestly observed fact requiring visual review.
5. Attach an additive walk-capture evidence list rather than overwrite the idle observations/movement baseline. Record direction, one-based frame, exact resource path and PNG SHA, actual loaded dimensions/PPU/pivot/world size, renderer identity, `Run`, measured motor distance and time, exact simulation frame, input snapshot SHA, paired image SHAs and camera projections. A failed/missing target is an assertion failure, never a fallback to idle or a fabricated passing record.

The main agent received this narrow plan before any source edit. Implementation then continued within the originally delegated test-only scope. The two isolated test sources were changed and compiled offline; their formal copies were not changed. The final handoff supersedes this document's initial planning language.

## Baseline source identity

Before modification, the two test files matched formal and isolated byte-for-byte; the formal copies and retained backups still have these hashes:

- Sandbox: `5fc0845e54c7ab53da97ad2582ffcf6c052e69f97f3ff0f87b49b3fe5b4f27d0`
- Animator: `509df5647a9e3324bfe6400dedf4c2e2278059119b340d2314721d86ea549d17`

Unchanged formal/isolated production inputs:

- `TianyongMapConfig.asset`: `963442447ad2c81ad8878960e2d411b7290b765036b538dd8db52d5e82c5a7c6`
- `TianyongCameraController.cs`: `d0c887165433cb8db5da889cdb0b1920f2f0a512b02a604b1f20ee17f92deb1d`
- `TianyongPlayerController.cs`: `5aad4fafebe8f38640e613f63075b3c6b0ebf88a95267a95c65e4ef9c925cba4`
- `QdaoBoySpriteAnimator.cs`: `b938771ebd81c2a90e250d75cd6209126c0eea5f2eeb58577ff680783aa948e9`

Both test sources already belong to the publisher's 50 current source/config/meta bindings. An isolated test-only edit intentionally makes those two formal copies differ until a separately reviewed, explicit source sync; a new Unity run cannot reuse an old snapshot or old XML. Existing character assets/metas and the historical formal character baseline do not need modification.

## Fresh run commands and inputs

These commands are instructions for the main agent's later authorized real run, not evidence of execution. First complete/approve/stage mixed04, import/index it in the sole isolated project, and close the editor. Use a unique new run; never overwrite existing XML/log/PNG evidence. The runner defaults to an obsolete different project, so `-Project` must be explicit.

```powershell
$walkPython = 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe'
$walkV13 = 'E:/work/image/qdao_original_roster_v13'
$walkProject = 'E:/work/tmp/qdao-original-live-candidate-20260917'
$walkRun = 'mixed04-real-walk-NEW_UNIQUE_RUN'
$walkEvidence = "$walkV13/runtime-validation/$walkRun"

& $walkPython -X utf8 -B "$walkV13/tools/capture_unity_inputs.py" --project $walkProject --output "$walkEvidence/input-editmode.json"
& "$walkV13/tools/run_unity_tests.ps1" -Platform EditMode -Project $walkProject -Run $walkRun -InputSnapshot "$walkEvidence/input-editmode.json"
& $walkPython -X utf8 -B "$walkV13/tools/capture_unity_inputs.py" --project $walkProject --output "$walkEvidence/input-playmode.json" --compare "$walkEvidence/input-editmode.json"
& "$walkV13/tools/run_unity_tests.ps1" -Platform PlayMode -Project $walkProject -Run $walkRun -InputSnapshot "$walkEvidence/input-playmode.json"
& $walkPython -X utf8 -B "$walkV13/tools/capture_unity_inputs.py" --project $walkProject --output "$walkEvidence/post-playmode.json" --compare "$walkEvidence/input-playmode.json"
```

Runner binds `QDAO_ROSTER_CAPTURE_DIR`, `QDAO_ROSTER_INPUT_SNAPSHOT`, input SHA, absolute project, filters, command arguments, launch/finish times and exit code. It uses a graphics device (`-force-d3d11`, no `-nographics`) and full existing Edit/Play filters. Snapshot covers all `Assets`, `Packages`, `ProjectSettings`, and `Library/PackageCache`, rejects links and live changes, and must show zero added/removed/changed files across the three snapshots. A mere successful snapshot command does not assert comparison is empty: its JSON must be checked. Publisher independently requires exact equality and current isolated inventory.

Existing publisher accepts exactly two reviewed idle images. New walking PNGs alone do not tighten publication. A separate strict walk-capture validator and actual visual review should bind all four walk views to the fresh input, report, approved manifest/resource SHA and frame-specific geometry before asserting actual native walking closeup acceptance. Prior `review_mixed_client_run.py` requires mixed=0 and must not be used for this real mixed04 run.

## Verification available without launching Unity

Unity's saved response file exists at `Library/Bee/artifacts/1900b0aE.dag/MmorpgClient.Tests.PlayMode.rsp`. A copied response file with all output/ref-output/debug-output paths redirected to this recovery directory can invoke the bundled `Editor/Data/DotNetSdk/dotnet.exe` and SDK 8.0.318 `Roslyn/bincore/csc.dll`. Running the compiler is not running Unity; it can check the test source against existing Unity/reference assemblies without changing Library. Its result is compilation evidence only. Real motor routing, captures, runtime assertions and visual quality still require the new actual graphics-enabled Unity run.

Process listing through CIM was denied in this audit's sandbox; no claim about current Unity liveness is made from that failed query. No process was started or stopped.
