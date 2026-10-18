from workflow import *
q=ROOT/'qa'/'r08_c13-quick-batch02';m=read(q/'manifest.json')
for e in m['entries']:
 e.update(viewedAt=now(),status='quick_pass',note='Actual native core join is continuous; full-tile internal review still pending.')
 if e['id']=='21:31':e.update(status='not_passed',note='First targeted edit did not fix column shift and introduced a circle carving above mismatched flower. Retain v01 as better existing source; next repair will use assembled whole joint, not repeat this target.')
 if e['id'].startswith('43:') or e['id']=='42:43':e['note']+=' p43 internal top-of-bottom-guide foliage clipping/texture rectangle retained for whole-native repair, no internal acceptance yet.'
write(q/'manifest.json',m)
pf=ROOT/'progress-r08_c13.json';p=read(pf);p['workingVersions']['21']='v01';p.update(selectedCoordinateCount=12,generatedNativeCount=len(list((ROOT/'native').glob('r08_c13_p*.png'))),pendingRepair={'21-31':'Column shaft step; first edit v02 ineffective, v01 retained; next whole-joint repair after full assembly','43':'internal guide boundary clips foliage at native y1024, material edge x230/1024'},inFlight=False,updatedAt=now());write(pf,p)
print('Batch02 quick reviews recorded; 12 core coordinates saved, 21v01 retained.')
