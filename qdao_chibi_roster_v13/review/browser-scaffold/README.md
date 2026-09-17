# V13 preview scaffold-only browser QA

Status: **passed-scaffold-only**. 2026-09-17T07:29:26.852Z

This verifies preview controls and honest pending-art state. It is not V13 animation-art acceptance or game integration validation.

- 47 assertions passed; 0 failed.
- Expected assets: 64 original odd frames and 8 dedicated idle PNGs.
- All 64 new even transition poses remain absent; their HTTP404s must be visible as pending poses, never filled by old art.
- Browser: Microsoft Edge 153.0.4234.32 in headless mode.
- Service reused at 127.0.0.1:8873, PID24520, serving only V13 root.

See [report.json](report.json) for requests, phase checks, timing samples, screenshots, and errors.

- [desktop-S-missing-transition.png](desktop-S-missing-transition.png)
- [desktop-S-dedicated-idle.png](desktop-S-dedicated-idle.png)
- [mobile-390-all-directions.png](mobile-390-all-directions.png)
- [mobile-390-E-large.png](mobile-390-E-large.png)



Visual review: all four first-run screenshots were viewed. A small-screen pending-text issue was corrected by the asset pipeline and this run was repeated. The current 390px E screenshot was viewed after correction; all eight direction canvases measure at least 14 CSS pixels for pending text. The original character draw scale is unchanged. Initial evidence is retained in `attempt-01/`.
