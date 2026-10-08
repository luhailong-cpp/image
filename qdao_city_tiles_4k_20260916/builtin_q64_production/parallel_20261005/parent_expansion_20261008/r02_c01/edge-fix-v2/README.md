# r02_c01 edge fix v2

Used one built-in image_gen call with the original joined patch and approved guild style reference. The final image is `joined.png` (1254 x 1254). `local-mask.png` limits the AI pixels to localized repaired returns; all x >= 1100 and every pixel outside the mask remain exactly unchanged. No image resampling, geometric registration, or color correction.

Five native QA crops and the whole patch were actually viewed. The hard tone cuts and two small lower contour breaks are repaired within the inspected scope. Parent must still verify the final assembly against external neighbors. This is a candidate patch, not formal acceptance of a 4K tile or city.

Generation records: `native.png.generation.json` records the built-in model/quality as undisclosed (null) and preserves the configured target, exact request, style input, receipt and observation window. `joined.png.generation.json` traces the derived asset and local mask; QA crops bind to joined pixels in `manifest.json`.
