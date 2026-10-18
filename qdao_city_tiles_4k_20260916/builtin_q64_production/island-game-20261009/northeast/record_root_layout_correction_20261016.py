from native_work import *
ident='r03_c09_p01_02_v3'
p=ZONE/'prompts'/f'{ident}.inputs.json';d=read(p);d=[d[0],d[1],d[2],{'file':(ZONE/'guides/r03c09-context-layout-only-20261016.png').as_posix(),'sha256':sha(ZONE/'guides/r03c09-context-layout-only-20261016.png'),'role':'enlarged original-layout context ONLY: identifies hanging red lantern, ivory garden wall and main hall column; not native pixels'},d[4]];write(p,d)
p=ZONE/'selection-r03_c09.json';s=read(p);s['pendingIssues']+=['2026-10-16 layout context audit: p01_02_v2 misidentified hanging lantern/tassel as timber column and roof; neighboring p01_01 and p02_01 must be rechecked/replaced against original terrace/wall geometry before expansion. Existing right half remains valid.'];s['internalReview']='partial_coverage_requires_structural_correction';write(p,s)
for ident in ['r03_c09_p01_01','r03_c09_p01_02_v2','r03_c09_p02_01']:
 p=ZONE/'native'/f'{ident}.png.generation.json';r=read(p);r.update(status='retained_candidate_requires_original_layout_correction',layoutReview='2026-10-16 enlarged original context confirms lantern/tassel was misidentified and propagated facade/terrace geometry; no whole-tile acceptance');write(p,r)
print('Recorded layout issue and exact 5 reference inputs for corrective version')

