# HD contract preparation Run 2

Unity EditMode passed 348/348 (19 HD contract cases), zero failed/skipped; process exited 0. XML time: 2026-09-18 08:13:25–08:16:15 UTC.

The complete saved input contains 25,967 files. The seven copied source hashes still match both the saved input and tested isolated source. Three new Unity-generated code meta files were synchronized to formal source to keep script GUIDs stable.

Scope: metadata geometry, complete inventory, each missing HD image, same-ID V13 fallback, stale/duplicate/dimension-invalid index and legacy EditMode regressions. The isolated project contains existing 512 Original 00–03, no HD candidate, and old Animator/Battle code. This is not HD visual acceptance or HD gameplay/cache validation. No PlayMode test was run here.

Run 1 compiler failure remains preserved. Formal source continues with additional camera telemetry, an old-actor/new-revision race fix, and parent-owned bounded animation/battle caches; those require a new combined run.

A temporary image-directory visibility interruption was observed after testing. The exact saved input SHA and XML were rechecked after the same files reappeared; this did not mutate isolated inputs or change the test conclusion.
