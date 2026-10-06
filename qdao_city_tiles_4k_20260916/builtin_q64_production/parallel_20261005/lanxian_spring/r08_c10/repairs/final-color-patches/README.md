# Final two color-patch repairs

The white pillar-base and lower-left leaf rectangular tone cutoffs were verified at native size and repaired with one built-in image edit. The final core preserves the source outside two small same-coordinate polygon masks.

- Final core: [repair-core4096.png](repair-core4096.png), 4096 × 4096 RGB; [generation/source chain](repair-core4096.png.generation.json).
- Composite support: [alpha4096.png](alpha4096.png), 4096 × 4096 L; [record](alpha4096.png.generation.json).
- Current repair design: [final-crop1254.png](final-crop1254.png), native 1254 × 1254; [record](final-crop1254.png.generation.json).
- Native before/after/mask visual evidence: [qa-native.png](qa-native.png); [record](qa-native.png.generation.json).
- [Actual prompt](prompt.txt), [tool receipt](tool-receipt.json), [AI generation record](generated-1254.png.generation.json), [unchanged source hashes](source.json), [processing and QA](processing.json), [processing procedure](process.py), and [intermediate cleanup](cleanup.json).

The repaired core is already feather-composited. For a disjoint-mask overlay onto another repaired core, copy its pixels wherever alpha is nonzero; do not apply fractional alpha a second time.

Source crop: [1900,1290,3154,2544). Crop-local masks: pillar [1030,729,1194,879); leaf [131,1139,231,1230). Feather is five native pixels inward only. No resize, translation, registration, global grading, or image blur. Outside-mask changed pixels: 0. All four return boundaries match the source over 16-pixel strips.

Actual built-in model and quality are undisclosed and recorded as null. The saved target configuration remains the batch configuration; official release/model pages were rechecked on 2026-10-06. The config target is not evidence of explicit submitted parameters or actual returned model.

The pillar's pre-existing 3–4 pixel step in its dark lower contour at crop x≈1172 remains visible in the source, generated output, and final repair. This edit removed the rectangular tone patch while keeping the existing geometry under the task's geometry lock.

The original selected core and central source remain untouched. Intermediate PNGs in this assigned repair folder were removed after the final outputs and references were verified; their hashes and provenance remain in the text records. The host-generated original is outside this delegated write directory and was not removed here.
