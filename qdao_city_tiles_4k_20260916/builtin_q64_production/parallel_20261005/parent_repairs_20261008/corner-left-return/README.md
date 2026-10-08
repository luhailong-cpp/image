# Corner left return repair branch

This independent branch repairs the diagonal paving-bevel break near context x627/y620..665 and the horizontal internal stitch near y329. Two disjoint local masks use the supplied native AI image at exact 1:1 coordinates, with smoothstep returns. No resizing, registration, displacement, tone adjustment, or additional AI call was used.

Both local targets and four return edges for each were actually inspected in ten original-scale QA crops and pass in that limited scope. Parent review is pending. Full tile/edge/city and runtime acceptance remain false.

The c07/c08 outputs use the original source hashes, not west-upper candidate files. Their changed bounding boxes are disjoint from west-upper. Merge only changed pixels against the same verified source; do not overwrite another branch or count these as new coordinates.

- [Bindings](bindings.json) / [Actual native visual review](review.json)
- [Horizontal target](qa/horizontal-center.png) / [north](qa/horizontal-north.png) / [south](qa/horizontal-south.png) / [west](qa/horizontal-west.png) / [east](qa/horizontal-east.png)
- [Diagonal target](qa/diagonal-center.png) / [north](qa/diagonal-north.png) / [south](qa/diagonal-south.png) / [west](qa/diagonal-west.png) / [east](qa/diagonal-east.png)
- [r08_c07 branch](coupled/r08_c07.png) / [generation chain](coupled/r08_c07.png.generation.json)
- [r08_c08 branch](coupled/r08_c08.png) / [generation chain](coupled/r08_c08.png.generation.json)
- [Native input](native.png) / [model/source record](native.png.generation.json) / [prompt](prompt.txt) / [builtin receipt](tool-response.json)

Actual builtin model/quality and server generation timestamp are undisclosed. Clock start/end readings are recorded only as tool-call observation/completion evidence.
