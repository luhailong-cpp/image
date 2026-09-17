# V13 deterministic asset tools

These tools preserve V12 exports byte for byte. They do not create animation art.

1. `python tools/pipeline.py init` freezes the approved manifest and copies 64 walk frames to odd positions, plus eight idle frames and the portrait. It also makes endpoint and idle reference sheets in `references/<DIR>/<first-half|second-half>/`.
2. Save built-in image generation source and its exact prompt. Prepare a JSON batch description, then use `python tools/pipeline.py import --batch path/to/batch.json`. Every input is a complete source cell, normalized with one uniform cell transform, then chroma-keyed and translated by an integer offset to the unchanged V12 direction reference.
3. `python tools/pipeline.py assemble` writes review contact sheets, PNG strips, source manifests and numeric QC for all completed directions. Partial output is explicitly pending.
4. `python tools/verify.py` independently verifies all 145 delivery PNG files, SHA preservation, source crops and normalization, translation, head anchors, numerical gates and strip cells. A visual review file remains separately required before publication.
5. `python tools/pipeline.py preview` makes the synchronous 480 ms comparison page. `python tools/serve_preview.py` serves only this V13 directory at loopback port 8873.

Batch format:

```json
{
  "batch_id": "S-first-half-v1",
  "source": "E:/work/image/qdao_chibi_roster_v13/source/S-first-half-v1.png",
  "prompt": "E:/work/image/qdao_chibi_roster_v13/source/S-first-half-v1.txt",
  "generation": {"tool": "built-in image_gen", "model_verified": false, "model_evidence": "host-managed, backend model not disclosed"},
  "grid": {"rows": 2, "cols": 2},
  "despill_radius": 4,
  "cells": [
    {"direction": "S", "frame": 2, "row": 0, "col": 0, "selection_reason": "Visual judgment explaining this specific transition"},
    {"direction": "S", "frame": 4, "row": 0, "col": 1, "selection_reason": "..."},
    {"direction": "S", "frame": 6, "row": 1, "col": 0, "selection_reason": "..."},
    {"direction": "S", "frame": 8, "row": 1, "col": 1, "selection_reason": "..."}
  ]
}
```

Complete rectangular cells are retained. The normalization factor is `512 / max(native_cell_width, native_cell_height)` for the whole batch. It is never derived from a character bbox. `common_scale` stays 1.0. Replacement attempts remain in `source/` and `processing/batches/`; only the selected frame record is updated. Odd output positions cannot be imported.

Do not mark a review passed based only on these numeric tools. Pose anatomy, alternating support, costume and accessory consistency, 15→16→01 continuity and normal/zoomed playback require visual inspection. Do not publish appearance metadata until complete verification and runtime validation have passed.

Publication is deliberately separate: see [PUBLISH.md](PUBLISH.md) and `publish.py`. The default invocation is read-only; staged isolated tests and formal publication require explicit destinations and `--execute`. No publication has been performed.
