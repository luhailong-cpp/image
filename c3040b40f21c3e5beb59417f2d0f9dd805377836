# Non-destructive mixed asset assembly

`assemble_mixed_roster.py` copies preserved Original 04–06 actions and portraits
into a **new** `mixed-candidates` run and fills only the missing frozen slots
with actual V14 HD outputs. No input image, metadata, old approval, formal
resource, or Original 00–03 file is written. Output directories cannot be
overwritten. An HD pilot for an already preserved slot is listed as excluded;
the old 512 PNG wins byte-for-byte.

The user subsequently authorized the current built-in image entry without
requiring confirmation of GPT Image 2.5. This tool therefore requires the saved
original raw, exact prompt and real built-in output receipt; it does not impose
a particular model version, fabricate a version, verify a C2PA signature or
call an API. A receipt's requested model string is not treated as model proof.
This updates this tool's workflow only; the earlier preparation snapshot and
its paused-model statement remain historical evidence and are not rewritten.

For **new** HD actions, an arbitrary nonempty receipt is insufficient. The
receipt must explicitly name the built-in tool, retain `actual_request.prompt`
matching the saved UTF-8 prompt without newline normalization, actual reference
image paths, a timestamp, one built-in call and zero paid API calls. Its actual
`output_hint` PNG path must equal `original_generated_file`; that original file
must still exist and have the exact saved raw SHA. Reference-file SHA bindings
and request/output bindings are saved and rechecked. The built-in entry does
not provide a signed receipt or an unforgeable API assertion: the result is
explicitly **saved metadata and file binding evidence**, not cryptographic
proof of generation or model identity. Historical receipts remain unchanged
and follow their separately preserved legacy contract.

```powershell
python -X utf8 -B tools/assemble_mixed_roster.py assemble `
  --character 04_mountain_guardian_boy `
  --preparation mixed-preparation/preserve-20260918-run1 `
  --hd-candidate candidate/04_mountain_guardian_boy `
  --output mixed-candidates/NEW_RUN/04_mountain_guardian_boy `
  --reconcile-legacy-text
```

This is a dry run. Add `--execute` to copy into the new output path. Run from
the V14 package directory or use absolute paths. Re-run verification with:

```powershell
python -X utf8 -B tools/assemble_mixed_roster.py check `
  --directory mixed-candidates/NEW_RUN/04_mountain_guardian_boy
```

`--require-complete` on either command rejects missing actions, unresolved
source conflicts or numeric QC failures. Even a complete source-ready assembly
remains `visual_review: pending`. The tool never writes `appearance.json`,
visual approval, a passed runtime validation or publication authorization.

Every `manifest.files` list contains exactly 137 slots. Missing slots have
`availability: missing`, null source/output hashes and required 1024 geometry;
no file is invented for them. Existing files retain their actual hash, size,
52/104 PPU, common pivot and root. Partial manifests are deliberately invalid
for runtime activation. Complete manifests can be input to a future dedicated
mixed visual approval workflow; old all-HD V14 approval/publish commands are
not a shortcut.

The assembler independently reproduces the recorded complete native cell,
alpha cleanup, chroma removal, whole-cell fixed scale, bounded despill and
integer root alignment, comparing all five saved stages and output pixels.
New HD cells must be at least 1024 in both dimensions and may not be upscaled.
Old 512 outputs retain their actual source dimensions and processing. Source
cell reuse is rejected; full directions receive resolution-normalized body
size, independent idle and duplicate-pixel checks. Visual gait, identity,
contacts, seams and near-camera detail still require actual human/model image
inspection and later real Unity captures.

Saved raw/prompt/receipt/stage evidence is copied without byte changes into
`evidence/`. `processing/mixed-sources.json` retains each complete original
source record alongside a separate record whose paths locate the copied
evidence. No model, generation or historic visual field is relabelled.
Original source-map bytes, the frozen preserved-output snapshot and inventory
are retained and bound by SHA. The check command reconstructs again from the
copied evidence and also verifies that the original legacy directory is still
unchanged.

Independent `check` derives every preserved slot from the actual fixed
`V13/candidate/<id>` source map and portrait record. It compares the copied
snapshot and source-map bytes to that real tree and requires every preserved
PNG, including the portrait, to remain present. Rehashing a copied snapshot,
marking an old frame missing, or pointing the report at another tree cannot
remove or replace a preserved frame. Both assembly and independent checking
enforce 05's 50/75 chroma profile through the shared reconstruction function.

Without `--reconcile-legacy-text`, historical prompt/receipt byte differences
remain explicit blockers even if output pixels reconstruct. The optional flag
uses the exact reviewed eleven-entry whitelist tool SHA
`f47f284bc9c4e36ac6f57d7ecca757f5c7f82e4458c9df16f17aa0eb6e218fc3`.
It verifies current bytes, historical hash, original path and frozen source-map
SHA and reproduces the historical newline bytes **only in memory**. That tool
is copied intact and re-executed on copied bytes by `check`; an unknown or
changed text is rejected. The original and copied text bytes and original
record hashes remain untouched. Exact reconciliation is source evidence, not
artwork approval.

`test_assemble_mixed_roster.py` uses temporary geometric PNG fixtures confined
to a temporary directory under `tools`. These files are cleaned and never
enter real candidates, Resources or generation evidence. Tests cover source
and stage tampering, missing/changed receipts, low native resolution, identity
and scale, preserved copies, 137-slot partial output, immutable destinations,
missing-frame completeness rejection and copied-text mutation.
Additional adversarial cases rehash modified manifests/reports after dropping
preserved images, changing copied source maps, deleting frozen rows or
redirecting the legacy root; these remain rejected. Native receipt fixtures
exercise request/reference/original-PNG binding validation while retaining an
explicit test-fixture label; their passage does not establish real generation.
