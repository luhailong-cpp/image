# Parent main-city repair candidates

Four scoped repair branches were merged into the child task's v014 candidate set. Only actual changed pixels were copied after source identity, at least128px context, overlap, and exact QA-pixel checks. Child selection remains unchanged.

The set retains11 complete pixel candidates and1 partial fragment. Five4096x4096 outputs below replace their snapshot entries; this adds no new coordinates. Formal city/client acceptance remains false.

| Tile | Current PNG | Provenance |
|---|---|---|
| r08_c07 | [r08_c07.png](r08_c07.png) | [record](r08_c07.png.generation.json) |
| r08_c08 | [r08_c08.png](r08_c08.png) | [record](r08_c08.png.generation.json) |
| r08_c09 | [r08_c09.png](r08_c09.png) | [record](r08_c09.png.generation.json) |
| r09_c08 | [r09_c08.png](r09_c08.png) | [record](r09_c08.png.generation.json) |
| r09_c09 | [r09_c09.png](r09_c09.png) | [record](r09_c09.png.generation.json) |

- [Complete parent candidate selection](current-selection.json)
- [Merge source identities and outputs](integration-state.json)
- [37 exact QA transfers](qa-transfer.json)
- [Decoded output verification](post-export-verification.json)
- [Actual final local visual review](final-visual-review.json)

Known limits: old upper gray tone transitions outside the west and corner-right masks remain. Full tile boundaries, other internal seams, unavailable neighbors, whole city, navigation and runtime are not accepted.

Branch source images have not been cleaned. [Cleanup proposal](../cleanup-proposal.json) is read-only planning; do not execute it until dependency retirement/preconditions are satisfied.
