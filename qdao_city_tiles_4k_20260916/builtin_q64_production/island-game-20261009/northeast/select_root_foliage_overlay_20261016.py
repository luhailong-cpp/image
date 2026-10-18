from native_work import *
h=read(ZONE/'qa/local-seams16-foliage-20261016/handoff.json');q=h['recommendedOverlay'].copy();ident=q['id']
assert sha(q['source'])==q['sha256']
assert all(x['unchanged'] and sha(x['file'])==x['expectedSha256'] for x in h['sourceChecks'])
q.update(review='passed_local_overlay_perimeters_only',reviewedAtUtc=now(),reviewer='root independent100pct + local_seams16',inspection=h['reviewRecord'],scope=h['scope'],residualIssues=h['residualIssues'],formalAccepted=False,operation=h['operation'])
p=ZONE/'qa'/f'{ident}.overlay.json';assert not p.exists();write(p,q)
s=read(ZONE/'selection-r03_c09.json');assert ident not in s['overlays'];s['overlays'].append(ident)
s['pendingIssues']=[v if not v.startswith('r03_c09_p03_02:') else 'r03_c09_p03_02 internal x1024 foliage density line: central400x690 native improvement selected; upper/lower residuals outside crop remain pending.' for v in s['pendingIssues']]
s['updatedAtUtc']=now();write(ZONE/'selection-r03_c09.json',s);print(json.dumps({'overlay':ident,'crop':q['coreCrop'],'paste':q['tileLocalPaste'],'remainingPending':True}))

