from native_work import *
h=read(ZONE/'qa/local-seams16-p0401-corner-20261016/handoff.json');q=h['recommendedOverlay'].copy()
assert sha(q['source'])==q['sha256'];assert sha(q['baseSource']['file'])==q['baseSource']['sha256']
q.update(review='passed_internal_overlay_perimeters_only_external_bottom_pending',reviewedAtUtc=now(),reviewer='root independent100pct + local_seams16',inspection=h['inspectionRecord'],formalAccepted=False,operation=h['operation'])
p=ZONE/'qa'/f"{q['id']}.overlay.json";assert not p.exists();write(p,q)
s=read(ZONE/'selection-r03_c09.json');s['overlays'].append(q['id']);s['pendingIssues']=[v for v in s['pendingIssues'] if not v.startswith('r03_c09_p04_01_v2 upper')]
s.setdefault('resolvedIssues',[]).append('p04_01 top wall molding offset fixed byv2; original v1 lower-right239x389 crop restores foliage continuity without changing upper wall.')
s['updatedAtUtc']=now();write(ZONE/'selection-r03_c09.json',s)
print(json.dumps({'selectedOverlay':q['id'],'remainingIssues':s['pendingIssues']}))

