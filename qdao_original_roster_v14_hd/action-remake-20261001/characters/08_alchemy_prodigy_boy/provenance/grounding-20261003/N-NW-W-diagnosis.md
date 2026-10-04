# N / NW / W actual pose review — 2026-10-03

Original comparison: 720 ms = 16 × 45 ms. Proposed arrays each total 800 ms. These are pose-based timing recommendations, not a substitute for fixing outward-pointing boots.

| Direction | Durations for frames 01–16 (ms) |
|---|---|
| N | 55,100,75,50,25,25,30,50,60,100,75,50,25,25,25,30 |
| NW | 55,85,75,55,30,30,35,50,60,85,75,55,25,25,25,35 |
| W | 50,100,90,50,25,25,25,30,55,100,90,50,25,25,25,35 |

N: 01–03 right support; 04 push; 05–07 flight; 08 contact; 09–11 left support; 12 push; 13–15 flight; 16 contact.
NW: 01–03 right support; 04 push; 05–06 flight; 07–09 left contact/loading; 10–11 left support; 12 push; 13–14 flight; 15–16 right contact.
W: 01 right heel approach; 02–03 right full support; 04 push; 05–08 left foot descent; 09 left heel contact; 10–11 left full support; 12 push; 13–16 right foot descent. W retained; no redraw.

## Minimal redraw outcome

Sources and per-image records are in N/selection.json and NW/selection.json. All three round2 sources are native 1254 RGBA; whole-canvas resize to1024, offset0, never940+42/50. Builtin tool actual model/quality undisclosed and recorded null. Runtime unchanged by this subagent.

- N04 v2: narrowed/straightened north-facing boot axes, small left recovery boot and correct right censer/left bottle preserved. Ground endpoint at alpha>=128 = 1105 native =902.3 on1024, preceding N03 =909. Residual ~7px, requires integration preview.
- N11 v2: original small right passing boot and exact arm phase preserved; v1 rejected because it copied N10. Straight left support boot endpoint1104 native =901.5 on1024; preceding N10 =916. **Residual14.5px remains unresolved. Do not claim fully grounded.**
- NW04 v2: raised heel and compact forefoot push align NW; toe endpoint1134 native =926 on1024, preceding NW03=920. Residual6px, requires integration preview.

The endpoint measurements are alpha silhouette evidence, not a full biomechanical ground-plane reconstruction. Two rounds per requested slot completed; no further generation beyond the agreed limit. Final acceptance must consider assembled normal-speed animation and the unresolved N11 support height.



## N11 follow-up actual evidence

Parent explicitly requested further correction. v3 locally extended the calf, sole1138 native=929.28 on1024 (13.28px below N10). v4 over-shortened and is rejected:1087=887.63. v5 is preferred candidate:1109=905.59, still10.41px above N10. All preserve straight N boot axis, correct hands/props and small right passing foot. No runtime edited. The local edit tool did not converge exactly to requested support height; the height residual remains explicitly unresolved, rather than silently accepted. Selection now points N11 to v5. All five rounds have prompt/job/refSHA and receipt records; actual model/quality remain null.
