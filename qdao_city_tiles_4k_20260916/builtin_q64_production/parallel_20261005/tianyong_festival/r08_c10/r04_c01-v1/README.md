# r08_c10 / r04_c01 v1

One built-in image generation completed. Native1254x1254 original bytes are saved as `native.png`; SHA256168c4928c746355cb4c8474d80b3d3ecab24e4234808487a941fd33d911a3587.

Tile-local crop `[-115,2957,1139,4211]`; global crop `[36749,31629,38003,32883]`. Source context contains genuine native left115, right230 and bottom115 strips, including a verified bottom-left115 square from coupled-v2/r09_c09.537165 known pixels and1035351 newly painted missing pixels. The prepared checkpoint snapshot froze current/v004 at the actual preparation time; source details and exact crops are in `preparation.json`.

Both curved ivory bands and the broad diagonal cross-band are present. This is a candidate awaiting local repair, not an accepted join. Bottom gray/ivory right contour is40..42px left of original. Smaller left-bottom offset and stronger gray mottling also need repair; right middle face has a warm/cool mismatch. Direct hard return visibly steps. No registration, tone correction, blend or current write was performed.

Native evidence: `native.png.generation.json`, `prompt.txt`, `request.json`, `tool-response.json`, `preparation.json`, `comparison.json`, `face-diagnostics.json`, `visual-review.json`. Source bytes and all input hashes were reverified. Inspect `qa-hard-context-return.png` and side/bottom native QA crops.

Generation used the host-managed built-in image_gen path with the approved04-guild style image actually viewed and attached. Batch target is gpt-image-2.5-sunburst/max. Submitted model/quality/size selectors and actual returned model/quality are null because the host tool exposes none. generatedAt is null; observedCompletionAt is2026-10-05 18:45:50 UTC. Actual output hint and host path are preserved. No API route or additional generation was used.

All new files stay in this piece directory. No current/progress/source-checkpoint or cross-directory image was modified; no artwork was deleted. This candidate contributes zero accepted new pixels and zero complete4096 tiles until reviewed repair is completed.

Additional measured material gate: right middle face crop[1024,480,1040,560] raw-minus-original meanRGB is[-56.57,-45.60,-23.64]. This exceeds a12/channel tone-only allowance; mechanical geometry correction alone cannot make this candidate acceptable.
