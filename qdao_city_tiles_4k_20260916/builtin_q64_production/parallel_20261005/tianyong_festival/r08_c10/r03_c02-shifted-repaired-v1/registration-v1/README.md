# r03_c02 shifted repaired: mechanical registration study v1

Local bottom-context join accepted after native-pixel inspection and an independent visual review. No new generation, upscale, structure replacement or write into current.

- Output: `joined.png`, native1254x1254.
- Tile-local piece: `[909,2330,2163,3584]`.
- New coverage: `[909,2330,2163,2957]` (1254x627).
-128px transition into original: `[909,2957,2163,3085]`.
- Exact original preserved below tile y3085:625746 pixels. The whole1254 square can be inserted, or crop `[0,0,1254,755]` for the minimal insertion including transition.
- This does not complete the original r03_c02 extent; tile-local y1933..2330 remains outside this shifted piece. Side-neighbor seams and the eventual4096 tile remain unverified.

All six existing slab side edges match one-to-one. Horizontal displacement reaches23.99998px, vertical displacement is zero. The field crosses y627 continuously (maximum row change0.07123px), continues to the slab top, and fades inside the wide horizontal ivory band. It is not zeroed at the former transparent boundary. No missing structure is filled mechanically.

`flow.npy`, `tone.npy`, `blend-alpha.npy`, `contour-knots.npy`, `contour-shifts.npy`, `parameters.json` and `register.py` preserve the actual operation. Maximum tone change per channel is below8 (<12 allowed).42 original-pixel contour measurements have at most1px residual. `continuity-check.json` records actual edge/width samples. Native1254 dimensions are retained, all maps are bounded and have positive horizontal Jacobian; no global resize is applied.

Inspect `joined.png`, `qa-return-y627.png`, `qa-upper-y395.png` and `qa-original-above-aligned-below.png`. The three gray slabs, broad ivory crossbar and rounded top corners remain intact; no new wave, double edge or width step was observed. `visual-review.json` gives the exact limited acceptance scope.

Input native SHA256:87cb716a838c5b1a784f30785b1457107c5e25f30d45402d06e791994253d83c. All source/model/quality evidence remains inherited from that image; there was no new model call. Source generation time, actual model and actual quality are unconfirmed/null. This mechanical derivation has its own recorded time and parameter provenance.
