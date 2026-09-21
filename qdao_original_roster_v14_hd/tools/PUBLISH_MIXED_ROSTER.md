# First mixed Original04 publication

> Historical first04 implementation notes. For the current04–06 sequential
> publisher, local paths, native-walk hard gate and prior-index protection, use
> [current publication instructions](PUBLISH_MIXED_ROSTER_CURRENT.md).

`publish_mixed_roster.py` is a separate, read-only-by-default publisher. It
supports the first formal publication of `04_mountain_guardian_boy` into the
fixed formal project `E:/work/mmorpg-client`, from the sole isolated project
`E:/work/tmp/qdao-original-live-candidate-20260917`. It does not change the older
all-HD publisher or old verification records. Extension to 05/06 needs a later
workflow for already-published V14 GUID/index differences; this tool deliberately
does not claim that support.

## Separate protection for formal and isolated import metadata

The first-04 publisher now supports the actual existing difference between the
two projects' old V13 metadata: 637 `.meta` files have independent GUIDs and/or
Unity importer serialization. It never copies, normalizes or rewrites them.

- Formal old characters must match **every file, byte size and SHA** in the
  retained `V13/runtime-validation/mixed-resolution-client-run1/formal-safety-baseline.json`.
  Its SHA is pinned to
  `8238ab4d32a2c4782f2b853339257cd3054b5e9b8c9c796351d78b42b823377f`.
  The fixed path, formal project identity, schema, capture scope, prior-review
  binding, 46 historical source-path declarations and exact 3451 character-file
  scope are checked. Replacing it with a fresh baseline cannot bless an old
  resource change. Historical source bytes in that record precede the accepted
  source sync; current source code still uses the separate 50-file equality gate.
- Isolated old characters, including **every old `.meta`**, must match the exact
  `protected_before` inventory in this approved stage's audit. Only the newly
  staged target and its newly created directory metas are excluded. A family
  meta already present before staging stays protected.
- Across projects, old author-supplied resource paths and SHA must agree exactly;
  only `.meta` is omitted from this cross-project comparison. An author file
  change, missing file, extra file, or either project's changed old meta is still
  rejected by its own complete protection comparison. This is not a general
  permission to ignore metadata differences.

No additional baseline-writing step or command-line option is needed. Every
preflight already takes a fresh full formal `Assets` / `Packages` /
`ProjectSettings` inventory, and execute repeats it before and after copying.
The historical character baseline prevents unnoticed old-resource drift; the
fresh in-memory inventory protects the entire formal project during this exact
publication. The audit records both legacy-inventory digests, the pinned formal
baseline SHA, file counts and the number of independent metadata differences.

05/06 remain unsupported. Their sequential release also needs a verified chain
of prior V14 publication/import evidence, each project's derived index checks,
and runtime acceptance of all previously published mixed actors. Simply ignoring
GUID differences or adding IDs would not establish those conditions.

Prerequisites:

1. A complete immutable mixed assembly and an actually visually reviewed,
   independently checked `mixed-approved/<run>/04_mountain_guardian_boy` bundle.
   The publisher reruns `approve_mixed_roster.verify_approved`, including original
   source reconstruction, legacy preservation, receipt/evidence bindings, numeric
   QC and the exact visual review. It never creates a passing review.
2. The existing `stage_mixed_roster.py` execute audit, still bound to that approval
   and the unchanged old character tree. Only its exact 137 PNG + 3 JSON may
   appear in the isolated runtime target, together with legal Unity metas and
   the root derived index. Finish import/index generation and close the isolated
   editor before taking the first real test input snapshot.
3. A **new actual** run under
   `E:/work/image/qdao_original_roster_v13/runtime-validation/<run>/` containing
   `input-editmode.json`, `input-playmode.json`, `post-playmode.json`,
   `editmode.xml`, `playmode.xml`, the corresponding `-launch.json`,
   `-completion.json`, `.log`, and
   `city-captures/runtime-observed-appearances.json` plus actual PNG captures.
   Use the existing `capture_unity_inputs.py` / `run_unity_tests.ps1` tools.
   Edit input precedes Edit launch, Play input follows Edit completion, and the
   post input follows both completions. All complete file/SHA/size inventories
   must be identical and match the current isolated input tree. Full filters,
   exit zero, distinct passed XML cases, all existing HD methods and all 22
   mixed cases are required. The existing old `review_mixed_client_run.py`
   requires mixed=0 and is not the review command for this new artwork run.
4. The real report must observe five originals: unchanged V13 00–03 and mixed04.
   The 136 actual mixed action paths, individual 512/52 or 1024/104 geometries,
   pivot/world size, distinct direction frames, dedicated idle, resource hashes,
   bounded residency and real motor route must match. Formal/current isolated
   character C#/meta/camera inputs must match all 50 bound source files. The
   historical actual V12 baseline still binds speed/cadence/controller behavior.
