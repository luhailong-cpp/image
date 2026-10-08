# West upper local repair package

Parent-owned candidate only. Active child selections and original source files are unchanged.

The AI-native patch removes the dark blue triangle between r08_c07/r08_c08. Exact native coordinates were used without resizing or registration. Only context rectangle [570,472,822,820] contributes changes, with a 40-pixel smoothstep alpha return around [610,512,782,780].

Actual native-scale review confirms the triangle improvement and continuous right/bottom returns. The old upper cream-strip x627 tone step and old slab y544 horizontal tone step remain visible outside/at the return. This package is pending parent review; the entire shared edge is not accepted.

- [Bound output identity and operation](binding.json)
- [Actual native visual review](review.json)
- [Original vs exported result, 1:1](qa/before-after-1to1.png)
- [Whole local context, 1:1](qa/whole-local-context-1to1.png)
- [Left return](qa/return-left-1to1.png) / [right return](qa/return-right-1to1.png) / [top return](qa/return-top-1to1.png) / [bottom return](qa/return-bottom-1to1.png) / [center](qa/center-1to1.png)
- [r08_c07 candidate](coupled/r08_c07.png) / [record](coupled/r08_c07.png.generation.json)
- [r08_c08 candidate](coupled/r08_c08.png) / [record](coupled/r08_c08.png.generation.json)
- [Native generated input](native.png) / [generation record](native.png.generation.json)
- [Exact prompt](prompt.txt) / [builtin tool receipt](tool-response.json)

Model and quality are unconfirmed for the actual built-in result. Configuration target and actual submitted/returned metadata are recorded separately. No new AI call was made during this mechanical integration.
