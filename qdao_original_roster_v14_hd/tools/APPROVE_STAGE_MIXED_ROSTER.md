# Mixed visual approval and isolated staging

These new tools support only original 04–06 with mixed-preserved-v1. They do not
modify the V13 or all-HD tools, approve existing incomplete candidates, run Unity,
or publish to the formal client. The current authorization permits the built-in
image entry without claiming a confirmed model version. Existing source/model
records remain byte-identical. Saved generation metadata/file bindings are not
cryptographic model or generation attestations.

## Sequence and boundaries

1. Finish a new immutable mixed-candidates/run/id assembly using
   assemble_mixed_roster.py. All 137 PNGs must be present; all 136 actions must
   independently reconstruct; numeric QC and exact legacy-text reconciliation
   must pass. Partial output can never receive an activation.
2. Actually inspect that exact assembly. Save PNG evidence and a fresh visual
   review input with the bindings below. The tools validate review assertions,
   file integrity and coverage; they cannot perform or authenticate human visual
   judgment. They never generate a passing review.
3. Run approve_mixed_roster.py approve in dry-run mode, then use --execute to
   seal a **new offline** mixed-approved/run/id bundle. Source assembly and
   source records are not rewritten. The bundle contains a passed visual/numeric
   manifest, QC, validation, appearance, unchanged runtime PNGs, original review,
   copied evidence and pre-approval metadata. Validation explicitly states that
   actual mixed-asset Unity acceptance and formal publication are pending.
4. Run the independent approved-bundle check, then the isolated-stage dry run.
   Execute staging only when authorized and the isolated Unity editor is closed.
   The exact supported project is
   `D:/luyuan/wuxingqitan/tmp/qdao-original-live-candidate-20260921` by default;
   `QDAO_ISOLATED_PROJECT` may select an independent project under workspace/tmp.
5. After staging, the primary agent still must capture real mixed-asset normal
   and closeup gameplay, run fresh Unity Edit/Play checks with complete input
   snapshots, review the real result, and implement/use a separately reviewed
   formal publisher. **These tools cannot authorize or perform formal publication.**

The source assembly, original default generated files, original references and
legacy source trees must remain available for independent rechecks. Copying a
review bundle does not sever its source bindings. These are local reproducibility
records, not signed approvals. Changing either checker tool invalidates the saved
approval tool binding and requires a deliberate fresh approval.

## Visual review input

Use UTF-8 JSON. Required identity and status fields:

- schema: qdao-original-v14-mixed/visual-review-input-v1
- character_id: the exact original 04/05/06 ID
- status: passed, only after actual successful inspection
- reviewer: the actual reviewer, and reviewed_at_utc: UTC ISO timestamp after
  the assembly creation and no later than now
- reviewed_artifacts: exact object of all 137 relative PNG paths to current SHA256
- reviewed_directions: eight distinct N, NE, E, SE, S, SW, W, NW
- notes_by_direction: all eight keys, with concrete observations (at least
  twelve characters each)

Bind these five current files by SHA256:

| Input field | Source assembly file |
|---|---|
| reviewed_input_manifest_sha256 | manifest.json |
| reviewed_input_qc_sha256 | qc.json |
| reviewed_input_assembly_report_sha256 | assembly-report.json |
| reviewed_input_sources_sha256 | processing/mixed-sources.json |
| reviewed_preserved_snapshot_sha256 | processing/preserved-output-snapshot.json |

Set every following name_review to true only after that inspection:
normal_size, enlarged, seam_15_16_01, anatomical_contacts_01_09,
native_resolution, closeup_1080p, mixed_resolution_transition,
preserved_identity. For the final four names also supply concrete name_notes.
The seam review includes 16→01; the mixed transition review must assess the real
old/new frame boundary, proportional consistency and clarity without redrawing
or upscaling old artwork.

Evidence is a nonempty list of objects:

~~~json
{
  "path": "absolute-or-review-relative-path.png",
  "sha256": "actual-sha256",
  "checks": ["normal_size", "enlarged"],
  "directions": ["N", "NE"],
  "notes": "Concrete observations from this exact saved evidence."
}
~~~

Evidence files must be distinct readable PNGs. The first four check types must
each cover all eight directions across the evidence set. All four global check
types need evidence. A closeup_1080p image must be 1920×1080; a native_resolution
image must have both sides at least 1024. These dimensional checks do not prove
screenshot content: the reviewer must actually inspect the displayed current
frames. Pre-stage offline 1080p previews support offline visual approval; they
are **not** the later required real Unity gameplay captures. Preserve any
cropped-top camera observations rather than changing the camera.

## Commands

Run from this tools directory with the workspace Python environment:

~~~text
python -B approve_mixed_roster.py approve --assembly <mixed-candidates/run/id> --review-input <review.json> --output <mixed-approved/new-run/id>
python -B approve_mixed_roster.py approve --assembly <mixed-candidates/run/id> --review-input <review.json> --output <mixed-approved/new-run/id> --execute
python -B approve_mixed_roster.py check --directory <mixed-approved/run/id>
python -B stage_mixed_roster.py --approved <mixed-approved/run/id> --project E:/work/tmp/qdao-original-live-candidate-20260917 --audit <V14-root>/mixed-stage-audits/<new-name>.json
~~~

The final command is read-only unless --execute is supplied. An execute stage
always repeats the full approved/source/visual checks. It allows only the new
target Assets/Resources/World/Characters/QdaoOriginalRosterV14/id with exactly
137 PNGs plus manifest.json, validation.json, appearance.json. Existing target
directories or target .meta GUID files cause rejection. All existing character
resources are SHA-snapshotted and checked unchanged. No C#, maps, UI, camera,
index, .meta or old character file is written. Unity subsequently creates import
metadata and its derived resource index during a separate run. Original
family/source identity and per-frame mixed geometry are retained; same-identity
fallback behavior remains the existing client contract.

Stage first reserves a new audit file, copies into its own new temporary
directory, then renames that complete directory atomically. Approval appears
only in the complete isolated target. An existing held Unity lock is rejected;
an unlocked stale lock is not deleted. A failure before activation cleans only
the new temporary directory and records failed_before_activation. A failure
after rename retains the new target with an explicit
failed_after_target_activation audit/error for inspection; no automatic
rollback can delete existing resources. The audit path cannot be reused.

## Verification scope

python -B -m unittest test_approve_stage_mixed_roster -v uses only temporary
geometric PNG fixtures and a mocked lower-level reconstruction result. It checks
fresh SHA/coverage flags, missing slots, failed source checks, timestamp/evidence
rejection, immutable outputs, independently derived metadata, exact isolated
target protection, copy failure cleanup and audit recovery states. It never
approves real artwork or stages into a real project. Actual source reconstruction
and saved receipt/reconciliation rejection are covered separately by
test_assemble_mixed_roster.py.
