# He Xiangu natural walk NE: source handoff

Status: RAW SOURCE FROZEN FOR SHARED EXPORT; final whole-character and eight-direction visual acceptance remains pending with root. No process, seal, or publication was performed in this direction task.

## Visual source review

All eight poses have been visually checked against the new cloth-robe idle: low black bun, muted sage and ivory cloth robe, full-length pale trousers, ivory cloth shoes; no glow, fantasy effects, exposed legs, or petal skirt. Hair ornament stays on anatomical RIGHT; the small lotus stem stays behind anatomical LEFT belt. Hands remain empty.

NE is a rear-right three-quarter view: RIGHT is near, the right ear/hair ornament may be visible, the face has no visible eye. Lotus is on the far LEFT side. No mirrored NW artwork was used.

01/05 visibly exchange the leading hip/thigh/shin chain. 03/07 exchange support and the low passing foot. Selected 02/06 have low rear toe release and long shins; selected 04/08 keep the foot near ankle height without a high knee or front kick. Arm swing is opposite the advancing leg. Rejected sheets and rejected single corrections remain in this folder and are not selected.

## Canonical phases

- 01: RIGHT front contact; LEFT rear; RIGHT arm back / LEFT arm forward.
- 02: RIGHT support; LEFT rear toe leaves ground at low height; arms retain the preceding opposition.
- 03: RIGHT support; LEFT passes close to the support ankle; arms approach neutral.
- 04: RIGHT support; LEFT advances low and nearly flat toward its next contact; RIGHT arm forward / LEFT arm back.
- 05: LEFT front contact; RIGHT rear; RIGHT arm forward / LEFT arm back.
- 06: LEFT support; RIGHT rear toe leaves ground at low height; arms retain the preceding opposition.
- 07: LEFT support; RIGHT passes close to the support ankle; arms approach neutral.
- 08: LEFT support; RIGHT advances low and nearly flat toward its next contact; RIGHT arm back / LEFT arm forward.

## Exact source assembly

Run assemble_direction.py in this folder to reproduce the sheets. Keys are 2 x 2 row-major 01/03/05/07; in-betweens are 2 x 2 row-major 02/04/06/08. Each cell is exactly 627 x 627. Every selected native canvas is 1254 x 1254: a full single-pose canvas is uniformly scaled by 0.5, or a 2 x 2 native sheet cell is copied at scale 1.0. There is no subject bounding-box fit, anatomy resize, mirror, duplicate-pose substitution, synthesized pose, or generated interpolation. Assembly reconstructed all selected cells and asserted pixel equality; eight selected RGBA cells are distinct.

phase-selection.json gives the per-phase native file and grid index. cell-source-map.json and each final .assembly.json give the native resolution, exact crop box, uniform whole-cell scale, native SHA-256, selected-cell pixel SHA-256, generation record and output position. upstream-inventory-sha256.json records the upstream raw files, prompts, generation records, and idle reference.

## Scale and final-review limitation

NE whole-cell head width remains within 0.8% of idle, but the walk subject height is 535-562 px versus idle 579 px, with the original head top at 30 versus idle 32. The raw body/pose height difference is disclosed for root all-direction review. Do not independently fit bodies or lengthen legs; a shared scale and stable body anchoring must be evaluated after export.

| Frame | Head top | Subject bottom | Height | Dark head width P90 |
|---|---:|---:|---:|---:|
| idle | 32 | 610 | 579 | 257.0 |
| 1 | 30 | 572 | 543 | 256.0 |
| 2 | 30 | 564 | 535 | 255.0 |
| 3 | 30 | 581 | 552 | 256.2 |
| 4 | 30 | 581 | 552 | 256.0 |
| 5 | 30 | 591 | 562 | 256.0 |
| 6 | 30 | 585 | 556 | 256.1 |
| 7 | 30 | 582 | 553 | 257.0 |
| 8 | 30 | 582 | 553 | 256.0 |

The head-width metric is a raster cross-check, not a substitute for anatomy or gait inspection. raw-nine-contact-review.jpg is the source contact sheet; no final transparent alignment or engine animation has been approved by this raw-source review.

## Frozen sheet SHA-256

- keys-final-raw.png: 71abf1bf40c214de2b0c4947ffa3785ae7ce3314d1fccbfa452e4f0288f8c262
- inbetweens-final-raw.png: 89c68a36464b9ef2c0595e95061c33df7b8e36526fb04cea332df215b61f121f
