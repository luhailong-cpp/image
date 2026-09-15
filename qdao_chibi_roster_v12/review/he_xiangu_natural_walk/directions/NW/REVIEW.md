# He Xiangu natural walk NW: source handoff

Status: RAW SOURCE FROZEN FOR SHARED EXPORT; final whole-character and eight-direction visual acceptance remains pending with root. No process, seal, or publication was performed in this direction task.

## Visual source review

All eight poses have been visually checked against the new cloth-robe idle: low black bun, muted sage and ivory cloth robe, full-length pale trousers, ivory cloth shoes; no glow, fantasy effects, exposed legs, or petal skirt. Hair ornament stays on anatomical RIGHT; the small lotus stem stays behind anatomical LEFT belt. Hands remain empty.

NW is an independently drawn rear-left three-quarter view: LEFT is near, the lotus is on the near back-left belt, the right hair ornament is mostly hidden. It is not a side profile and is not a mirrored NE.

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

NW whole-cell head width remains within 0.8% of idle; head top is 20-21 px versus idle 21. Walk subject height is 565-581 px versus idle 585. The foot-bottom differences are retained from the genuine poses and must not drive per-frame scaling or stretched legs.

| Frame | Head top | Subject bottom | Height | Dark head width P90 |
|---|---:|---:|---:|---:|
| idle | 21 | 605 | 585 | 254.0 |
| 1 | 21 | 595 | 575 | 256.0 |
| 2 | 20 | 590 | 571 | 254.0 |
| 3 | 21 | 601 | 581 | 253.0 |
| 4 | 21 | 601 | 581 | 252.1 |
| 5 | 21 | 598 | 578 | 253.1 |
| 6 | 21 | 585 | 565 | 253.0 |
| 7 | 21 | 601 | 581 | 253.1 |
| 8 | 21 | 601 | 581 | 253.0 |

The head-width metric is a raster cross-check, not a substitute for anatomy or gait inspection. raw-nine-contact-review.jpg is the source contact sheet; no final transparent alignment or engine animation has been approved by this raw-source review.

## Frozen sheet SHA-256

- keys-final-raw.png: 3a371e3aa6530cb5d7997ae76338314afb023d44c8bcc2307d7b72cd8be2b33c
- inbetweens-final-raw.png: e85c68de2c5dbf4b32bf4787d24ae532ecb285cbad6613b9a10123d36a0eb2ad
