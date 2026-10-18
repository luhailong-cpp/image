from native_work import *
h=read(ZONE/'qa/local-seams16-20261016/handoff.json');o=h['recommendedOverlay'];ident=o['id'];src=Path(o['source']);assert sha(src)==o['sha256']
assert all(x['unchanged'] and sha(x['file'])==x['expectedSha256'] for x in h['sourceChecks'])
q={k:o[k] for k in ['id','source','sha256','nativeWorldBox','coreCrop','coreWorldBox','tileLocalPaste','size']}
q.update(review='passed_local_overlay_perimeters_only',reviewedAtUtc=now(),reviewer='root independent100pct + local_seams16',inspection=o['reviewRecord'],scope='400x840 local improvement only; full seam remains pending outside crop',formalAccepted=False,operation='exact original native crop paste; no resize, feather, blur or generated pixels from code')
p=ZONE/'qa'/f'{ident}.overlay.json';assert not p.exists();write(p,q)
s=read(ZONE/'selection-r03_c09.json');assert ident not in s['overlays'];s['overlays'].append(ident)
s['pendingIssues']=[v if not v.startswith('r03_c09_p02_02 right join') else 'r03_c09_p02_02 right join: local400x840 material and foliage repair selected; original upper25px/lower159px including sphere top still pending. Rejected v2 retained.' for v in s['pendingIssues']]
s['updatedAtUtc']=now();write(ZONE/'selection-r03_c09.json',s)
print(json.dumps(q))

