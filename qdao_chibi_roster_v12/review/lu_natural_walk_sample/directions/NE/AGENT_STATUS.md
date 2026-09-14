# Northeast authored walk candidate

Use walk-NE-canonical-raw.png (4 columns x 2 rows, 627 px per cell) and build_agent_ne_canonical.py. Exact selected single-frame paths and original hashes are in agent-sources.json and the raw assembly JSON.

Eight distinct poses are authored from built-in ImageGen. The two half-cycles now genuinely exchange legs: right/left contact, rear lift, low passing, and opposite forward reach; near right arm swaps back/forward at contacts. 04 and 08 shoe toes face NE. Short cloth robe, small gourd and sword positions are preserved.

A real head-width error in 04-06 was corrected through ImageGen. Final processed head width is 128-131 px (previously122-130). Original1254-canvas head top varies29-34 px only; original head widthP90 is382.1-390.1px. No individual bbox fit, no interpolated poses, no duplicated frames.

The agent-canonical-preview folder uses the existing v2 lowest-foot anchor only for diagnosis. Its head top65-92px exposes a frame-origin problem due to perspective walking-foot positions. Do not treat that preview as approved runtime output. Root is testing v3 whole-frame integer translation against stable upper-body/idle anchors with the same uniform scale. This agent has not changed any runtime code or formal character24 assets.

Numeric gates: 8 unique frames; no empty frames, source/output edge contact or clamping; body-scale CV1.154%. Root still owns v3 alignment and cross-direction/idle visual acceptance.
