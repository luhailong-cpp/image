# Walk capture handoff — stopped 2026-09-19

The user requested remaining work be written into handoff documents and continued later. No further implementation, Unity launch, import, formal synchronization or publication should be inferred from this handoff.

## Exact final state

Two **isolated** test files changed under `E:/work/tmp/qdao-original-live-candidate-20260917/Assets/Tests/PlayMode/`:

| File | Current isolated SHA-256 |
| --- | --- |
| `QdaoRosterAnimatorPlayModeTests.cs` | `a561d1bdebf095a6adf2c8d0d91d6464eb812ae7cb9dc9494daf09342a70dbc7` |
| `QdaoRosterSandboxPlayModeTests.cs` | `69656d276d1230fbbd231ef750de137cf588908ca47bb275c187b8a04058c912` |

The animator test now checks each frame's `GeometryForResource` rather than assuming every V14 frame is 1024/104. It retains all-frame uniqueness, cadence, direction, independent-idle and residency checks. This corrects a real mixed-asset test failure that the prior mock-only mixed run did not expose.

The existing sandbox test gained a conditional mixed04 capture helper: after the normal real-motor contract walk, it prepares clear real city routes, then drives the actual controller until the actual renderer shows SW02 and NW02 in `Run`, with positive measured travel and exact loaded-resource identity. It writes two additional observations in `walkFrameCaptures`, each with normal configured 27 and nearest configured 5 screenshots, both taken synchronously during the same simulation frame. It records resource SHA, 1024/104 geometry, pivot/world size, route/time/motor/state and input snapshot SHA. It does not assign sprite/animation phase, change the production camera/controller/animator, or replace the old idle observations. Camera zoom/target are restored in `finally`; existing camera clipping remains visible in recorded projected bounds.

**These route/capture helpers have compiled but have never run in Unity.** A future real run may reveal route availability, rendering, coroutine timing, camera crop or assertion issues. Do not claim that real SW02/NW02 gameplay PNGs exist or are accepted.

Formal test copies under `E:/work/mmorpg-client` are untouched and still match backups:

| File | Formal + backup SHA-256 |
| --- | --- |
| `QdaoRosterAnimatorPlayModeTests.cs` | `509df5647a9e3324bfe6400dedf4c2e2278059119b340d2314721d86ea549d17` |
| `QdaoRosterSandboxPlayModeTests.cs` | `5fc0845e54c7ab53da97ad2582ffcf6c052e69f97f3ff0f87b49b3fe5b4f27d0` |

Backups are in this directory's `walk-capture-before/`. No automatic rollback or formal copy has been performed. The publisher's 50-file source binding will correctly reject a formal/isolated mismatch until a future explicit reviewed source synchronization. Old snapshots/XML cannot validate these new sources.

Map config, camera controller, movement controller and sprite animator production SHA values remain identical in both projects and identical to the pre-change audit. Exact values, paths and all evidence hashes are saved in `WALK_CAPTURE_HANDOFF_STATE.json`.

## Independent validator already saved before the stop request

The following two files were completed just before the stop message arrived; no further validator work was added afterward:

- `E:/work/image/qdao_original_roster_v14_hd/tools/verify_mixed_walk_captures.py` — SHA `40fe9f09cd39a0438d3004e59622900fe1d65f7b9c80c980e49ff8eb6ed8b2d5`
- `E:/work/image/qdao_original_roster_v14_hd/tools/test_verify_mixed_walk_captures.py` — SHA `484abd0cac7dedb45723b7914f870559fd1bcb695e7be15cc19d53710a5ce2e0`

The read-only verifier requires the sole isolated project and exact new run/report/Play input/launch/results, all 50 current source bindings, tested manifest, native source SHA/geometry, exact SW02/NW02 targets, real motor Run assertions and measured movement. It reuses the existing PNG decoder/SHA/1920×1080/projection/zoom/clipping gate for all four views. Its output status is deliberately `bound_evidence_requires_visual_review`; it cannot approve artwork or publish anything.

It is **not wired into the publisher**, whose existing review schema still checks two idle screenshots. Completing the future actual four-view check and visual review remains necessary before claiming native walking closeup validation. The independent verifier has not been run against a real new capture report because none exists. Full project integrity, approval and publication gates remain separate.

Future read-only invocation, only after the real run exists:

```powershell
& 'C:/Users/luyua/AppData/Local/Programs/Python/Python312/python.exe' -X utf8 -B `
  'E:/work/image/qdao_original_roster_v14_hd/tools/verify_mixed_walk_captures.py' `
  --run 'E:/work/image/qdao_original_roster_v13/runtime-validation/ACTUAL_NEW_RUN'
```

## Completed local verification

- Offline C# compilation: Unity's bundled SDK 8.0.318 Roslyn compiler returned **exit 0**, using a copied existing PlayMode response file with `out`/`refout` redirected to `walk-capture-compile/`. Unity itself was never started. That directory contains the exact `.rsp`, DLL/ref DLL and portable PDB. Do not copy those outputs into any Unity project.
- New small binding tests: **10/10 passed**, 0.008 s. They cover exact targets, missing/duplicate evidence, idle substitution, wrong SHA/input, preserved/native identity, 512/PPU/pivot/world-scale errors, stationary/warp substitution, simulation/time binding and delegation of PNG gate failures. Their PNG checker is mocked; they are not screenshot or Unity tests.
- Existing shared PNG/projection checks: **4/4 passed**, 3.329 s, testing real temporary PNG SHA/decode dimensions, truthful nearest clipping/zoom and finite projection/configuration values. These are synthetic files, not gameplay captures.

Commands used were `python -X utf8 -B -m unittest test_verify_mixed_walk_captures -v`, plus the four existing `test_publish_original_roster_v14_gates.PublicationGateTests` cases named in the tool transcript. No large publication suite was rerun.

## Next session sequence

1. Read this handoff and the parent roster handoff; respect the user's stop until work is explicitly resumed. Recheck files against `WALK_CAPTURE_HANDOFF_STATE.json` before editing.
2. Finish real mixed04 art and its offline source/visual approval. New NW04/06/07 purple edge concerns were sent to the guardian agent; do not assume they were resolved by this audit. Old SW01/SW13 themselves have purple artifacts and remain under the original preservation constraint.
3. Review the two test-only changes, then use the sole isolated project for the future authorized import and graphics-enabled full test run. Preserve fresh launch/XML/log/input snapshots. Exact run commands and binding requirements are in `WALK_CAPTURE_ENTRY_AUDIT.md`.
4. Verify actual four walking PNGs with the independent tool, inspect all four visually, and record true observed clipping/detail. The prior idle capture review and offline asset review do not substitute for this new result.
5. Resolve formal/isolated test-source synchronization as an explicit later source change, then rerun the complete publication preflight against fresh evidence. No 05/06 publication support was added; the existing first-04 boundary remains.

## Process closeout

The owned offline compiler session 19752 returned exit 0. Both owned Python test commands returned exit 0. The earlier owned preview QA server had already been stopped and its temporary fixture removed. There is no live owned exec session or background helper to resume/terminate. No Unity, publication or formal-sync process was started here. Other agents' image tasks and unrelated background processes were not touched.

Related earlier completed audit deliverables remain `PIPELINE_RECOVERY_AUDIT.md`, `PUBLISHER_META_FIX.md` / `publisher-meta-fix-tests.json` (16 small metadata protection tests passed), `preview-browser-qa.json`, and the independent `tools/MIXED_PREVIEW.md` preview instructions. Their scopes and caveats remain as recorded; none claim finished art or real new Unity runtime acceptance.
