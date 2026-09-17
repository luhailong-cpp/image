# Original Q roster V13: deterministic processing

No tool here draws new poses or interpolates old poses. Save each genuine built-in image_gen result and its exact prompt. The user selected GPT Image 2; processing records that requested model but does not invent backend-model confirmation.

## First direction

```powershell
python -B tools/pipeline.py import-walk --character CHARACTER_ID --direction S --source source/S-4x4.png --prompt source/S-prompt.txt --receipt source/S-tool-result.json
python -B tools/verify.py --character CHARACTER_ID --direction S
```

A walk source is one continuous direction in a native 4-row × 4-column grid, read row-major as 01–16. Do not pack four directions into this sheet. The first pose is anatomical RIGHT contact, frame09 LEFT contact, and16 returns smoothly to01; those are visual requirements, not something a script can establish.

Every complete source cell uses `512 / max(native_cell_width, native_cell_height)`, followed by the one character-wide `--common-scale` (default1). The processor never scales a subject bbox independently. Chroma removal uses the frozen generate2dsprite implementation; bounded despill preserves alpha, green and protected reds. Any original foreground touching a source-cell boundary is rejected. All16 outputs are committed only after all16 source cells pass.

Alignment is explicitly **v2** here: upper-body horizontal alpha-median256, lowest alpha>8 at471, integer translation only. This implements the requested common center/feet line. It does not claim to be Lu Dongbin's old fixed-idle-head-ROI v3. Final game metadata must describe the chosen real alignment; the renderer foot pivot stays(256,471).

The first imported direction immediately produces standalone512RGBA frames, the8192×512 strip, `review/S-contact.png`, pending manifest/QC, and browser inventory. Generation receipts are optional for early visual iteration but required for final visual-accepted verification; preserve the actual tool result, prompt, model evidence and source file instead of writing a fabricated response.

## Idle and portrait

```powershell
python -B tools/pipeline.py import-idle --character CHARACTER_ID --source source/idle-2x4.png --prompt source/idle-prompt.txt --receipt source/idle-tool-result.json
python -B tools/pipeline.py portrait --character CHARACTER_ID --source RESTORED_ORIGINAL_4096.png
```

Idle is2 rows ×4 columns in order N, NE, E, SE / S, SW, W, NW. All eight must be independent neutral standing drawings. Use the same character-wide scale as walk. Portrait is a whole-image LANCZOS downsample from the restored original4096×4096 to1024×1024; it is never cropped or redesigned.

## Review and verification

```powershell
python -B tools/pipeline.py review --character CHARACTER_ID
python -B tools/verify.py --character CHARACTER_ID
python -B tools/serve_preview.py --port 8874
```

Open `http://127.0.0.1:8874/`. It displays actual PNGs, normal480ms playback, slower playback, pause/step controls and normal/large display sizes. Missing images remain visibly missing.

A complete character has145 delivery PNGs:128 walk +8 idle +1 original portrait +8 strips. The verifier reconstructs every generated output from its original cell, chroma/edge steps, common scale and integer translation, checks all16 unique frames, idle independence, body-area CV≤.08, idle/walk height drift≤.08, cross-direction height ratio≤1.10, and strip cells pixel-for-pixel. It supports `--direction` for early first-direction checks without pretending the whole character is complete.

Numeric processing leaves `visual_review:pending`. Final `--require-visual` also needs generation receipts and a real `review/visual-review.json` with status passed, current `reviewed_manifest_sha256`/`reviewed_qc_sha256`, all eight `reviewed_directions`, the exact manifest `reviewed_artifacts` path→SHA map, and normal-size/enlarged/seam15-16-01/anatomical01-09 inspection flags. Do not write these flags before actually inspecting the art. These tools do not publish game appearance metadata.

A direction may alternatively use two genuine2×4 sheets: `--rows 2 --cols 4 --start-frame 1` for01–08 and `--start-frame 9` for09–16. Source records retain each separate original image, native cell and half-cycle position; the verifier rejects reused source cells. Partial imports produce a labeled partial contact sheet but no16-frame strip until all16 PNGs exist. After a character profile is established, omitting `--common-scale` reuses its recorded value; it never silently returns to1.0.
