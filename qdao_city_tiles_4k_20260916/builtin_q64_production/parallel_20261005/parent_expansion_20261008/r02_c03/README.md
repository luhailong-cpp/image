# r02_c03 native gap patch

Current local result: [joined.png](joined.png), with its exact [RGBA insertion patch](newfilled-patch.png). [manifest.json](manifest.json) binds all source hashes, tile-local coordinates, opacity masks and [review.json](review.json).

This fills813,056 previously transparent native pixels against the bound v014 source. The window is[1933,909,3187,2163] in r08_c10. The left overlap must be reconciled with the neighboring parent patch before a full tile is accepted; overlapping coverage must not be counted twice. No new complete4K tile is claimed here.

Use RGBA alpha-composite at the specified window. It reproduces joined.png exactly over the original context; do not replace the full1254 square indiscriminately. Existing top/bottom/right returns use at most32px of opacity transition. One pre-existing white trim step uses a separately bounded18px transition. No image scaling, blur or geometric registration was applied.

Two AI calls contributed: the original native gap fill and one narrow gold-face surface correction that removed two artificial transverse bars. Both used the built-in tool; submitted model/quality and actual returned model/quality were undisclosed and remain null. The configuration target and complete evidence are in [native.png.generation.json](native.png.generation.json) and [surface repair provenance](surface-repair/native.png.generation.json). Their prompts and references are retained. Every derived output has its own generation record.

Twelve native crops and the final joined image were visually inspected. Acceptance is limited to these local returns and surface repairs; the adjacent left parent patch, whole4K tile, wholecity and runtime remain unaccepted. No child directory or selection was changed.