5. Actually inspect the current normal and nearest gameplay captures and save a
   review under this new run. See schema below. All observed normal PNGs are
   checked for regression; both 04 captures require an exact visual review.

The current gameplay captures show the **preserved 512 idle** after movement.
The publisher verifies and records that actual geometry. These screenshots do
not demonstrate a new 1024 walk frame at nearest zoom; native walking detail,
mixed transitions and loop seams remain bound to the complete offline visual
approval. The real runtime separately inventories all 136 loaded action frames.
Nearest camera top clipping must be recorded honestly; this tool never adjusts
camera behavior. The formal Editor is not launched by publication.

## Runtime review JSON

Use actual hashes and actual inspection notes; this schema is not a ready-made
approval. Top-level fields:

- `schema`: `qdao-original-v14-mixed/runtime-visual-review-v1`
- `status`: `passed`, `reviewer`: actual reviewer name, `reviewed_utc`: actual UTC
  timestamp after runtime observation and no later than the present
- `runtime_report_sha256`, `input_snapshot_sha256` (Play input),
  `approval_receipt_sha256` (approved `approval.json`), `stage_audit_sha256`
- `mixed_geometry_reviewed: true`,
  `preserved_idle_capture_acknowledged: true`, and concrete
  `mixed_geometry_notes` of at least 12 characters
- `views`: exactly two records, one each for `normalView` and `nearestView`, with
  `character_id: "04_mountain_guardian_boy"`, `view`, `status: "passed"`,
  `image_sha256`, `clipping_reviewed: true`, the actual boolean
  `full_frame_inside_capture`, and concrete `notes` of at least 12 characters

Saved reviews and tool receipts are local reviewer assertions plus checked file
bindings, not signed or independently authenticated attestations. Tests cannot
establish real visual quality or actual Unity execution.

## Command

Run from the V14 root with the workspace bundled Python (or equivalent Python
with Pillow). Substitute the actual immutable run names:

```powershell
python -X utf8 -B tools/publish_mixed_roster.py `
  --approved mixed-approved/APPROVED_RUN/04_mountain_guardian_boy `
  --project E:/work/mmorpg-client `
  --run E:/work/image/qdao_original_roster_v13/runtime-validation/ACTUAL_RUN `
  --stage-audit mixed-stage-audits/STAGE_RUN.json `
  --runtime-visual-review E:/work/image/qdao_original_roster_v13/runtime-validation/ACTUAL_RUN/runtime-visual-review.json `
  --audit mixed-publication-audits/NEW_PUBLICATION_RUN.json
```

Without `--execute`, this makes **zero writes**, including no audit file. With
`--execute`, the entire preflight is repeated and compared immediately before
any writes. It reserves a new audit, copies only the 140 authored files into a
new temporary directory inside the formal family, verifies all formal Assets,
Packages and ProjectSettings file inventories unchanged, and atomically renames
the complete directory to the new same-ID target. An existing target or target
GUID blocks publication. Neither metas nor the isolated index are copied; the
formal Editor must derive its own on the next authorized import. Held Unity
locks are rejected; unlocked stale locks are preserved.

Failure before activation cleans only the newly created temporary directory and
retains its audit. Failure after activation retains the target and records
`failed_after_target_activation`; it never deletes already promoted resources.
Success is `published_pending_formal_editor_import`, not a claim that formal
Unity has already imported or run the new resources.

## Unit tests

From `tools`: `python -X utf8 -B -m unittest test_publish_mixed_roster -v`.
Fixtures are explicitly synthetic and temporary. The full-workflow fixture mocks
only the heavy source/visual-approved verifier; it exercises the real publication
checks and copying against temporary miniature Unity-shaped directories.
Reconstruction/approval tests remain in `test_assemble_mixed_roster` and
`test_approve_stage_mixed_roster`; shared launch/PNG/HD gates remain covered by
`test_publish_original_roster_v14_gates`. No fixture reaches real candidates,
actual Resources, approvals or saved runtime evidence.

Focused metadata protection regression tests:

```powershell
python -X utf8 -B -m unittest test_publish_mixed_baselines -v
```

These use small dictionaries and two temporary JSON records per case, without
PNG fixtures or real project scans. They cover independent GUID/importer bytes,
formal and isolated author/meta tampering, size changes, missing/extra files,
cross-project author mismatch, pinned-baseline SHA and identity/scope failures,
timestamp/duplicate/traversal rejection and preservation of preexisting family
metadata. Passing them verifies the gate logic, not actual Unity or publication.
