from native_work import *
ident='r03_c09_p03_02'
s=read(ZONE/'selection-r03_c09.json');s['cores'][2][1]=ident;s['updatedAtUtc']=now()
s.setdefault('pendingIssues',[]).append('r03_c09_p03_02: upper join passes; right actual core join coherent but internal original anchor boundary x1024 has a straight darker density edge. Needs local material transition repair after core coverage.')
write(ZONE/'selection-r03_c09.json',s)
for stem,status,obs in [('r03_c09_p02_02__r03_c09_p03_02','passed_internal_only','Ivory coping and foliage contours continuous at upper join.'),('r03_c09_p03_02__r03_c09_p03_03','pending_internal_anchor_transition','Actual core join geometry continuous; visible darker vertical density edge within left side at sourcex1024. Not fully passed.')]:
 p=ZONE/'qa'/f'{stem}.json';d=read(p);d.update(status=status,reviewedAtUtc=now(),reviewer='root',observed=obs);write(p,d)
p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='selected_native_candidate_material_transition_pending',internalSeams='upper pass; right actual core contours align but internal anchor density line pending');write(p,d)
print(json.dumps({'selected':ident,'pendingMaterial':True}))

